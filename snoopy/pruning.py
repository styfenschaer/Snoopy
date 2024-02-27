import operator
import re
import warnings
from dataclasses import dataclass
from typing import Callable, Literal

from . import units
from .core import Error, File, Folder, Transformer

_ops_map = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}


@dataclass
class _PruneByCompare(Transformer):
    attr: str
    operator: Literal["==", "!=", ">", ">=", "<", "<="]
    threshold: float | int
    prune_files: bool
    prune_folders: bool
    prune_errors: bool
    hide_only: bool

    def __post_init__(self):
        if not self.hide_only:
            warnings.warn(
                "Argument 'hide_only' was set to False. Removing "
                "elements from a directory tree can result in "
                "incorrectly reported folder properties."
            )

        self.get = operator.attrgetter(self.attr)
        self.cmp = _ops_map[self.operator]

    def visit_folder(self, folder: Folder) -> Folder | None:
        if not self.prune_folders:
            return folder
        return self._process(folder)

    def visit_file(self, file: File) -> Folder | None:
        if not self.prune_files:
            return file
        return self._process(file)

    def visit_error(self, error: Error) -> Error | None:
        if not self.prune_errors:
            return error
        return self._process(error)

    def _process(self, item: Folder | File | Error):
        if not self.cmp(self.get(item), self.threshold):
            return item

        if self.hide_only:
            item.hide()
            return item


def _parse_size_cmp(expr):
    match = re.match(r"\s*([<>=]+)\s*(\d+(\.\d+)?)\s*(\w+)\s*", expr)
    if not match:
        raise ValueError(f"cannnot parse expression '{expr}'")

    operator, number, _, unit = match.groups()
    return operator, float(number), unit


def by_size(
    tree: Folder,
    expr: str,
    *,
    prune_files: bool = True,
    prune_folders: bool = True,
    hide_only: bool = True,
):
    op, value, unit = _parse_size_cmp(expr)
    return _PruneByCompare(
        attr="bytes",
        operator=op,
        threshold=units.to_bytes(value, unit),
        prune_files=prune_files,
        prune_folders=prune_folders,
        prune_errors=False,
        hide_only=hide_only,
    )(tree, inplace=True)


@dataclass
class _FromFilter(Transformer):
    filter: Callable[[Folder | File | Error], bool]
    prune_files: bool
    prune_folders: bool
    prune_errors: bool
    hide_only: bool

    def visit_folder(self, folder: Folder) -> Folder | None:
        return self._process(folder, self.prune_folders)

    def visit_file(self, file: File) -> Folder | None:
        return self._process(file, self.prune_files)

    def visit_error(self, error: Error) -> Error | None:
        return self._process(error, self.prune_errors)

    def _process(self, item: Folder | File | Error, cond: bool):
        if not cond:
            return item

        if not self.filter(item):
            return item

        if self.hide_only:
            item.hide()
            return item


def from_filter(
    filter: Callable[[Folder | File | Error], bool],
    tree: Folder,
    prune_files: bool = True,
    prune_folders: bool = True,
    prune_errors: bool = False,
    hide_only: bool = False,
):
    return _FromFilter(
        filter=filter,
        prune_files=prune_files,
        prune_folders=prune_folders,
        prune_errors=prune_errors,
        hide_only=hide_only,
    )(tree, inplace=True)
