"""Decide which test files a change could affect, and say why.

Plain picture: drop dye into the river at every changed file and follow it
*backwards* along the import roads. Every test file the dye reaches could be
broken by the change, so it must be run. Programmers call this *change
impact analysis* or *test impact analysis*; following the roads is a
*breadth-first search* (visit nearest neighbours first, then theirs...).

Safety rule: when we cannot trace a change (a settings file, a data file, an
unreadable file), we do not guess. We say "run every test" and explain why.
Running too many tests wastes a little time; running too few can hide a bug.
"""

from __future__ import annotations

import fnmatch
from collections import deque
from dataclasses import asdict, dataclass, field
from pathlib import PurePosixPath

from .gitdiff import Change
from .imports import ImportGraph, build_graph, module_names

# Files whose change can alter how *every* test behaves.
CONFIG_PATTERNS = [
    "pyproject.toml", "setup.cfg", "setup.py", "tox.ini", "pytest.ini", "noxfile.py",
    "requirements*.txt", "constraints*.txt", "Pipfile", "Pipfile.lock",
    "poetry.lock", "uv.lock", "pdm.lock", ".python-version", "MANIFEST.in",
]
# Files that cannot change what code does.
NO_EFFECT_PATTERNS = [
    "*.md", "*.rst", "*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.ico",
    "LICENSE*", "COPYING*", "AUTHORS*", "CHANGELOG*", ".gitignore", ".gitattributes",
    "docs/*", ".github/ISSUE_TEMPLATE/*",
]


def is_test_file(path: str) -> bool:
    """pytest's default naming rule: test_*.py or *_test.py."""
    name = PurePosixPath(path).name
    return name.endswith(".py") and (name.startswith("test_") or name.endswith("_test.py"))


def _matches(path: str, patterns: list[str]) -> bool:
    name = PurePosixPath(path).name
    return any(fnmatch.fnmatch(name, p) or fnmatch.fnmatch(path, p) for p in patterns)


def _under(path: str, folder: str) -> bool:
    return folder in ("", ".") or path == folder or path.startswith(folder + "/")


@dataclass
class Selection:
    """The answer, with every reason recorded so a report can show its work."""

    tests: list[str] = field(default_factory=list)
    reasons: dict[str, str] = field(default_factory=dict)
    all_tests: list[str] = field(default_factory=list)
    run_all: bool = False
    run_all_reasons: list[str] = field(default_factory=list)
    no_effect: list[str] = field(default_factory=list)
    removed_tests: list[str] = field(default_factory=list)
    unreadable: dict[str, str] = field(default_factory=dict)
    dynamic_imports: list[str] = field(default_factory=list)
    changes: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def select_tests(root, changes: list[Change], graph: ImportGraph | None = None) -> Selection:
    graph = graph or build_graph(root)
    existing = set(graph.files)
    sel = Selection(changes=[asdict(c) for c in changes])
    sel.all_tests = sorted(f for f in graph.files if is_test_file(f))

    came_from: dict[str, str | None] = {}  # file -> the next file toward the change
    why_seed: dict[str, str] = {}         # starting files -> what happened to them
    deleted_names: dict[str, str] = {}     # module name -> deleted path

    def seed(path: str, reason: str) -> None:
        if path in existing and path not in came_from:
            came_from[path] = None
            why_seed[path] = reason

    settings_scopes: list[tuple[str, str]] = []  # (settings file, folder it governs)
    events: list[tuple[str, str]] = []
    for c in changes:
        if c.status == "renamed":
            events.append((c.old_path, "deleted (renamed away)"))
            events.append((c.path, f"renamed from {c.old_path}"))
        else:
            events.append((c.path, c.status))

    for path, what in events:
        if path.endswith(".py"):
            if what.startswith("deleted"):
                if is_test_file(path) and what == "deleted":
                    sel.removed_tests.append(path)
                primary, alts = module_names(path, graph.root)
                for n in [primary, *alts]:
                    if n:
                        deleted_names[n] = path
            else:
                seed(path, f"was {what}")
            if path in graph.unreadable:
                sel.run_all_reasons.append(
                    f"{path} could not be read ({graph.unreadable[path]}), so its effects can't be traced"
                )
        elif _matches(path, CONFIG_PATTERNS):
            folder = str(PurePosixPath(path).parent)
            if folder in ("", "."):
                sel.run_all_reasons.append(
                    f"{path} is a project settings file; it can change how every test behaves"
                )
            else:
                # A settings file in a sub-folder (one project inside a bigger
                # repository) governs only the tests in that folder.
                settings_scopes.append((path, folder))
        elif _matches(path, NO_EFFECT_PATTERNS):
            sel.no_effect.append(path)
        else:
            sel.run_all_reasons.append(
                f"{path} is not Python code, so we can't trace what uses it"
            )

    # Files that imported something which no longer exists.
    for f in graph.files:
        gone = sorted(n for n in graph.raw_imports.get(f, ()) if n in deleted_names
                      and not graph.resolve(n, f))
        if gone:
            seed(f, f"imports {gone[0]}, but {deleted_names[gone[0]]} was deleted")

    # Follow the roads backwards (breadth-first search).
    queue = deque(came_from)
    while queue:
        cur = queue.popleft()
        for user in sorted(graph.users.get(cur, ())):
            if user not in came_from:
                came_from[user] = cur
                queue.append(user)

    def tail(f: str) -> str:
        """Why f is affected, as the end of a sentence about f:
        'was modified', or 'uses a.py, which uses b.py, which was modified'."""
        chain = [f]
        while came_from[chain[-1]] is not None:
            chain.append(came_from[chain[-1]])
        if len(chain) == 1:
            return why_seed[f]
        return "uses " + ", which uses ".join(chain[1:]) + ", which " + why_seed[chain[-1]]

    chosen: dict[str, str] = {}
    for f in came_from:
        if is_test_file(f):
            chosen[f] = f"{f} {tail(f)}"
    # A conftest.py holds shared test settings for every test in its folder
    # and below. If the dye reached one, all those tests are affected.
    for c in sorted(came_from):
        if PurePosixPath(c).name == "conftest.py":
            folder = str(PurePosixPath(c).parent)
            for t in sel.all_tests:
                if _under(t, folder) and t not in chosen:
                    chosen[t] = f"{t} uses the shared test settings in {c}, which {tail(c)}"

    for path, folder in settings_scopes:
        for t in sel.all_tests:
            if _under(t, folder) and t not in chosen:
                chosen[t] = (f"{t} is in {folder}/, whose settings file {path} was changed; "
                             "settings can change how every test there behaves")

    sel.unreadable = dict(graph.unreadable)
    sel.dynamic_imports = sorted(graph.dynamic)
    if sel.run_all_reasons:
        sel.run_all = True
        for t in sel.all_tests:
            chosen.setdefault(t, f"{t} runs because every test must: {sel.run_all_reasons[0]}")
    sel.tests = sorted(chosen)
    sel.reasons = {t: chosen[t] for t in sel.tests}
    sel.removed_tests.sort()
    sel.no_effect.sort()
    return sel
