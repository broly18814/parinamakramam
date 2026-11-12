# SPDX-License-Identifier: Apache-2.0
"""Do the tests still bite? A differential mutation check on the changed lines (A2).

Plain picture: to find out whether a smoke alarm works, you light a match under
it. Here the "match" is a small deliberate mistake in the code (a *mutant*):
`==` becomes `!=`, `100` becomes `101`, `and` becomes `or`. A test that fails
on the mistake *kills* the mutant.

What makes this check differential: mutants are made in the OLD version of the
lines the change touched, and two copies of the old commit are tested, one with
the OLD tests and one with the NEW tests. A mutant the old tests killed but the
new tests don't is a check the change took away, however the change did it
(loosened, edited, replaced, skipped, made unable to fail, or switched off in
settings). Mutants that neither side kills count the same on both sides, so
they can't cause an alarm. Design: docs/product/A2-design.md.

Nothing here runs anything except the project's own tests, in temporary copies,
with the same minimal environment as `pkv check`.
"""

from __future__ import annotations

import ast
import io
import os
import re
import shutil
import tarfile
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, TypeVar

from .affected import Selection, is_test_file
from .gitdiff import Change, _git
from .runner import _run_one, find_python, minimal_env, read_junit
from .tamper import Finding

TEST_SETTINGS = {"conftest.py", "pytest.ini", "tox.ini", "setup.cfg", "pyproject.toml"}
TEST_DIRS = {"tests", "test"}
MAX_MUTANTS = 30
TOTAL_BUDGET_S = 300.0

_COMPARE = {ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE,
            ast.GtE: ast.Gt, ast.Is: ast.IsNot, ast.IsNot: ast.Is, ast.In: ast.NotIn, ast.NotIn: ast.In}
_BINOP = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.Div, ast.Div: ast.Mult,
          ast.FloorDiv: ast.Div, ast.Mod: ast.Mult}
_SYMBOL = {ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=",
           ast.Is: "is", ast.IsNot: "is not", ast.In: "in", ast.NotIn: "not in", ast.Add: "+",
           ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.FloorDiv: "//", ast.Mod: "%"}


def is_test_related(path: str) -> bool:
    """Test files, files in a tests/ folder, and settings files that change how tests run."""
    p = PurePosixPath(path)
    return is_test_file(path) or p.name in TEST_SETTINGS or any(part in TEST_DIRS for part in p.parts[:-1])


@dataclass(frozen=True)
class Site:
    """One place a mutant can be made: the node's position in `ast.walk` order, and what to do."""

    index: int
    line: int
    col: int
    action: str  # e.g. "compare:0", "binop", "boolop", "not", "neg", "number", "bool", "return", "negate-test"
    label: str   # plain description, e.g. "`==` → `!=`"


def changed_old_lines(root: Path, ref: str, change: Change) -> set[int]:
    """Line numbers, in the OLD file, that the change modified or deleted."""
    old = change.old_path or change.path
    out = _git(root, "diff", "-U0", "-M", "--no-ext-diff", ref, "--", old, change.path).decode(errors="replace")
    lines: set[int] = set()
    for m in re.finditer(r"^@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@", out, re.M):
        start, count = int(m.group(1)), int(m.group(2) if m.group(2) is not None else 1)
        lines.update(range(start, start + count))
    return lines


def find_sites(source: str, lines: set[int]) -> list[Site]:
    """Every mutation site on the given lines of `source`, in a fixed order."""
    tree = ast.parse(source)
    sites: list[Site] = []
    for i, node in enumerate(ast.walk(tree)):
        line = getattr(node, "lineno", None)
        if line not in lines:
            continue
        col = getattr(node, "col_offset", 0)
        if isinstance(node, ast.Compare):
            for k, op in enumerate(node.ops):
                if type(op) in _COMPARE:
                    new = _COMPARE[type(op)]
                    sites.append(Site(i, line, col, f"compare:{k}", f"`{_SYMBOL[type(op)]}` → `{_SYMBOL[new]}`"))
        elif isinstance(node, ast.BinOp) and type(node.op) in _BINOP:
            swapped = _BINOP[type(node.op)]
            sites.append(Site(i, line, col, "binop", f"`{_SYMBOL[type(node.op)]}` → `{_SYMBOL[swapped]}`"))
        elif isinstance(node, ast.BoolOp):
            sites.append(Site(i, line, col, "boolop", "`and` → `or`" if isinstance(node.op, ast.And)
                              else "`or` → `and`"))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            sites.append(Site(i, line, col, "not", "`not x` → `x`"))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            sites.append(Site(i, line, col, "neg", "`-x` → `x`"))
        elif isinstance(node, ast.Constant) and isinstance(node.value, bool):
            sites.append(Site(i, line, col, "bool", f"`{node.value}` → `{not node.value}`"))
        elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            sites.append(Site(i, line, col, "number", f"`{node.value!r}` → `{node.value + 1!r}`"))
            if node.value not in (0, 1):  # +1 is tiny next to a large number; doubling is a real change
                sites.append(Site(i, line, col, "double", f"`{node.value!r}` → `{node.value * 2!r}`"))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            sites.append(Site(i, line, col, "drop-call", f"`….{node.func.attr}(…)` call removed"))
        elif isinstance(node, ast.Return) and node.value is not None and not (
                isinstance(node.value, ast.Constant) and node.value.value is None):
            sites.append(Site(i, line, col, "return", "`return …` → `return None`"))
        elif isinstance(node, (ast.If, ast.While)):
            sites.append(Site(i, line, col, "negate-test", "condition negated"))
    return sorted(sites, key=lambda s: (s.line, s.col, s.index, s.action))


