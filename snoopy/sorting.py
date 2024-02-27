from dataclasses import dataclass
from typing import Any, Callable

from .core import Error, File, Folder, Transformer


@dataclass
class _Sorting(Transformer):
    attr: str
    default: Any
    reverse: bool
    func: Callable[[Any], Any] | None = None

    def key(self, x: Folder | File | Error):
        val = getattr(x, self.attr, self.default)
        if self.func is not None:
            val = self.func(val)
        return val

    def visit_folder(self, folder: Folder):
        folder.items.sort(key=self.key, reverse=self.reverse)
        return folder


def by_last_modified(
    tree: Folder,
    *,
    reverse: bool = True,
    inplace: bool = False,
):
    return _Sorting(
        "last_modified",
        default=-1,
        reverse=reverse,
    )(tree, inplace=inplace)


def by_last_access(
    tree: Folder,
    *,
    reverse: bool = True,
    inplace: bool = False,
):
    return _Sorting(
        "last_access",
        default=-1,
        reverse=reverse,
    )(tree, inplace=inplace)


def by_created(
    tree: Folder,
    *,
    reverse: bool = True,
    inplace: bool = False,
):
    return _Sorting(
        "created",
        default=-1,
        reverse=reverse,
    )(tree, inplace=inplace)


def by_num_files(
    tree: Folder,
    *,
    reverse: bool = True,
    inplace: bool = False,
    deep_files: bool = True,
):
    return _Sorting(
        ("files", "deep_files")[deep_files],
        default=[],
        reverse=reverse,
        func=len,
    )(tree, inplace=inplace)


def by_num_folders(
    tree: Folder,
    *,
    reverse: bool = True,
    inplace: bool = False,
    deep_folders: bool = True,
):
    return _Sorting(
        ("folders", "deep_folders")[deep_folders],
        default=[],
        reverse=reverse,
        func=len,
    )(tree, inplace=inplace)


def by_num_errors(
    tree: Folder,
    *,
    reverse: bool = True,
    inplace: bool = False,
    deep_errors: bool = True,
):
    return _Sorting(
        ("errors", "deep_errors")[deep_errors],
        default=[],
        reverse=reverse,
        func=len,
    )(tree, inplace=inplace)


def by_size(
    tree: Folder,
    *,
    reverse: bool = True,
    inplace: bool = False,
):
    return _Sorting(
        "bytes",
        default=-1,
        reverse=reverse,
    )(tree, inplace=inplace)


def by_kind(
    tree: Folder,
    *,
    reverse: bool = True,
    inplace: bool = False,
):
    return _Sorting(
        "__class__",
        default=None,
        reverse=reverse,
        func=lambda c: c.__name__,
    )(tree, inplace=inplace)


def alphabetic(
    tree: Folder,
    *,
    case_sensitive: bool = True,
    reverse: bool = False,
    inplace: bool = False,
):
    return _Sorting(
        "name",
        default="",
        reverse=reverse,
        func=(lambda s: s.lower(), None)[case_sensitive],
    )(tree, inplace=inplace)
