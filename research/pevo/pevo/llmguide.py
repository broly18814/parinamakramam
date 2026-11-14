"""EXP-007: showing a hidden piece of code to a language model, and reading its guesses back
(docs/research/EXP-007-build-spec.md, S1, S2 and S6).

Plain picture: cover one piece of a real function with a sticker (`__HOLE__`), show the model
the function as it was really written, and ask what's under the sticker. To check a guess, put
it where the sticker was, tidy the function exactly as EXP-005 tidies code (numbered variable
names, placeholder strings), and compare the piece with the real one.

For specialists: the prompt is the original source with the task node's exact span replaced,
because `normalise` deep-copies, so normalised nodes keep their original positions. A guess
is substituted back, the function is re-parsed and normalised, and the node at the same
structural path (field, index) from the function's root is compared with `shape()`. Positions
in `ast` are UTF-8 byte columns, and are converted.

Nothing here runs any code from the project or from the model.
"""
from __future__ import annotations

import ast
import random
import re
from dataclasses import dataclass

from pevo.codeblocks import MIN_SIZE, normalise, shape, size
from pevo.grammarsearch import Task, base_templates, kind_of, positions

HOLE_NAME = "__HOLE__"
INSTRUCTION = ("Write only the Python code that replaces __HOLE__: a single expression, or a single "
               "statement if __HOLE__ stands alone on its line. No explanation.")
_FENCE = re.compile(r"^\s*```[a-zA-Z0-9_+-]*\s*\n(.*?)(?:\n\s*```.*)?$", re.S)


# ---------------------------------------------------------------- where a node is

def path_to(root: ast.AST, target: ast.AST) -> tuple | None:
    """The structural path (field, index or None) from `root` to `target`, by identity."""
    if root is target:
        return ()
    for name, value in ast.iter_fields(root):
        items = list(enumerate(value)) if isinstance(value, list) else [(None, value)]
        for i, v in items:
            if isinstance(v, ast.AST):
                p = path_to(v, target)
                if p is not None:
                    return ((name, i), *p)
    return None


def node_at(root: ast.AST, path: tuple) -> ast.AST | None:
    node = root
    for name, i in path:
        v = getattr(node, name, None)
        if i is not None:
            if not isinstance(v, list) or i >= len(v):
                return None
            v = v[i]
        if not isinstance(v, ast.AST):
            return None
        node = v
    return node


# ---------------------------------------------------------------- the prompt (S1)

def _offset(lines: list[str], lineno: int, col_bytes: int) -> int:
    """Character offset in the joined text of (1-based line, UTF-8 byte column)."""
    before = sum(len(x) for x in lines[: lineno - 1])
    return before + len(lines[lineno - 1].encode("utf-8")[:col_bytes].decode("utf-8", errors="ignore"))


@dataclass(frozen=True)
class Hole:
    """One task, ready to show: the function text with the piece covered, and how to check guesses."""

    text: str            # the function as written, with the piece replaced by __HOLE__
    truth: str           # the original source of the hidden piece
    fn_name: str
    indented: bool       # the function is nested (method or inner function)
    is_stmt: bool
    is_slice: bool       # a slice (`a:b`) can only be read inside a subscript
    col: int             # the hole's column in characters (a statement's indentation)
    path: tuple          # from the function's root to the piece
    target: tuple        # shape() of the hidden piece


def make_hole(source: str, fn: ast.AST, node: ast.AST) -> Hole:
    """`fn` is a normalised function from EXP-005's `functions(source)`; `node` is inside it."""
    lines = source.splitlines(keepends=True)
    start_line = min([fn.lineno] + [d.lineno for d in getattr(fn, "decorator_list", [])])
    seg_a = _offset(lines, start_line, 0)
    seg_b = sum(len(x) for x in lines[: fn.end_lineno])
    a = _offset(lines, node.lineno, node.col_offset)
    b = _offset(lines, node.end_lineno, node.end_col_offset)
    path = path_to(fn, node)
    if path is None:
        raise ValueError("node is not inside fn")
    col = a - _offset(lines, node.lineno, 0)
    return Hole(text=source[seg_a:a] + HOLE_NAME + source[b:seg_b], truth=source[a:b], fn_name=fn.name,
                indented=fn.col_offset > 0, is_stmt=isinstance(node, ast.stmt),
                is_slice=isinstance(node, ast.Slice), col=col, path=path,
                target=shape(node))


