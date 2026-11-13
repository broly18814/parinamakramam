# SPDX-License-Identifier: Apache-2.0
"""A5: `pkv map`, a map of a Python project, built without running it and without any AI model.

Plain picture: the city map pkv already draws to pick tests (which file uses which, and which
tests reach which code), printed for people and tools to read before they change anything.

"Reaches" means exactly what it means in test selection (affected.test_reach), so the map and
the tests pkv picks can never disagree. How right the map is was measured against what Python
really loads (REAL-005, docs/product/A5-design.md).
"""

from __future__ import annotations

import subprocess
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

from .affected import is_test_file, test_reach
from .imports import ImportGraph, build_graph

TOP = 15


def kind(path: str) -> str:
    if PurePosixPath(path).name == "conftest.py":
        return "test settings"
    return "test" if is_test_file(path) else "code"


def package_of(path: str, root: Path) -> str:
    """The folder of the outermost package that contains `path`, or the file's own folder."""
    d = PurePosixPath(path).parent
    top = None
    while str(d) not in ("", ".") and (root / d / "__init__.py").exists():
        top = d
        d = d.parent
    return str(top if top is not None else PurePosixPath(path).parent)


@dataclass
class ProjectMap:
    root: Path
    graph: ImportGraph
    kinds: dict[str, str] = field(default_factory=dict)
    packages: dict[str, str] = field(default_factory=dict)
    reach: dict[str, set[str]] = field(default_factory=dict)  # test file -> files it depends on
    reached_by: dict[str, set[str]] = field(default_factory=dict)  # file -> test files that reach it
    ignored: list[str] = field(default_factory=list)  # git-ignored Python files, left out of the map

    @property
    def files(self) -> list[str]:
        return [f for f in self.graph.files if f in self.kinds]

    @property
    def tests(self) -> list[str]:
        return [f for f in self.files if self.kinds[f] == "test"]

    @property
    def code(self) -> list[str]:
        return [f for f in self.files if self.kinds[f] == "code"]

    def unreached(self) -> list[str]:
        return [f for f in self.code if not self.reached_by.get(f)]

    def route(self, test: str, target: str) -> list[str]:
        """One shortest chain of imports from `test` (or a conftest.py that applies to it) to `target`."""
        starts = [test] + [cf for cf in self.files if self.kinds[cf] == "test settings"
                           and _under(test, str(PurePosixPath(cf).parent))]
        came: dict[str, str | None] = {s: None for s in starts}
        queue = deque(starts)
        while queue:
            cur = queue.popleft()
            if cur == target:
                chain = [cur]
                while (prev := came[chain[-1]]) is not None:
                    chain.append(prev)
                return list(reversed(chain))
            for d in sorted(self.graph.deps.get(cur, ())):
                if d not in came and d in self.kinds:
                    came[d] = cur
                    queue.append(d)
        return []

    def to_dict(self) -> dict[str, Any]:
        g = self.graph
        return {
            "schema": "pkv-map/1",
            "files": {f: {"kind": self.kinds[f], "package": self.packages[f],
                          "uses": sorted(set(g.deps.get(f, ())) & set(self.kinds)),
                          "used_by": sorted(set(g.users.get(f, ())) & set(self.kinds)),
                          "reached_by_tests": sorted(self.reached_by.get(f, ()))}
                      for f in self.files},
            "ignored_files_left_out": len(self.ignored),
            "unreached_code": self.unreached(),
            "dynamic_imports": sorted(g.dynamic),
            "unreadable": dict(sorted(g.unreadable.items())),
        }


def _under(path: str, folder: str) -> bool:
    return folder in ("", ".") or path == folder or path.startswith(folder + "/")


def git_ignored(root: Path, files: list[str]) -> set[str]:
    """Which of `files` git ignores (empty if `root` isn't a git repository)."""
    if not files:
        return set()
    r = subprocess.run(["git", "-C", str(root), "check-ignore", "--stdin", "-z"],
                       input="\0".join(files).encode(), capture_output=True)
    if r.returncode not in (0, 1):  # 1 = nothing ignored; anything else = not a repository
        return set()
    return {p for p in r.stdout.decode().split("\0") if p}


