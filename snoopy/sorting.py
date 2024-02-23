from dataclasses import dataclass
from typing import Any, Callable

from .core import Error, File, Folder, Groomer, clone


@dataclass
class _Sorting(Groomer):
    attribute: str
    default: Any
    reverse: bool
    inplace: bool
    wrapper: Callable[[Any], Any] | None = None

    def key(self, x: Folder | File | Error):
        val = getattr(x, self.attribute, self.default)
        if self.wrapper is not None:
            val = self.wrapper(val)
        return val

    def groom_folder(self, folder: Folder):
        if not self.inplace:
            folder = clone(folder)

        folder.items.sort(key=self.key, reverse=self.reverse)
        return folder


def by_last_modified(
    tree: Folder,
    /,
    *,
    reverse: bool = True,
    inplace: bool = False,
):
    tree = _Sorting(
        "last_modified",
        default=-1,
        reverse=reverse,
        inplace=inplace,
    ).groom(tree)
    if not inplace:
        return tree


def by_last_access(
    tree: Folder,
    /,
    *,
    reverse: bool = True,
    inplace: bool = False,
):
    tree = _Sorting(
        "last_access",
        default=-1,
        reverse=reverse,
        inplace=inplace,
    ).groom(tree)
    if not inplace:
        return tree


def by_created(
    tree: Folder,
    /,
    *,
    reverse: bool = True,
    inplace: bool = False,
):
    tree = _Sorting(
        "created",
        default=-1,
        reverse=reverse,
        inplace=inplace,
    ).groom(tree)
    if not inplace:
        return tree


def by_size(
    tree: Folder,
    /,
    *,
    reverse: bool = True,
    inplace: bool = False,
):
    tree = _Sorting(
        "bytes",
        default=-1,
        reverse=reverse,
        inplace=inplace,
    ).groom(tree)
    if not inplace:
        return tree


def by_num_files(
    tree: Folder,
    /,
    *,
    reverse: bool = True,
    inplace: bool = False,
    deep_files: bool = True,
):

    tree = _Sorting(
        ("files", "deep_files")[deep_files],
        default=[],
        reverse=reverse,
        inplace=inplace,
        wrapper=len,
    ).groom(tree)
    if not inplace:
        return tree


def by_num_folders(
    tree: Folder,
    /,
    *,
    reverse: bool = True,
    inplace: bool = False,
    deep_folders: bool = True,
):

    tree = _Sorting(
        ("folders", "deep_folders")[deep_folders],
        default=[],
        reverse=reverse,
        inplace=inplace,
        wrapper=len,
    ).groom(tree)
    if not inplace:
        return tree


def by_num_errors(
    tree: Folder,
    /,
    *,
    reverse: bool = True,
    inplace: bool = False,
    deep_errors: bool = True,
):

    tree = _Sorting(
        ("errors", "deep_errors")[deep_errors],
        default=[],
        reverse=reverse,
        inplace=inplace,
        wrapper=len,
    ).groom(tree)
    if not inplace:
        return tree