def prompt(hole: Hole, library_lines: list[str] | None = None) -> str:
    """The user message: the instruction, the library if any (S1), and the function."""
    parts = [INSTRUCTION]
    if library_lines:
        parts.append("Helpers you may use (HOLE marks a part you fill in):\n" + "\n".join(library_lines))
    parts.append("```python\n" + hole.text.rstrip("\n") + "\n```")
    return "\n\n".join(parts)


# ---------------------------------------------------------------- reading a guess back (S2)

def clean_guess(text: str, is_stmt: bool, is_slice: bool = False) -> str | None:
    """Strip a code fence; keep the first expression, or the first statement."""
    m = _FENCE.match(text)
    if m:
        text = m.group(1)
    bare = text.strip()
    if len(bare) > 2 and bare[0] == bare[-1] == "`" and not bare.startswith("``"):
        text = bare[1:-1]                     # inline code: `x + 1` (S2, second refinement)
    text = text.strip("\n")
    if not text.strip():
        return None
    lines = text.splitlines()
    if not is_stmt:
        # The longest run of leading lines that reads as one expression *in brackets*, which is
        # where it goes back (S2): a bracketed expression may span lines, and adjacent strings on
        # separate lines join. A slice (`a:b`) exists only inside a subscript, so it's read there.
        for n in range(len(lines), 0, -1):
            chunk = "\n".join(lines[:n]).strip()
            try:
                ast.parse(f"_[{chunk}]" if is_slice else f"({chunk})", mode="eval")
            except SyntaxError:
                continue
            return chunk
        return None
    indent = min((len(ln) - len(ln.lstrip()) for ln in lines if ln.strip()), default=0)
    body = "\n".join(ln[indent:] for ln in lines)
    try:
        tree = ast.parse(body)
    except SyntaxError:
        return None
    if not tree.body:
        return None
    return ast.get_source_segment(body, tree.body[0])


def _parse_function(text: str, indented: bool, name: str) -> ast.AST | None:
    src = ("if True:\n" + text) if indented else text
    try:
        mod = ast.parse(src)
    except SyntaxError:
        return None
    top = mod.body[0].body if indented else mod.body
    for st in top:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and st.name == name:
            return st
    return None


def piece_shape(hole: Hole, guess: str) -> tuple | None:
    """The shape of the piece a guess puts in the hole, or None if it can't be read (S2)."""
    node = piece_node(hole, guess)
    return None if node is None else shape(node)


def piece_node(hole: Hole, guess: str) -> ast.AST | None:
    """The normalised node a guess puts in the hole (its rules are what G3 counts, S3), or None."""
    g = clean_guess(guess, hole.is_stmt, hole.is_slice)
    if g is None:
        return None
    if hole.is_stmt:
        g = g.replace("\n", "\n" + " " * hole.col)
        tries = [g]
    else:
        tries = ["(" + g + ")", g]          # brackets keep precedence; `*x` needs none
    for filled in tries:
        fn = _parse_function(hole.text.replace(HOLE_NAME, filled, 1), hole.indented, hole.fn_name)
        if fn is None:
            continue
        piece = node_at(normalise(fn), hole.path)
        if piece is not None and isinstance(piece, ast.stmt) == hole.is_stmt:
            return piece
    return None


# ---------------------------------------------------------------- tasks with their nodes

def sample_tasks_with_nodes(future: dict, inventory: set | dict, max_size: int = 12, per_function: int = 8,
                            seed: int = 0) -> list[tuple[Task, ast.AST, ast.AST]]:
    """grammarsearch.sample_tasks, step for step (same draws, same tasks), also returning each
    task's function and node, which the prompt needs. A self-check confirms they're identical."""
    rng = random.Random(seed)
    out = []
    for path, qual in sorted(future):
        tree = future[(path, qual)]
        pos = positions(tree)
        eligible = [n for n in ast.walk(tree)
                    if n is not tree and isinstance(n, (ast.stmt, ast.expr)) and MIN_SIZE <= size(n) <= max_size]
        for n in rng.sample(eligible, min(per_function, len(eligible))):
            ctx, c2 = pos[id(n)]
            t = Task(path, qual, size(n), ctx, c2, kind_of(type(n).__name__), shape(n),
                     all(x in inventory for x in base_templates(n)))
            out.append((t, tree, n))
    return out


