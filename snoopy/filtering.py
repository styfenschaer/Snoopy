import fnmatch
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .core import Error, File, Folder


def chain(*filters: Callable[[Folder | File | Error], bool]):
    def chained_filters(item: Folder | File | Error) -> bool:
        return any(filter(item) for filter in filters)

    return chained_filters


@dataclass(init=False)
class Name:
    def __init__(self, *names: str):
        self.names = names

    def __call__(self, item: Folder | File):
        return item.name in self.names


@dataclass(init=False)
class Regex:
    def __init__(self, *patterns: str):
        self.patterns = patterns

    def __call__(self, item: Folder | File):
        string = str(item.path)
        return any(re.match(pattern, string) for pattern in self.patterns)


@dataclass(init=False)
class Pattern:
    def __init__(self, *patterns: str, root: str | Path = None):
        if isinstance(root, str):
            root = Path(root)

        self.root = root
        self.parts = [Path(pat).parts for pat in patterns]

    @classmethod
    def from_gitignore(cls, path: str | Path):
        patterns = []
        for line in Path(path).read_text().splitlines():
            if line and (not line.startswith("#")):
                patterns.append(line)

        root = Path(path).resolve().parent
        return cls(*patterns, root=root)

    def __call__(self, item: File | Folder):
        path = item.path
        if self.root is not None:
            path = path.relative_to(self.root)

        item_parts = path.parts
        for pat_parts in self.parts:
            for name, pat in zip(
                item_parts[::-1],
                pat_parts[::-1],
            ):
                if not fnmatch.fnmatch(name, pat):
                    break
            else:
                return True
        return False


class GitIgnore:
    def __new__(self, path: str | Path):
        return Pattern.from_gitignore(path)


def pycache(item: Folder):
    return Name("__pycache__")(item)


def venv(item: Folder):
    return Name(".venv")(item)


def hidden(item: Folder):
    return item.name.startswith(".")
