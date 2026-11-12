"""C1: how fast can this Mac train small language models? (plan v2, Track C)

Plain words: build GPT-style models of four sizes, train each one for a fixed
time on random tokens, and count how many tokens a second it gets through.
Random tokens are fine here: speed doesn't depend on what the text says.

Engineering terms: decoder-only Transformer (pre-LayerNorm, learned positions,
tied input/output embedding, GELU MLP, no biases in Linear layers), AdamW,
compiled train step (`mx.compile`), synchronised with `mx.eval` every step.
Throughput is reported per 10-second window so thermal throttling is visible.

Usage:
    uv run --no-project --python 3.14 --with mlx==0.31.2 \
        python experiments/C1-throughput/bench_throughput.py measure --out results/run1.jsonl
    python experiments/C1-throughput/bench_throughput.py summarise results/run1.jsonl

Only `measure` needs MLX. Everything else is plain Python so it can be checked anywhere.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import statistics
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

VOCAB = 32768  # a typical tokenizer size; EXP-M1 will vary it
CONTEXT = 1024  # tokens per sequence
BATCH = 16  # sequences per step, so 16,384 tokens per step
CHINCHILLA_TOKENS_PER_PARAM = 20
WINDOW_SECONDS = 10.0
SECONDS_PER_DAY = 86_400


@dataclass(frozen=True)
class Size:
    name: str
    d_model: int
    layers: int

    @property
    def heads(self) -> int:
        return self.d_model // 64


SIZES = (
    Size("10M", 256, 4),
    Size("25M", 384, 6),
    Size("50M", 512, 10),
    Size("125M", 768, 14),
)
DTYPES = ("float32", "bfloat16")


def param_count(size: Size, vocab: int = VOCAB, context: int = CONTEXT) -> int:
    """Exact number of trainable numbers in the model below.

    Embedding (tied with the output layer) + positions + per block
    (attention 4·d², MLP 8·d², two LayerNorms 2·2·d) + the final LayerNorm (2·d)."""
    d = size.d_model
    per_block = 12 * d * d + 4 * d
    return vocab * d + context * d + size.layers * per_block + 2 * d


def train_flops_per_token(size: Size, vocab: int = VOCAB, context: int = CONTEXT) -> int:
    """Forward + backward cost of one token, by the usual 6·N rule plus attention.

    N counts the weights a token passes through (blocks and the output layer, not the
    position table); attention adds 6·L·T·d for the score and value products
    (the causal half of 12·L·T·d)."""
    d = size.d_model
    matmul_params = size.layers * 12 * d * d + vocab * d
    return 6 * matmul_params + 6 * size.layers * context * d


def chinchilla_days(params: int, tokens_per_second: float) -> float:
    """Days of non-stop training to see 20 tokens per parameter."""
    return CHINCHILLA_TOKENS_PER_PARAM * params / tokens_per_second / SECONDS_PER_DAY


def environment() -> dict[str, str]:
    def run(*cmd: str) -> str:
        try:
            return subprocess.run(cmd, capture_output=True, text=True, check=False).stdout.strip()
        except OSError:
            return "unknown"

    power = run("pmset", "-g", "batt").splitlines()
    return {
        "chip": run("sysctl", "-n", "machdep.cpu.brand_string"),
        "memory_bytes": run("sysctl", "-n", "hw.memsize"),
        "macos": platform.mac_ver()[0],
        "python": platform.python_version(),
        "power": power[0] if power else "unknown",
    }


def measure(sizes: tuple[Size, ...], dtypes: tuple[str, ...], seconds: float, out: Path) -> None:
    import mlx.core as mx
    import mlx.nn as nn
    import mlx.optimizers as optim
    from mlx.utils import tree_flatten

    class Attention(nn.Module):
        def __init__(self, d: int, heads: int) -> None:
            super().__init__()
            self.heads = heads
            self.qkv = nn.Linear(d, 3 * d, bias=False)
            self.out = nn.Linear(d, d, bias=False)

        def __call__(self, x: mx.array) -> mx.array:
            b, t, d = x.shape
            q, k, v = mx.split(self.qkv(x), 3, axis=-1)
            q, k, v = (a.reshape(b, t, self.heads, -1).transpose(0, 2, 1, 3) for a in (q, k, v))
            o = mx.fast.scaled_dot_product_attention(
                q, k, v, scale=1.0 / math.sqrt(d // self.heads), mask="causal"
            )
            return self.out(o.transpose(0, 2, 1, 3).reshape(b, t, d))

    class Block(nn.Module):
        def __init__(self, d: int, heads: int) -> None:
            super().__init__()
            self.ln1 = nn.LayerNorm(d)
            self.attn = Attention(d, heads)
            self.ln2 = nn.LayerNorm(d)
            self.up = nn.Linear(d, 4 * d, bias=False)
            self.down = nn.Linear(4 * d, d, bias=False)

        def __call__(self, x: mx.array) -> mx.array:
            x = x + self.attn(self.ln1(x))
            return x + self.down(nn.gelu(self.up(self.ln2(x))))

    class GPT(nn.Module):
        def __init__(self, size: Size) -> None:
            super().__init__()
            self.wte = nn.Embedding(VOCAB, size.d_model)
            self.wpe = nn.Embedding(CONTEXT, size.d_model)
            self.blocks = [Block(size.d_model, size.heads) for _ in range(size.layers)]
            self.ln_f = nn.LayerNorm(size.d_model)

        def __call__(self, idx: mx.array) -> mx.array:
            x = self.wte(idx) + self.wpe(mx.arange(idx.shape[1]))
            for block in self.blocks:
                x = block(x)
            return self.wte.as_linear(self.ln_f(x))

    env = environment() | {"mlx": mx.__version__}
    out.parent.mkdir(parents=True, exist_ok=True)

    def run_one(size: Size, dtype: str) -> dict:
        mx.random.seed(0)
        model = GPT(size)
        model.set_dtype(getattr(mx, dtype))
        actual = sum(v.size for _, v in tree_flatten(model.parameters()))
        if actual != param_count(size):
            raise SystemExit(f"{size.name}: model has {actual} numbers, formula says {param_count(size)}")
        optimizer = optim.AdamW(learning_rate=3e-4, weight_decay=0.1)

        def loss_fn(m: GPT, x: mx.array, y: mx.array) -> mx.array:
            return nn.losses.cross_entropy(m(x), y, reduction="mean")

        loss_and_grad = nn.value_and_grad(model, loss_fn)
        state = [model.state, optimizer.state]

        def train_step(x: mx.array, y: mx.array) -> mx.array:
            loss, grads = loss_and_grad(model, x, y)
            optimizer.update(model, grads)
            return loss

        step = mx.compile(train_step, inputs=state, outputs=state)

        def batch() -> tuple[mx.array, mx.array]:
            tokens = mx.random.randint(0, VOCAB, (BATCH, CONTEXT + 1))
            return tokens[:, :-1], tokens[:, 1:]

        for _ in range(3):  # compile and warm up; not timed
            loss = step(*batch())
            mx.eval(loss, state)
        mx.reset_peak_memory()

        windows: list[float] = []
        steps = 0
        start = window_start = time.perf_counter()
        window_tokens = 0
        while True:
            x, y = batch()
            mx.eval(x, y)
            loss = step(x, y)
            mx.eval(loss, state)
            steps += 1
            window_tokens += BATCH * CONTEXT
            now = time.perf_counter()
            if now - window_start >= WINDOW_SECONDS:
                windows.append(window_tokens / (now - window_start))
                window_start, window_tokens = now, 0
            if now - start >= seconds:
                break
        record = {
            "size": asdict(size),
            "params": actual,
            "dtype": dtype,
            "batch": BATCH,
            "context": CONTEXT,
            "vocab": VOCAB,
            "steps": steps,
            "seconds": round(time.perf_counter() - start, 2),
            "window_tokens_per_second": [round(w, 1) for w in windows],
            "final_loss": round(float(loss.item()), 4),
            "peak_memory_bytes": mx.get_peak_memory(),
            "environment": env,
        }
        return record

    for size in sizes:
        for dtype in dtypes:
            record = run_one(size, dtype)
            with out.open("a") as f:
                f.write(json.dumps(record) + "\n")
            median = statistics.median(record["window_tokens_per_second"])
            print(f"{size.name} {dtype}: median {median:,.0f} tok/s", flush=True)
            mx.clear_cache()


def summarise(records: list[dict]) -> str:
    """The results table, from the raw records. Median over 10-second windows."""
    lines = [
        "| Size | Parameters | Number format | Tokens/s (median) | Slowest window | Effective TFLOP/s "
        "| Peak memory (GB) | Final loss | Days to 20 tokens/parameter |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in records:
        size = Size(**r["size"])
        windows = r["window_tokens_per_second"]
        median = statistics.median(windows)
        tflops = train_flops_per_token(size, r["vocab"], r["context"]) * median / 1e12
        lines.append(
            f"| {size.name} | {r['params'] / 1e6:.1f}M | {r['dtype']} | {median:,.0f} | {min(windows):,.0f} "
            f"| {tflops:.2f} | {r['peak_memory_bytes'] / 1e9:.1f} | {r['final_loss']:.2f} "
            f"| {chinchilla_days(r['params'], median):.2f} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    m = sub.add_parser("measure")
    m.add_argument("--out", type=Path, required=True)
    m.add_argument("--seconds", type=float, default=120.0)
    m.add_argument("--sizes", nargs="*", default=[s.name for s in SIZES])
    m.add_argument("--dtypes", nargs="*", default=list(DTYPES))
    s = sub.add_parser("summarise")
    s.add_argument("results", type=Path)
    args = parser.parse_args(argv)
    if args.command == "measure":
        chosen = tuple(size for size in SIZES if size.name in args.sizes)
        measure(chosen, tuple(args.dtypes), args.seconds, args.out)
    else:
        records = [json.loads(line) for line in args.results.read_text().splitlines() if line]
        sys.stdout.write(summarise(records))


if __name__ == "__main__":
    main()