# ---------------------------------------------------------------- the model-alone controls (S6)

def direct_scores(target: tuple, pieces: list[tuple | None], mean_logprobs: list[float]) -> tuple[bool, bool]:
    """(any-of-k solved, top-1 solved). Top-1 is the guess with the highest mean log-probability
    per token; ties go to the earlier one. Unreadable guesses (None) never match."""
    any_k = any(p == target for p in pieces)
    if not pieces:
        return False, False
    best = max(range(len(pieces)), key=lambda i: (mean_logprobs[i], -i))
    return any_k, pieces[best] == target


# ---------------------------------------------------------------- names for the library (S4)

_DESCRIBE = {
    "Call": "calls {callee} with {n} argument(s)",
    "Expr": "a statement that calls {callee}",
    "Compare": "a comparison using {op}",
    "BoolOp": "combines conditions with {op}",
    "BinOp": "arithmetic with {op}",
    "UnaryOp": "applies {op}",
    "Attribute": "reads the attribute .{attr}",
    "Subscript": "indexes or slices a value",
    "Assign": "an assignment",
    "AugAssign": "an in-place update with {op}",
    "AnnAssign": "an annotated assignment",
    "Return": "returns a value",
    "If": "an if statement",
    "For": "a for loop",
    "While": "a while loop",
    "Raise": "raises an exception",
    "Try": "a try statement",
    "With": "a with statement",
    "IfExp": "a conditional expression",
    "Tuple": "a tuple", "List": "a list", "Dict": "a dict", "Set": "a set",
    "ListComp": "a list comprehension", "DictComp": "a dict comprehension", "GeneratorExp": "a generator",
    "Lambda": "a lambda", "JoinedStr": "an f-string", "Starred": "an unpacking",
}
_OPS = {"Eq": "==", "NotEq": "!=", "Lt": "<", "LtE": "<=", "Gt": ">", "GtE": ">=", "Is": "is", "IsNot": "is not",
        "In": "in", "NotIn": "not in", "And": "and", "Or": "or", "Add": "+", "Sub": "-", "Mult": "*",
        "Div": "/", "FloorDiv": "//", "Mod": "%", "Not": "not", "USub": "unary -", "BitOr": "|", "BitAnd": "&"}


def _snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def _callee(node: ast.AST) -> str | None:
    call = node.value if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) else node
    if not isinstance(call, ast.Call):
        return None
    f = call.func
    return f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)


def _first_op(node: ast.AST) -> str:
    for n in ast.walk(node):
        for v in ([n.op] if hasattr(n, "op") else []) + list(getattr(n, "ops", [])):
            return _OPS.get(type(v).__name__, type(v).__name__)
    return "an operator"


def block_names(examples: list[tuple[ast.AST, int]]) -> list[tuple[str, str]]:
    """(name, description) for each block, in library order, by S4's fixed rule. `examples` holds
    each block's example node (from EXP-005's corpus) and its number of holes. Deterministic."""
    out, seen = [], {}
    for node, holes in examples:
        t = type(node).__name__
        callee = _callee(node)
        stem = _snake(callee) if callee else ("if_stmt" if t == "If" else _snake(t))
        name = f"{stem}_{holes}"
        seen[name] = seen.get(name, 0) + 1
        if seen[name] > 1:
            name = f"{name}_{seen[name]}"
        call = node.value if isinstance(node, ast.Expr) else node
        desc = _DESCRIBE.get(t, f"a {t} pattern").format(
            callee=f"`{callee}`" if callee else "a function", op=f"`{_first_op(node)}`",
            attr=getattr(node, "attr", ""),
            n=len(call.args) + len(call.keywords) if isinstance(call, ast.Call) else 0)
        out.append((name, desc))
    return out


def library_lines(examples: list[str], names: list[tuple[str, str]] | None) -> list[str]:
    """How the library is listed in the prompt: numbered code (L1), or named and described (L2)."""
    if names is None:
        return [f"{i + 1}. {ex}" for i, ex in enumerate(examples)]
    return [f"{n}: {ex}  # {d}" for ex, (n, d) in zip(examples, names, strict=True)]