def build_map(root: str | Path, graph: ImportGraph | None = None) -> ProjectMap:
    """The map covers the files git doesn't ignore: the same files a receipt's fingerprint covers."""
    root = Path(root)
    g = graph or build_graph(root)
    m = ProjectMap(root=root, graph=g)
    skip = git_ignored(root, g.files)
    m.ignored = sorted(skip)
    for f in g.files:
        if f not in skip:
            m.kinds[f] = kind(f)
            m.packages[f] = package_of(f, root)
    for t in m.tests:
        m.reach[t] = test_reach(g, t) & set(m.kinds)
        for f in m.reach[t]:
            m.reached_by.setdefault(f, set()).add(t)
    return m


def _plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


def render(m: ProjectMap) -> str:
    g = m.graph
    tests, code = m.tests, m.code
    n_settings = sum(1 for k in m.kinds.values() if k == "test settings")
    L = [f"# Project map: {m.root.name}", "",
         f"{_plural(len(m.files), 'Python file')}: {len(code)} code, {len(tests)} test, "
         f"{n_settings} shared test settings (conftest.py). Read without running anything.", ""]

    pkgs = sorted({m.packages[f] for f in m.files})
    L += ["## Parts of the project", "",
          "| Part | Code files | Test files | Uses parts | Code reached by tests |", "|---|---|---|---|---|"]
    for p in pkgs:
        own = [f for f in m.files if m.packages[f] == p]
        pc = [f for f in own if m.kinds[f] == "code"]
        uses = sorted({m.packages[d] for f in own for d in g.deps.get(f, ())
                       if d in m.packages and m.packages[d] != p})
        reached = sum(1 for f in pc if m.reached_by.get(f))
        L.append(f"| `{p}` | {len(pc)} | {sum(1 for f in own if m.kinds[f] == 'test')} | "
                 f"{', '.join(f'`{u}`' for u in uses) or '-'} | {f'{reached} of {len(pc)}' if pc else '-'} |")

    def n_users(f: str) -> int:
        return len(set(g.users.get(f, ())) & set(m.kinds))

    busy = sorted(code, key=lambda f: (-n_users(f), f))[:TOP]
    L += ["", f"## Most-used code (top {min(TOP, len(busy))})", "",
          "A change here affects the most of the project.", "",
          "| File | Used directly by | Reached by test files |", "|---|---|---|"]
    for f in busy:
        L.append(f"| `{f}` | {n_users(f)} | {len(m.reached_by.get(f, ()))} of {len(tests)} |")

    un = m.unreached()
    L += ["", f"## Code no test reaches ({len(un)})", ""]
    if un:
        L.append("\"Tests pass\" says nothing about these files:")
        L += [f"- `{f}`" for f in un]
    else:
        L.append("Every code file is reached by at least one test file.")

    limits = [f"`{f}` loads code by name at run time; links from it may be missing"
              for f in sorted(g.dynamic) if f in m.kinds]
    limits += [f"could not read `{f}` ({e})" for f, e in sorted(g.unreadable.items()) if f in m.kinds]
    if m.ignored:
        n = len(m.ignored)
        limits.append(f"{_plural(n, 'Python file')} that git ignores {'is' if n == 1 else 'are'} left out, "
                      "as from a receipt's fingerprint")
    if limits:
        L += ["", "## Limits of this map", ""] + [f"- {x}" for x in limits]
    L += ["", "---", "A link means one file imports another, found by reading the code. "
          "`pkv map --module FILE` shows one file in detail; `--json` gives the whole map."]
    return "\n".join(L) + "\n"


def render_module(m: ProjectMap, path: str) -> str:
    g = m.graph
    if path not in m.kinds:
        raise KeyError(path)
    users = sorted(set(g.users.get(path, ())) & set(m.kinds))
    deps = sorted(set(g.deps.get(path, ())) & set(m.kinds))
    reached = sorted(m.reached_by.get(path, ()))
    L = [f"# `{path}` ({m.kinds[path]}, in `{m.packages[path]}`)", "",
         f"## Uses ({len(deps)})", ""] + ([f"- `{d}`" for d in deps] or ["Nothing in this project."])
    L += ["", f"## Used by ({len(users)})", ""] + ([f"- `{u}`" for u in users] or ["Nothing in this project."])
    L += ["", f"## Test files that reach it ({len(reached)})", ""]
    if not reached and m.kinds[path] == "code":
        L.append("None: \"tests pass\" says nothing about this file.")
    for t in reached:
        chain = m.route(t, path)
        between = chain[1:-1]
        L.append(f"- `{t}`" + (", through " + " → ".join(f"`{c}`" for c in between) if between else ", directly"))
    if path in g.dynamic:
        L += ["", "This file loads code by name at run time, so some of its links may be missing."]
    return "\n".join(L) + "\n"
