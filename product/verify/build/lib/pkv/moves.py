# SPDX-License-Identifier: Apache-2.0
"""Tell a moved test from a deleted one (defect D4 from REAL-001).

Plain picture: the shop says the stock didn't vanish, it moved to the other
warehouse. We don't take its word for it: we go to the other warehouse and
count every item, check none of the boxes is marked "do not sell", and check
the warehouse is one customers can actually reach.

A test that disappeared or shrank is excused as *moved* only if all of these
hold (docs/product/D4-design.md, section 2):
1. every check it lost reappears unchanged, each counted once, in this same
   change; style differences don't matter (`assertEqual(a, b)` is the same
   check as `assert a == b`), and a check whose failure would be swallowed
   doesn't count;
2. it reappears in a test pytest really runs (a collected test, in a test file);
3. that destination clearly is the original: the same test name, or at least
   80% of the original's disappeared statements reappear in it, in order;
4. the destination gained no skip or xfail mark;
5. no parametrize rows were lost.

When they hold, the suspicious finding becomes a notice. Otherwise it stays
exactly as it was. This module never adds suspicious findings and never
removes any other kind.
"""

from __future__ import annotations

import ast
import copy
from collections import Counter
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from .affected import is_test_file
from .gitdiff import Change
from .tamper import (
    Finding,
    _dotted,
    _handler_hides_failure,
    _is_skip,
    _is_test_function,
    _old_source,
    read_tests,
)

MOVE_KINDS = {"test-removed", "fewer-checks", "check-weakened", "test-file-deleted"}
COVERAGE_NEEDED = 0.8

# unittest's comparison methods, written as the comparison they make.
COMPARE = {
    "assertEqual": "Eq", "assertEquals": "Eq", "assertNotEqual": "NotEq", "assertIs": "Is",
    "assertIsNot": "IsNot", "assertIn": "In", "assertNotIn": "NotIn", "assertGreater": "Gt",
    "assertGreaterEqual": "GtE", "assertLess": "Lt", "assertLessEqual": "LtE",
}
RAISES = {"raises", "assertRaises", "assertRaisesRegex"}
NONE = ast.parse("None", mode="eval").body


class _SameSpelling(ast.NodeTransformer):
    """`exc.exception` (unittest's assertRaises) and `exc.value` (pytest.raises)
    are the same thing: the exception that was raised."""

    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
        self.generic_visit(node)
        if node.attr == "exception" and isinstance(node.value, ast.Name):
            node.attr = "value"
        return node


def _d(node: ast.AST) -> str:
    return ast.dump(_SameSpelling().visit(copy.deepcopy(node)))


def _assert_key(test: ast.expr) -> str:
    if isinstance(test, ast.Compare) and len(test.ops) == 1:
        return f"{type(test.ops[0]).__name__}({_d(test.left)}, {_d(test.comparators[0])})"
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return f"false({_d(test.operand)})"
    return f"true({_d(test)})"


def _call_name(call: ast.Call) -> str:
    return _dotted(call.func).split(".")[-1]


def _is_check_call(call: ast.Call) -> bool:
    name = _call_name(call)
    return name.startswith("assert") or name in ("raises", "warns", "approx", "fail", "deprecated_call")


def _call_key(call: ast.Call, body: list[ast.stmt] | None = None) -> str:
    name, a = _call_name(call), call.args
    kws = {k.arg: k.value for k in call.keywords if k.arg}
    if name in COMPARE and len(a) >= 2:
        return f"{COMPARE[name]}({_d(a[0])}, {_d(a[1])})"
    if name == "assertTrue" and a:
        return f"true({_d(a[0])})"
    if name == "assertFalse" and a:
        return f"false({_d(a[0])})"
    if name in ("assertIsNone", "assertIsNotNone") and a:
        return f"{'Is' if name == 'assertIsNone' else 'IsNot'}({_d(a[0])}, {_d(NONE)})"
    if name in RAISES and a:
        rest = a[1:]
        match = kws.get("match")
        if name == "assertRaisesRegex" and rest:
            match, rest = rest[0], rest[1:]
        inner = [_d(x) for x in rest] + [_stmt_key(s) for s in (body or [])]
        return f"raises({_d(a[0])}, {_d(match) if match is not None else '-'}, [{'; '.join(inner)}])"
    inner = [_d(x) for x in a] + [f"{k}={_d(v)}" for k, v in sorted(kws.items())]
    inner += [_stmt_key(s) for s in (body or [])]
    return f"{name}({'; '.join(inner)})"


