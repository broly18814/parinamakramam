# SPDX-License-Identifier: Apache-2.0
"""Build a map of which Python files use which other Python files.

Plain picture: a city map of one-way roads. If file A says `import b`, there
is a road from A to B. If B changes, everything that has a road leading to B
(directly or through other files) could break. Programmers call this map an
*import graph* (graph = dots joined by lines).

How we read imports: Python can describe its own code as a tree of parts
(the *abstract syntax tree*, via the built-in `ast` module). We read that
tree instead of running the code, so nothing in the user's project is ever
executed while we build the map. This is called *static analysis*.

Honest limits (reported to the user, never hidden):
- Imports built at run time (`importlib.import_module(name)`, `__import__`)
  cannot be seen statically. Files that do this are flagged as "dynamic".
- Files with syntax errors cannot be read. They are listed as unreadable.
"""

from __future__ import annotations

import ast
import os
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

SKIP_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "env", ".env", "node_modules",
    "__pycache__", ".tox", ".nox", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "build", "dist", "site-packages", ".eggs",
}


# Files that mark the top folder of a Python project. In a repository that
# holds several projects, each project's own top folder is where Python looks
# for that project's code (pytest's rootdir and `pythonpath`, or an install).
PROJECT_MARKERS = {"pyproject.toml", "setup.py", "setup.cfg", "pytest.ini", "tox.ini"}


def _walk(root: Path) -> list[tuple[str, list[str]]]:
    """(folder relative to root, its file names), skipping tool and
    environment folders that are not the project's own code."""
    out: list[tuple[str, list[str]]] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d for d in dirnames if d not in SKIP_DIRS and not d.endswith(".egg-info")
        )
        out.append((Path(dirpath).relative_to(root).as_posix(), sorted(filenames)))
    return out


def python_files(root: Path) -> list[str]:
    """All .py files under root (posix relative paths)."""
    return sorted(
        f if d == "." else f"{d}/{f}" for d, names in _walk(root) for f in names if f.endswith(".py")
    )


def project_roots(root: Path) -> list[str]:
    """Sub-folders that are the top of a Python project of their own."""
    return sorted(d for d, names in _walk(root) if d != "." and PROJECT_MARKERS & set(names))


def module_names(rel: str, root: Path, sub_projects: list[str] | tuple[str, ...] = ()) -> tuple[str, list[str]]:
    """Names other code could use to import this file.

    Returns (primary, alternatives).

    primary follows Python's package rule: walk up through folders that
    contain __init__.py. `app/models.py` inside package `app` is
    "app.models"; a lone `tests/helpers.py` (no __init__.py) is "helpers".

    alternatives are the dotted path from the repository's top folder and
    from the top folder of each sub-project containing the file
    (`sub_projects`, see project_roots), each also without a leading `src/`
    for projects that keep code there (the common "src layout").
    """
    p = PurePosixPath(rel)
    parts: list[str] = [] if p.name == "__init__.py" else [p.stem]
    d = p.parent
    while str(d) not in ("", ".") and (root / d / "__init__.py").exists():
        parts.insert(0, d.name)
        d = d.parent
    primary = ".".join(parts)
    full = list(p.parent.parts) + ([] if p.name == "__init__.py" else [p.stem])
    tops = [0] + [len(PurePosixPath(sp).parts) for sp in sub_projects if rel.startswith(sp + "/")]
    alts: set[str] = set()
    for t in tops:
        rest = full[t:]
        alts.add(".".join(rest))
        if rest and rest[0] == "src" and len(rest) > 1:
            alts.add(".".join(rest[1:]))
    alts.discard(primary)
    alts.discard("")
    return primary, sorted(alts)


def _with_parents(name: str) -> list[str]:
    """'a.b.c' -> ['a', 'a.b', 'a.b.c']: importing a.b.c also runs a and a.b."""
    bits = name.split(".")
    return [".".join(bits[: i + 1]) for i in range(len(bits))]


_DYNAMIC_CALLS = {"import_module", "__import__"}


def read_imports(source: str, primary: str, is_package: bool) -> tuple[set[str], bool]:
    """Return (imported names, uses_dynamic_import) for one file's source.
    Raises SyntaxError if the file is not valid Python."""
    tree = ast.parse(source)
    names: set[str] = set()
    dynamic = False
    package = primary if is_package else primary.rpartition(".")[0]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.update(_with_parents(alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # relative import: "from . import x", "from ..a import b"
                pkg_bits = package.split(".") if package else []
                keep = len(pkg_bits) - (node.level - 1)
                base_bits = pkg_bits[: max(keep, 0)]
                if node.module:
                    base_bits += node.module.split(".")
                base = ".".join(base_bits)
            else:
                base = node.module or ""
            if base:
                names.update(_with_parents(base))
            for alias in node.names:
                if alias.name != "*":
                    names.add(f"{base}.{alias.name}" if base else alias.name)
        elif isinstance(node, ast.Call):
            fn = node.func
            called = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
            if called in _DYNAMIC_CALLS:
                dynamic = True
    return names, dynamic


@dataclass
class ImportGraph:
    """The map. `deps[a]` = files that a uses; `users[b]` = files that use b."""

    root: Path
    files: list[str]
    deps: dict[str, set[str]] = field(default_factory=dict)
    users: dict[str, set[str]] = field(default_factory=dict)
    raw_imports: dict[str, set[str]] = field(default_factory=dict)
    unreadable: dict[str, str] = field(default_factory=dict)
    dynamic: set[str] = field(default_factory=set)
    index: dict[str, set[str]] = field(default_factory=dict)
    primary: dict[str, str] = field(default_factory=dict)
    sub_projects: list[str] = field(default_factory=list)  # see project_roots

    def resolve(self, name: str, importer: str) -> set[str]:
        """Which project files does `name` refer to, seen from `importer`?
        Names that match nothing are outside the project (Python's own
        library or installed packages) and are ignored."""
        cands = self.index.get(name, set()) - {importer}
        if len(cands) <= 1:
            return cands
        # Several files share the name. Prefer the one next to the importer
        # (pytest puts a test's own folder on the import path), then exact
        # package names; if still ambiguous, keep all (safer to over-select).
        here = str(PurePosixPath(importer).parent)
        siblings = {c for c in cands if str(PurePosixPath(c).parent) == here}
        if siblings:
            return siblings
        exact = {c for c in cands if self.primary.get(c) == name}
        return exact or cands


def build_graph(root: str | os.PathLike[str]) -> ImportGraph:
    root = Path(root)
    files = python_files(root)
    subs = project_roots(root)
    g = ImportGraph(root=root, files=files, sub_projects=subs)
    for f in files:
        primary, alts = module_names(f, root, subs)
        g.primary[f] = primary
        for n in [primary, *alts]:
            if n:
                g.index.setdefault(n, set()).add(f)
    for f in files:
        try:
            source = (root / f).read_text(encoding="utf-8", errors="replace")
            names, dyn = read_imports(source, g.primary[f], f.endswith("__init__.py"))
        except SyntaxError as e:
            g.unreadable[f] = f"line {e.lineno}: {e.msg}"
            names, dyn = set(), False
        g.raw_imports[f] = names
        if dyn:
            g.dynamic.add(f)
        targets: set[str] = set()
        for n in names:
            targets |= g.resolve(n, f)
        g.deps[f] = targets
        for t in targets:
            g.users.setdefault(t, set()).add(f)
    return g
