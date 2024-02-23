import abc
from dataclasses import dataclass, field

from .core import Error, File, Folder, Groomer, clone


@dataclass
class _Sort(abc.ABC, Groomer):
    reverse: bool = field(default=True)
    inplace: bool = field(default=False)

    @abc.abstractmethod
    def key(self, x: Folder | File | Error):
        return x

    def groom_folder(self, folder: Folder):
        if not self.inplace:
            folder = clone(folder)

        folder.items.sort(key=self.key, reverse=self.reverse)
        return folder


class ByLastModified(_Sort):
    def key(self, x: Folder | File | Error):
        return getattr(x, "last_modified", -1)


def by_last_modified(
    tree: Folder,
    /,
    *,
    reverse: bool = True,
    inplace: bool = False,
):
    tree = ByLastModified(reverse, inplace).groom(tree)
    if not inplace:
        return tree


class ByLastAccess(_Sort):
    def key(self, x: Folder | File | Error):
        return getattr(x, "last_access", -1)


def by_last_access(
    tree: Folder,
    /,
    *,
    reverse: bool = True,
    inplace: bool = False,
):
    tree = ByLastAccess(reverse, inplace).groom(tree)
    if not inplace:
        return tree


class ByCreated(_Sort):
    def key(self, x: Folder | File | Error):
        return getattr(x, "created", -1)


def by_created(
    tree: Folder,
    /,
    *,
    reverse: bool = True,
    inplace: bool = False,
):
    tree = ByCreated(reverse, inplace).groom(tree)
    if not inplace:
        return tree


class BySize(_Sort):
    def key(self, x: Folder | File | Error):
        return getattr(x, "bytes", -1)


def by_size(
    tree: Folder,
    /,
    *,
    reverse: bool = True,
    inplace: bool = False,
):
    tree = BySize(reverse, inplace).groom(tree)
    if not inplace:
        return tree


@dataclass
class ByNumFiles(_Sort):
    deep_files: bool = field(default=False)

    def key(self, x: Folder | File | Error):
        try:
            if self.deep_files:
                return len(x.deep_files)
            else:
                return len(x.files)
        except AttributeError:
            return -1


def by_num_files(
    tree: Folder,
    /,
    *,
    reverse: bool = True,
    inplace: bool = False,
    deep_files: bool = True,
):
    tree = ByNumFiles(reverse, inplace, deep_files).groom(tree)
    if not inplace:
        return tree