def _with_check(st: ast.With) -> ast.Call | None:
    for item in st.items:
        ctx = item.context_expr
        if isinstance(ctx, ast.Call) and _is_check_call(ctx):
            return ctx
    return None


def _stmt_key(st: ast.stmt) -> str:
    """One statement, spelled the same way whatever the test style."""
    if isinstance(st, ast.Assert):
        return _assert_key(st.test)
    if isinstance(st, ast.Expr) and isinstance(st.value, ast.Call) and _is_check_call(st.value):
        return _call_key(st.value)
    if isinstance(st, ast.With) and (call := _with_check(st)) is not None:
        return _call_key(call, st.body)
    return _d(st)


def _swallows(st: ast.stmt) -> bool:
    if isinstance(st, ast.Try):
        return any(_handler_hides_failure(h) for h in st.handlers)
    if isinstance(st, ast.With):
        for item in st.items:
            ctx = item.context_expr
            if isinstance(ctx, ast.Call) and _call_name(ctx) == "suppress" and {
                    _dotted(x).split(".")[-1] for x in ctx.args} & {"AssertionError", "Exception", "BaseException"}:
                return True
    return False


def _checks(stmts: list[ast.stmt], out: Counter[str]) -> None:
    """Every check in these statements whose failure would really count."""
    for st in stmts:
        if _swallows(st):
            if isinstance(st, ast.Try):  # the handlers and else/finally still count
                for h in st.handlers:
                    _checks(h.body, out)
                _checks(st.orelse + st.finalbody, out)
            continue
        if isinstance(st, ast.Assert):
            out[_assert_key(st.test)] += 1
            continue
        if isinstance(st, ast.With) and (call := _with_check(st)) is not None:
            out[_call_key(call, st.body)] += 1
            if _call_name(call) not in RAISES:
                _checks(st.body, out)
            continue
        if isinstance(st, ast.Expr) and isinstance(st.value, ast.Call) and _is_check_call(st.value):
            out[_call_key(st.value)] += 1
            continue
        for field in ("body", "orelse", "finalbody"):
            inner = getattr(st, field, None)
            if isinstance(inner, list) and inner and isinstance(inner[0], ast.stmt):
                _checks(inner, out)
        for h in getattr(st, "handlers", []):
            _checks(h.body, out)


@dataclass
class Shape:
    """What a test checks, statement by statement, and how it can be switched off."""

    checks: Counter[str]
    stmts: list[str]
    skips: int
    cases: int | None


