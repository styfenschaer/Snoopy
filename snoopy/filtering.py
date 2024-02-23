from dataclasses import dataclass
from typing import Callable

from .core import Error, File, Folder


def chain(*filters: Callable[[Folder | File | Error], bool]):
    def chained_filters(item: Folder | File | Error) -> bool:
        return any(filter(item) for filter in filters)

    return chained_filters


def ignore_hidden(folder: Folder):
    return folder.name.startswith(".")


def ignore_pycache(folder: Folder):
    return folder.name == "__pycache__"


def ignore_venv(folder: Folder):
    return folder.name == ".venv"


@dataclass
class IgnoreNames:
    names: File | list[File]

    def __post_init__(self):
        if isinstance(self.names, str):
            self.names = [self.names]

    def __call__(self, item: Folder | File):
        return item.name in self.names
