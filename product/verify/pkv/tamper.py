# SPDX-License-Identifier: Apache-2.0
"""Spot changes that weaken the tests instead of fixing the code.

Plain picture: comparing the exam paper before and after the student had it.
Were questions removed? Were some marked "don't count this"? Was the answer
key edited at the same time as the student's answers?

How: for every test file the change touched, read the old version (from
git) and the new version (from disk) as code structure (AST), and compare
test by test. Nothing is executed.

Two levels:
- "suspicious": the change weakens what the tests check. A careful human
  must look before trusting "tests pass".
- "notice": worth a look, often legitimate (e.g. shared test settings changed).

These are signals, not proof of bad intent. Sometimes a test really should
be deleted. The report says what changed; a person decides.
"""

from __future__ import annotations

import ast
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from .affected import is_test_file
from .gitdiff import Change
from .imports import ImportGraph, build_graph, module_names, read_imports

SENSITIVE_WORDS = ("auth", "login", "password", "passwd", "secret", "security",
                   "permission", "crypto", "token", "session", "payment", "billing")

SKIP_NAMES = {"skip", "skipif", "xfail", "skipTest", "skipUnless", "expectedFailure"}


@dataclass
class Finding:
    severity: str  # "suspicious" or "notice"
    kind: str
    file: str
    message: str
    test: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TestInfo:
    asserts: int = 0          # all checks (assert statements, self.assertX(...), pytest.raises, ...)
    exact: int = 0            # checks that pin down an exact value (==, is, assertEqual, ...)
    swallowed: int = 0        # checks inside try/except (or suppress) that would hide their failure
    cases: int | None = 1     # parametrize rows (product of all tables); None if not countable
    skips: int = 0
    tautologies: int = 0
    literals: tuple[str, ...] = ()


# unittest checks that pin down an exact value; other assert* methods are looser.
EXACT_UNITTEST = {
    "assertEqual", "assertEquals", "assertIs", "assertIsNone", "assertListEqual", "assertTupleEqual",
    "assertDictEqual", "assertSetEqual", "assertSequenceEqual", "assertMultiLineEqual", "assertCountEqual",
    "assertAlmostEqual", "assertAlmostEquals",
}
# Exceptions whose handler would also catch a failing check (AssertionError).
CATCHES_FAILURE = {"AssertionError", "Exception", "BaseException"}


def _dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_dotted(node.value)}.{node.attr}"
    if isinstance(node, ast.Call):
        return _dotted(node.func)
    return ""


def _is_skip(node: ast.AST) -> bool:
    """pytest.mark.skip / skipif / xfail, pytest.skip(), unittest.skip..., self.skipTest()."""
    name = _dotted(node)
    return bool(name) and name.split(".")[-1] in SKIP_NAMES


def _is_tautology(test: ast.AST) -> bool:
    """assert True / assert 1 / assert "x" / assert x == x: can never fail."""
    if isinstance(test, ast.Constant):
        return bool(test.value)
    if isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(
            test.ops[0], (ast.Eq, ast.Is, ast.GtE, ast.LtE)):
        return ast.dump(test.left) == ast.dump(test.comparators[0])
    return False


def _check_call_name(node: ast.Call) -> str | None:
    """'assertEqual', 'raises', ... if this call is a check, else None."""
    last = _dotted(node.func).split(".")[-1]
    if last.startswith("assert") or last in ("raises", "warns", "approx", "fail"):
        return last
    return None


def _assert_weight(test: ast.expr) -> tuple[int, int]:
    """(checks, exact checks) in one assert statement.

    `assert a == b` is 1 exact check. `assert (a, b) == (1, 2)` compares two
    pairs of values, so it counts as 2 exact checks; merging two asserts into
    one tuple comparison is therefore not "fewer checks". Anything other than
    ==/is (>, !=, in, is not, a bare truth test) is a looser check.
    """
    if isinstance(test, ast.Compare) and all(isinstance(op, (ast.Eq, ast.Is)) for op in test.ops):
        left, right = test.left, test.comparators[-1]
        if (len(test.ops) == 1 and isinstance(left, (ast.Tuple, ast.List)) and isinstance(right, (ast.Tuple, ast.List))
                and len(left.elts) == len(right.elts) > 1):
            n = len(left.elts)
            return n, n
        return 1, 1
    return 1, 0


