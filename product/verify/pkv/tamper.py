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

from .affected import is_test_file
from .gitdiff import Change

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

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TestInfo:
    asserts: int = 0
    skips: int = 0
    tautologies: int = 0
    literals: tuple = ()


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


def _count_checks(fn: ast.AST) -> TestInfo:
    info = TestInfo()
    lits: list = []
    for node in ast.walk(fn):
        if isinstance(node, ast.Assert):
            info.asserts += 1
            if _is_tautology(node.test):
                info.tautologies += 1
            lits += [repr(c.value) for c in ast.walk(node.test) if isinstance(c, ast.Constant)]
        elif isinstance(node, ast.Call):
            last = _dotted(node.func).split(".")[-1]
            if last.startswith("assert") or last in ("raises", "warns", "approx", "fail"):
                info.asserts += 1  # unittest's self.assertEqual(...), pytest.raises(...)
                lits += [repr(c.value) for a in node.args for c in ast.walk(a)
                         if isinstance(c, ast.Constant)]
            if _is_skip(node.func):
                info.skips += 1
    decorators = getattr(fn, "decorator_list", [])
    info.skips += sum(1 for d in decorators if _is_skip(d))
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
        elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            class_skips = sum(1 for d in node.decorator_list if _is_skip(d))
            module_skips += class_skips
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name.startswith("test"):
                    tests[f"{node.name}::{item.name}"] = _count_checks(item)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(t, ast.Name) and t.id == "pytestmark" for t in targets):
                module_skips += sum(1 for n in ast.walk(node.value) if _is_skip(n))
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and _is_skip(node.value.func):
            module_skips += 1  # pytest.skip(..., allow_module_level=True)
    return tests, module_skips


def _old_source(root: Path, ref: str | None, path: str) -> str | None:
    if ref is None:
        return None
    r = subprocess.run(["git", "-C", str(root), "show", f"{ref}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace") if r.returncode == 0 else None


def find_tampering(root: str | Path, changes: list[Change], ref: str | None) -> list[Finding]:
    root = Path(root)
    findings: list[Finding] = []
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
            findings.append(Finding("suspicious", "test-file-deleted", path,
                f"the whole test file {path} was deleted."))
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
            if new.tautologies > old.tautologies:
                findings.append(Finding("suspicious", "always-passes", path,
                    f"the test {t} in {path} gained a check that can never fail (like 'assert True').", t))
            if code_changed and new.literals != old.literals and new.asserts >= old.asserts:
                findings.append(Finding("notice", "expected-values-changed", path,
                    f"the expected values in {t} ({path}) changed in the same change as the code. "
                    "Check the new expected values are right, not just made to match.", t))
    return findings
