import operator
from dataclasses import dataclass
from typing import Literal

from . import units
from .core import Error, File, Folder, Groomer, clone

_ops_map = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}


@dataclass
class _RejectByCompare(Groomer):
    attribute: str
    operator: Literal["==", "!=", ">", ">=", "<", "<="]
    threshold: float | int
    reject_files: bool
    reject_folders: bool
    reject_errors: bool
    hide_only: bool

    def __post_init__(self):
        self.get = operator.attrgetter(self.attribute)
        self.cmp = _ops_map[self.operator]

    def groom_folder(self, folder: Folder) -> Folder | None:
        if not self.reject_folders:
            return folder
        return self._process(folder)

    def groom_file(self, file: File) -> Folder | None:
        if not self.reject_files:
            return file
        return self._process(file)

    def groom_error(self, error: Error) -> Folder | None:
        if not self.reject_errors:
            return error
        return self._process(error)

    def _process(self, item: Folder | File | Error):
        if not self.cmp(self.get(item), self.threshold):
            return item

        if self.hide_only:
            item.hide()
            return item


def by_size(
    tree: Folder,
    cmp: Literal["==", "!=", ">", ">=", "<", "<="],
    value: float | int,
    unit: Literal["B", "KB", "MB", "GB", "TB"],
    *,
    reject_files: bool = True,
    reject_folders: bool = True,
    inplace: bool = False,
    hide_only: bool = False,
):
    return _RejectByCompare(
        attribute="bytes",
        operator=cmp,
        threshold=units.convert(value, unit, "B"),
        reject_files=reject_files,
        reject_folders=reject_folders,
        reject_errors=False,
        hide_only=hide_only,
    ).groom(tree, inplace=inplace)