def _handler_hides_failure(h: ast.ExceptHandler) -> bool:
    """Would this `except` catch a failing check and carry on silently?"""
    if h.type is None:
        caught = {"BaseException"}  # a bare `except:` catches everything
    elif isinstance(h.type, ast.Tuple):
        caught = {_dotted(e).split(".")[-1] for e in h.type.elts}
    else:
        caught = {_dotted(h.type).split(".")[-1]}
    if not caught & CATCHES_FAILURE:
        return False
    for n in ast.walk(ast.Module(body=h.body, type_ignores=[])):
        if isinstance(n, ast.Raise):
            return False  # re-raised: the failure still counts
        if isinstance(n, ast.Call) and _dotted(n.func).split(".")[-1] == "fail":
            return False  # turned into an explicit failure
    return True


def _checks_in(body: list[ast.stmt]) -> int:
    n = 0
    for node in ast.walk(ast.Module(body=body, type_ignores=[])):
        if isinstance(node, ast.Assert):
            n += _assert_weight(node.test)[0]
        elif isinstance(node, ast.Call) and _check_call_name(node):
            n += 1
    return n


def _swallowed(fn: ast.AST) -> int:
    """Checks placed where their failure would be caught and ignored:
    try/except AssertionError (or Exception, BaseException, bare except)
    without re-raising, and `with contextlib.suppress(AssertionError, ...)`."""
    n = 0
    for node in ast.walk(fn):
        if isinstance(node, ast.Try) and any(_handler_hides_failure(h) for h in node.handlers):
            n += _checks_in(node.body)
        elif isinstance(node, ast.With):
            for item in node.items:
                ctx = item.context_expr
                if (isinstance(ctx, ast.Call) and _dotted(ctx.func).split(".")[-1] == "suppress"
                        and {_dotted(a).split(".")[-1] for a in ctx.args} & CATCHES_FAILURE):
                    n += _checks_in(node.body)
    return n


def _cases(fn: ast.AST) -> int | None:
    """How many parametrize rows feed this test (product over all tables).
    None if a table isn't written out literally (e.g. built by a function)."""
    total = 1
    for d in getattr(fn, "decorator_list", []):
        if isinstance(d, ast.Call) and _dotted(d.func).split(".")[-1] == "parametrize":
            values: ast.expr | None = d.args[1] if len(d.args) > 1 else None
            for kw in d.keywords:
                if kw.arg == "argvalues":
                    values = kw.value
            if not isinstance(values, (ast.List, ast.Tuple)):
                return None
            total *= len(values.elts)
    return total


def _count_checks(fn: ast.AST) -> TestInfo:
    info = TestInfo()
    lits: list[str] = []
    for node in ast.walk(fn):
        if isinstance(node, ast.Assert):
            checks, exact = _assert_weight(node.test)
            info.asserts += checks
            info.exact += exact
            if _is_tautology(node.test):
                info.tautologies += 1
            lits += [repr(c.value) for c in ast.walk(node.test) if isinstance(c, ast.Constant)]
        elif isinstance(node, ast.Call):
            name = _check_call_name(node)
            if name:
                info.asserts += 1  # unittest's self.assertEqual(...), pytest.raises(...)
                if name in EXACT_UNITTEST:
                    info.exact += 1
                lits += [repr(c.value) for a in node.args for c in ast.walk(a)
                         if isinstance(c, ast.Constant)]
            if _is_skip(node.func):
                info.skips += 1
    decorators = getattr(fn, "decorator_list", [])
    info.skips += sum(1 for d in decorators if _is_skip(d))
    info.swallowed = _swallowed(fn)
    info.cases = _cases(fn)
    info.literals = tuple(sorted(lits))
    return info


def read_tests(source: str) -> tuple[dict[str, TestInfo], int]:
    """Map each test (e.g. 'test_login' or 'TestUser::test_name') to what it
    checks, plus a count of skip markers that apply to the whole file."""
    tree = ast.parse(source)
    tests: dict[str, TestInfo] = {}
    module_skips = 0
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            tests[node.name] = _count_checks(node)
        elif isinstance(node, ast.ClassDef) and node.name.startswith("Test") and not any(
                isinstance(i, ast.FunctionDef) and i.name == "__init__" for i in node.body):
            # (pytest does not collect Test* classes that define __init__)
            class_skips = sum(1 for d in node.decorator_list if _is_skip(d))
            module_skips += class_skips
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name.startswith("test"):
                    tests[f"{node.name}::{item.name}"] = _count_checks(item)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            # `pytestmark: list` (a label with no value) has value None: nothing to count.
            if node.value is not None and any(isinstance(t, ast.Name) and t.id == "pytestmark"
                                              for t in targets):
                module_skips += sum(1 for n in ast.walk(node.value) if _is_skip(n))
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and _is_skip(node.value.func):
            module_skips += 1  # pytest.skip(..., allow_module_level=True)
    return tests, module_skips


