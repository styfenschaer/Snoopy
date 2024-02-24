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
    names: str | list[str]

    def __post_init__(self):
        if isinstance(self.names, str):
            self.names = [self.names]

    def __call__(self, item: Folder | File):
        return item.name in self.names


@dataclass
class IgnoreSuffix:
    suffix: str | list[str]

    def __post_init__(self):
        if isinstance(self.suffix, str):
            self.suffix = [self.suffix]

    def __call__(self, item: File | Folder):
        return item.path.suffix in self.suffix


# fmt: off
def ignore_pdf(file: File): return file.path.suffix == ".pdf"
def ignore_txt(file: File): return file.path.suffix == ".txt"
def ignore_py(file: File): return file.path.suffix == ".py"
def ignore_md(file: File): return file.path.suffix == ".md"
def ignore_tex(file: File): return file.path.suffix == ".tex"
# fmt:on
