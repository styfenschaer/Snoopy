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
    inplace: bool
    hide_only: bool

    def __post_init__(self):
        self.get = operator.attrgetter(self.attribute)
        self.cmp = _ops_map[self.operator]

    def groom(self, tree: Folder):
        if not self.inplace:
            tree = clone(tree)

        return super().groom(tree)

    def groom_folder(self, folder: Folder) -> Folder | None:
        if not self.reject_folders:
            return folder

        if not self.cmp(self.get(folder), self.threshold):
            return folder

        if self.hide_only:
            folder.hide(deep=True)
            return folder

    def groom_file(self, file: File) -> Folder | None:
        if not self.reject_files:
            return file

        if not self.cmp(self.get(file), self.threshold):
            return file

        if self.hide_only:
            file.hide()
            return file

    def groom_error(self, error: Error) -> Folder | None:
        if not self.reject_errors:
            return error

        if not self.cmp(self.get(error), self.threshold):
            return error

        if self.hide_only:
            error.hide()
            return error


def by_size(
    tree: Folder,
    cmp: Literal["==", "!=", ">", ">=", "<", "<="],
    value: float | int,
    unit: Literal["TB", "GB", "MB", "KB", "B"],
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
        inplace=inplace,
        hide_only=hide_only,
    ).groom(tree)