T = TypeVar("T")


def spread(items: list[T], limit: int) -> list[T]:
    """At most `limit` items, evenly spaced, so every changed region gets some mutants."""
    if len(items) <= limit:
        return items
    return [items[(k * len(items)) // limit] for k in range(limit)]


def apply_site(source: str, site: Site) -> str:
    """The source with exactly one mutation applied (formatting may change; behaviour is what matters)."""
    tree = ast.parse(source)
    nodes = list(ast.walk(tree))
    node = nodes[site.index]
    parent_of: dict[int, tuple[ast.AST, str, int | None]] = {}
    for parent in nodes:
        for name, value in ast.iter_fields(parent):
            if isinstance(value, ast.AST):
                parent_of[id(value)] = (parent, name, None)
            elif isinstance(value, list):
                for j, item in enumerate(value):
                    if isinstance(item, ast.AST):
                        parent_of[id(item)] = (parent, name, j)

    def replace(old: ast.AST, new: ast.AST) -> None:
        parent, name, j = parent_of[id(old)]
        if j is None:
            setattr(parent, name, new)
        else:
            getattr(parent, name)[j] = new

    action = site.action
    if action.startswith("compare:") and isinstance(node, ast.Compare):
        k = int(action.split(":")[1])
        node.ops[k] = _COMPARE[type(node.ops[k])]()
    elif action == "binop" and isinstance(node, ast.BinOp):
        node.op = _BINOP[type(node.op)]()
    elif action == "boolop" and isinstance(node, ast.BoolOp):
        node.op = ast.Or() if isinstance(node.op, ast.And) else ast.And()
    elif action in ("not", "neg") and isinstance(node, ast.UnaryOp):
        replace(node, node.operand)
    elif action == "bool" and isinstance(node, ast.Constant):
        node.value = not node.value
    elif action == "number" and isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        node.value = node.value + 1
    elif action == "double" and isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        node.value = node.value * 2
    elif action == "drop-call" and isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        replace(node, node.func.value)
    elif action == "return" and isinstance(node, ast.Return):
        node.value = ast.Constant(value=None)
    elif action == "negate-test" and isinstance(node, (ast.If, ast.While)):
        node.test = ast.UnaryOp(op=ast.Not(), operand=node.test)
    else:  # pragma: no cover - sites and actions are made together
        raise ValueError(f"cannot apply {site}")
    return ast.unparse(ast.fix_missing_locations(tree)) + "\n"


@dataclass
class SuiteRun:
    passed: set[str]
    failed: set[str]
    broken: bool  # the run as a whole failed (collection error, timeout, crash): every test counts as failing
    seconds: float


@dataclass
class MutationReport:
    ran: bool
    reason: str
    mutants: int = 0
    killed_by_old: int = 0
    killed_by_new: int = 0
    lost: list[dict[str, Any]] = field(default_factory=list)
    partial: bool = False
    old_tests: list[str] = field(default_factory=list)
    new_tests: list[str] = field(default_factory=list)
    excluded_old: list[str] = field(default_factory=list)  # failed on the unmutated old code
    excluded_new: list[str] = field(default_factory=list)  # new tests that fail on the old code
    duration_s: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def findings(self) -> list[Finding]:
        if not self.ran:
            return [Finding("notice", "mutation-check", "", f"Mutation check not run: {self.reason}.")]
        out = [Finding("notice", "mutation-check", "",
                       f"Mutation check: {self.mutants} small deliberate mistakes in the changed lines of the old "
                       f"code; the old tests caught {self.killed_by_old}, the new tests caught "
                       f"{self.killed_by_new}." + (" (Stopped early: time limit.)" if self.partial else ""))]
        if self.lost:
            examples = "; ".join(f"{m['file']} line {m['line']}: {m['change']}" for m in self.lost[:5])
            files = sorted({m["file"] for m in self.lost})
            out.append(Finding(
                "suspicious", "checks-lost", files[0],
                f"{len(self.lost)} mistake(s) in the changed code that the old tests caught are no longer caught "
                f"by the new tests, so the change removed checks: {examples}"
                + (f" (and {len(self.lost) - 5} more)" if len(self.lost) > 5 else "")))
        return out


def _extract(root: Path, ref: str, dest: Path) -> None:
    data = _git(root, "archive", "--format=tar", ref)
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        if hasattr(tarfile, "data_filter"):
            tar.extractall(dest, filter="data")
        else:  # pragma: no cover - Python versions without extraction filters
            tar.extractall(dest)  # our own repository's archive


def _run_suite(folder: Path, tests: list[str], python: str, env: dict[str, str], timeout: float) -> SuiteRun:
    junit = folder.parent / f"{folder.name}-junit.xml"
    if junit.exists():
        junit.unlink()
    cmd = [python, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--junitxml={junit}", "--", *tests]
    t0 = time.monotonic()
    code, hung, _ = _run_one(folder, cmd, env, timeout)
    seconds = time.monotonic() - t0
    _, _, executed = read_junit(junit)
    names = {f"{c}::{n}": o for c, n, o in executed}
    passed = {k for k, o in names.items() if o == "passed"}
    failed = {k for k, o in names.items() if o in ("failed", "error")}
    broken = hung or code is None or code not in (0, 1, 5)
    return SuiteRun(passed, failed, broken, seconds)


def _killed(baseline: SuiteRun, run: SuiteRun) -> bool:
    if not baseline.passed:
        return False
    return run.broken or bool(baseline.passed & (run.failed | (baseline.passed - run.passed)))


def mutation_check(root: Path, ref: str | None, changes: list[Change], sel: Selection, *,
                   python: str | None = None, keep_env: list[str] | None = None,
                   max_mutants: int = MAX_MUTANTS, budget_s: float = TOTAL_BUDGET_S) -> MutationReport:
    t0 = time.monotonic()
    if ref is None:
        return MutationReport(False, "there is no earlier commit to compare with")
    if not any(is_test_related(c.path) or (c.old_path and is_test_related(c.old_path)) for c in changes):
        return MutationReport(False, "the change didn't touch tests or test settings, so no check can have been lost")
    sources = [c for c in changes if c.status in ("modified", "renamed") and c.path.endswith(".py")
               and not is_test_related(c.path)]
    plans: list[tuple[str, str, Site]] = []
    for c in sources:
        old_path = c.old_path or c.path
        old_source = _git(root, "show", f"{ref}:{old_path}").decode("utf-8", errors="replace")
        try:
            for s in find_sites(old_source, changed_old_lines(root, ref, c)):
                plans.append((old_path, old_source, s))
        except SyntaxError:
            continue
    if not plans:
        return MutationReport(False, "no changed lines of existing code to make mistakes in")
    chosen = spread(plans, max_mutants)

    py = python or find_python(root)
    with tempfile.TemporaryDirectory() as td:
        a, b = Path(td) / "old-tests", Path(td) / "new-tests"
        _extract(root, ref, a)
        shutil.copytree(a, b)
        for c in changes:
            for p in {c.path, c.old_path} - {None}:
                assert p is not None
                if not is_test_related(p):
                    continue
                target, here = b / p, root / p
                if here.is_file():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(here, target)
                elif target.exists():
                    target.unlink()
        new_tests = [t for t in sel.tests if (b / t).is_file()]
        old_tests = sorted({t for t in sel.tests if (a / t).is_file()} |
                           {p for c in changes for p in (c.path, c.old_path or "")
                            if p and is_test_file(p) and (a / p).is_file() and c.status in ("deleted", "renamed")})
        if not old_tests or not new_tests:
            return MutationReport(False, "no tests on one side to compare", old_tests=old_tests, new_tests=new_tests)

        def env_for(folder: Path) -> dict[str, str]:
            env = minimal_env(keep_env)
            extra = [str(folder), str(folder / "src")]
            env["PYTHONPATH"] = os.pathsep.join(extra + ([env["PYTHONPATH"]] if "PYTHONPATH" in env else []))
            return env

        env_a, env_b = env_for(a), env_for(b)
        base_a = _run_suite(a, old_tests, py, env_a, 600)
        base_b = _run_suite(b, new_tests, py, env_b, 600)
        report = MutationReport(True, "", old_tests=old_tests, new_tests=new_tests,
                                excluded_old=sorted(base_a.failed), excluded_new=sorted(base_b.failed))
        if base_a.broken or not base_a.passed:
            report.ran = False
            report.reason = "the old tests don't pass on the old code, so there is nothing to compare"
            return report
        if base_b.broken or not base_b.passed:
            report.ran, report.reason = False, ("the new tests can't run on the old code (for example, they use a "
                                                "renamed module or a new function), so there is nothing to compare")
            return report
        per_run = max(10.0, 5 * max(base_a.seconds, base_b.seconds))
        for old_path, old_source, site in chosen:
            if time.monotonic() - t0 > budget_s:
                report.partial = True
                break
            try:
                mutated = apply_site(old_source, site)
            except (ValueError, SyntaxError):
                continue
            for folder in (a, b):
                (folder / old_path).write_text(mutated, encoding="utf-8")
            old_kill = _killed(base_a, _run_suite(a, old_tests, py, env_a, per_run))
            new_kill = _killed(base_b, _run_suite(b, new_tests, py, env_b, per_run))
            for folder in (a, b):
                (folder / old_path).write_text(old_source, encoding="utf-8")
            report.mutants += 1
            report.killed_by_old += old_kill
            report.killed_by_new += new_kill
            if old_kill and not new_kill:
                report.lost.append({"file": old_path, "line": site.line, "change": site.label})
    report.duration_s = round(time.monotonic() - t0, 3)
    return report