def _old_source(root: Path, ref: str | None, path: str) -> str | None:
    if ref is None:
        return None
    r = subprocess.run(["git", "-C", str(root), "show", f"{ref}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace") if r.returncode == 0 else None


def _deleted_with_its_code(root: Path, ref: str | None, path: str, changes: list[Change],
                           graph: ImportGraph) -> bool:
    """Was this deleted test file removed together with the code it tested?

    True if the old test imported at least one project module that this same
    change deletes, and imports no project module that still exists (package
    __init__ files aside). Removing a feature and its tests together is
    normal; deleting the tests of code that stays is the suspicious case.
    """
    old_src = _old_source(root, ref, path)
    if old_src is None:
        return False
    try:
        names, _ = read_imports(old_src, PurePosixPath(path).stem, False)
    except SyntaxError:
        return False
    deleted: set[str] = set()
    for c in changes:
        if c.status == "deleted" and c.path.endswith(".py") and not is_test_file(c.path):
            primary, alts = module_names(c.path, root, graph.sub_projects)
            deleted.update(n for n in (primary, *alts) if n)
    still_used = {f for n in names for f in graph.resolve(n, path) if not f.endswith("__init__.py")}
    return bool(names & deleted) and not still_used


def find_tampering(root: str | Path, changes: list[Change], ref: str | None,
                   graph: ImportGraph | None = None) -> list[Finding]:
    root = Path(root)
    findings: list[Finding] = []
    lazy_graph: list[ImportGraph] = [graph] if graph is not None else []

    def get_graph() -> ImportGraph:
        if not lazy_graph:
            lazy_graph.append(build_graph(root))
        return lazy_graph[0]
    code_changed = any(
        c.path.endswith(".py") and not is_test_file(c.path)
        and PurePosixPath(c.path).name != "conftest.py" and c.status != "deleted"
        for c in changes)

    for c in changes:
        path = c.path
        name = PurePosixPath(path).name
        lower = path.lower()

        if any(w in lower for w in SENSITIVE_WORDS) and not is_test_file(path):
            findings.append(Finding("notice", "sensitive-file", path,
                f"{path} looks security-related (login, passwords, payments...) and was {c.status}. "
                "A person should review this change."))

        if name == "conftest.py":
            findings.append(Finding("notice", "shared-settings", path,
                f"the shared test settings in {path} were {c.status}. These affect many tests at once."))
            continue
        if not is_test_file(path) and not (c.old_path and is_test_file(c.old_path)):
            continue

        if c.status == "renamed" and c.old_path and is_test_file(c.old_path) and not is_test_file(path):
            findings.append(Finding("suspicious", "test-file-hidden", path,
                f"the test file {c.old_path} was renamed to {path}. pytest only runs files named "
                "test_*.py or *_test.py, so these tests will no longer run."))
            continue
        if c.status == "deleted":
            if _deleted_with_its_code(root, ref, path, changes, get_graph()):
                findings.append(Finding("notice", "test-deleted-with-code", path,
                    f"the test file {path} was deleted together with the code it tested."))
            else:
                findings.append(Finding("suspicious", "test-file-deleted", path,
                    f"the whole test file {path} was deleted, but the code it tested is still there."))
            continue

        old_src = _old_source(root, ref, c.old_path or path) if c.status != "added" else None
        try:
            new_tests, new_mod_skips = read_tests((root / path).read_text(errors="replace"))
        except (SyntaxError, OSError):
            continue  # pytest will fail to load it, so the run fails anyway
        try:
            old_tests, old_mod_skips = read_tests(old_src) if old_src else ({}, 0)
        except SyntaxError:
            old_tests, old_mod_skips = {}, 0

        for t in sorted(set(old_tests) - set(new_tests)):
            findings.append(Finding("suspicious", "test-removed", path,
                f"the test {t} was removed from {path}.", t))
        if new_mod_skips > old_mod_skips:
            findings.append(Finding("suspicious", "skip-added", path,
                f"{path} now skips tests for the whole file (a 'skip' marker was added)."))
        for t, new in sorted(new_tests.items()):
            old = old_tests.get(t)
            if old is None:  # a new test
                if new.asserts == 0:
                    findings.append(Finding("notice", "checks-nothing", path,
                        f"the new test {t} in {path} has no checks (no assert), so it can never fail.", t))
                if new.tautologies:
                    findings.append(Finding("suspicious", "always-passes", path,
                        f"the new test {t} in {path} contains a check that can never fail (like 'assert True').", t))
                if new.skips:
                    findings.append(Finding("notice", "skip-in-new-test", path,
                        f"the new test {t} in {path} is marked to be skipped.", t))
                continue
            if new.asserts < old.asserts:
                findings.append(Finding("suspicious", "fewer-checks", path,
                    f"the test {t} in {path} now checks less: {old.asserts} checks before, {new.asserts} now.", t))
            if new.skips > old.skips:
                findings.append(Finding("suspicious", "skip-added", path,
                    f"the test {t} in {path} was newly marked to be skipped or expected to fail.", t))
            if new.swallowed > old.swallowed:
                findings.append(Finding("suspicious", "failure-swallowed", path,
                    f"in the test {t} in {path}, {new.swallowed - old.swallowed} check(s) now sit inside a "
                    "try/except (or suppress) that would catch their failure and carry on, so they can't fail.", t))
            if new.asserts >= old.asserts and new.exact < old.exact:
                findings.append(Finding("suspicious", "check-weakened", path,
                    f"the test {t} in {path} now checks less precisely: {old.exact} exact check(s) "
                    f"(like '==' or assertEqual) before, {new.exact} now. Looser checks (like '>' or "
                    "'is not None') can pass even when the result is wrong.", t))
            if old.cases is not None and new.cases is not None and new.cases < old.cases:
                findings.append(Finding("suspicious", "fewer-cases", path,
                    f"the test {t} in {path} now runs fewer cases: {old.cases} before, {new.cases} now "
                    "(rows were removed from its parametrize table).", t))
            if new.tautologies > old.tautologies:
                findings.append(Finding("suspicious", "always-passes", path,
                    f"the test {t} in {path} gained a check that can never fail (like 'assert True').", t))
            if code_changed and new.literals != old.literals and new.asserts >= old.asserts:
                findings.append(Finding("notice", "expected-values-changed", path,
                    f"the expected values in {t} ({path}) changed in the same change as the code. "
                    "Check the new expected values are right, not just made to match.", t))
    return findings


def find_not_run(root: str | Path, tests: list[str], executed: list[list[str]]) -> list[Finding]:
    """Selected tests that pytest never ran: something removed them from the run.

    pkv knows, from reading the code, every test function in the files it
    selected. pytest's result file lists every test it actually ran (or
    skipped). A selected test missing from that list was removed some other
    way: a settings option (-k, -m, --deselect...), a conftest hook, a plugin.
    This check works the same whichever mechanism was used.

    A whole file skipped or failing to load appears in pytest's results as
    one entry with an empty class name; such files are not reported here
    (they are covered by the skip and load-error rules).
    """
    root = Path(root)
    ran: set[tuple[str, str]] = set()
    whole_file: set[str] = set()
    for classname, name, _outcome in executed:
        if not classname:
            whole_file.add(name.split(".")[-1])
            continue
        base = name.split("[")[0]
        parts = classname.split(".")
        if len(parts) >= 2 and parts[-1][:1].isupper():
            ran.add((parts[-2], f"{parts[-1]}::{base}"))
        else:
            ran.add((parts[-1], base))
    findings: list[Finding] = []
    for t in tests:
        stem = PurePosixPath(t).stem
        if stem in whole_file:
            continue
        try:
            static, _ = read_tests((root / t).read_text(errors="replace"))
        except (SyntaxError, OSError):
            continue
        for name in sorted(static):
            if (stem, name) not in ran:
                findings.append(Finding("suspicious", "test-not-run", t,
                    f"the test {name} in {t} was selected but pytest never ran it: something removed it "
                    "from the run (a settings option such as -k or --deselect, a conftest hook, or a plugin).",
                    name))
    return findings