def _body(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> list[ast.stmt]:
    body = fn.body
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
            and isinstance(body[0].value.value, str):
        body = body[1:]  # the docstring
    return body


def shapes(source: str) -> dict[str, Shape]:
    """Each collected test in a file (same names as tamper.read_tests)."""
    tree = ast.parse(source)
    infos, module_skips = read_tests(source)
    out: dict[str, Shape] = {}

    def add(key: str, fn: ast.FunctionDef | ast.AsyncFunctionDef, extra_skips: int) -> None:
        if key not in infos:
            return
        found: Counter[str] = Counter()
        body = _body(fn)
        _checks(body, found)
        out[key] = Shape(found, [_stmt_key(s) for s in body], infos[key].skips + extra_skips, infos[key].cases)

    for node in tree.body:
        if _is_test_function(node):
            assert isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            add(node.name, node, module_skips)
        elif isinstance(node, ast.ClassDef):
            class_skips = sum(1 for d in node.decorator_list if _is_skip(d))
            for item in node.body:
                if _is_test_function(item):
                    assert isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                    add(f"{node.name}::{item.name}", item, module_skips + class_skips)
    return out


def _coverage(disappeared: list[str], appeared: list[str]) -> float:
    """Share of the disappeared statements that reappear, in the same order."""
    if not disappeared:
        return 0.0
    blocks = SequenceMatcher(None, disappeared, appeared, autojunk=False).get_matching_blocks()
    return sum(b.size for b in blocks) / len(disappeared)


def _minus(a: list[str], b: list[str]) -> list[str]:
    """Items of a (in order) not accounted for by b (as a multiset)."""
    left = Counter(b)
    out = []
    for x in a:
        if left[x]:
            left[x] -= 1
        else:
            out.append(x)
    return out


def _base(name: str) -> str:
    return name.split("::")[-1]


def excuse_moves(root: str | Path, changes: list[Change], ref: str | None,
                 findings: list[Finding]) -> list[Finding]:
    candidates = [f for f in findings if f.severity == "suspicious" and f.kind in MOVE_KINDS]
    if not candidates or ref is None:
        return findings
    root = Path(root)
    old: dict[tuple[str, str], Shape] = {}
    new: dict[tuple[str, str], Shape] = {}
    for c in changes:
        was_test = is_test_file(c.old_path or c.path)
        if c.status != "added" and was_test:
            src = _old_source(root, ref, c.old_path or c.path)
            try:
                for t, s in (shapes(src) if src else {}).items():
                    old[(c.path, t)] = s  # keyed by today's path, so a renamed file lines up
            except SyntaxError:
                pass
        if c.status != "deleted" and is_test_file(c.path):
            try:
                for t, s in shapes((root / c.path).read_text(errors="replace")).items():
                    new[(c.path, t)] = s
            except (SyntaxError, OSError):
                pass

    # What each test gained in this change: checks (to be claimed once) and statements.
    gained: dict[tuple[str, str], Counter[str]] = {}
    appeared: dict[tuple[str, str], list[str]] = {}
    for key, s in new.items():
        before = old.get(key)
        gained[key] = s.checks - (before.checks if before else Counter())
        appeared[key] = _minus(s.stmts, before.stmts) if before else list(s.stmts)

    def destination(src_key: tuple[str, str], lost: Counter[str], disappeared: list[str],
                    src: Shape) -> tuple[str, str] | None:
        best: tuple[float, tuple[str, str]] | None = None
        for key in sorted(new):
            if key == src_key or not lost <= gained[key]:
                continue
            same_name = _base(key[1]) == _base(src_key[1])
            cover = _coverage(disappeared, appeared[key])
            if not same_name and cover < COVERAGE_NEEDED:
                continue
            d = new[key]
            if d.skips > src.skips:
                continue  # it was switched off on the way
            if src.cases is not None and d.cases is not None and d.cases < src.cases:
                continue  # rows of its table were lost
            if not lost and not disappeared:
                continue
            score = (2.0 if same_name else 0.0) + cover
            if best is None or score > best[0]:
                best = (score, key)
        return best[1] if best else None

    def excuse(path: str, test: str, whole: bool) -> tuple[str, str] | None:
        src = old.get((path, test))
        if src is None:
            return None
        now = None if whole else new.get((path, test))
        lost = src.checks - (now.checks if now else Counter())
        disappeared = _minus(src.stmts, now.stmts) if now else list(src.stmts)
        if now is not None and not lost:
            return None  # nothing went anywhere, so a move can't explain the finding
        dest = destination((path, test), lost, disappeared, src)
        if dest is not None:
            gained[dest] -= lost  # each reappearing check can explain only one loss
        return dest

    out: list[Finding] = []
    for f in findings:
        if f not in candidates:
            out.append(f)
            continue
        if f.kind == "test-file-deleted":
            tests = sorted(t for (p, t) in old if p == f.file)
            dests = [excuse(f.file, t, whole=True) for t in tests]
            found = [d for d in dests if d is not None]
            if tests and len(found) == len(tests):
                where = ", ".join(sorted({f"{p}::{t}" for p, t in found}))
                out.append(Finding("notice", "test-file-moved", f.file,
                    f"the test file {f.file} was deleted, but all {len(tests)} of its tests reappear unchanged "
                    f"in tests pytest runs ({where}): moved, renamed or reorganised, nothing lost."))
            else:
                out.append(f)
            continue
        if not f.test:
            out.append(f)
            continue
        dest = excuse(f.file, f.test, whole=f.kind == "test-removed")
        if dest is None:
            out.append(f)
        else:
            what = "was removed" if f.kind == "test-removed" else "checks less"
            out.append(Finding("notice", "test-moved", f.file,
                f"the test {f.test} in {f.file} {what}, but every check it lost reappears unchanged in "
                f"{dest[0]}::{dest[1]}, a test pytest runs: moved, renamed or reorganised, nothing lost.", f.test))
    return out
