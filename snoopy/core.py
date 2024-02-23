from __future__ import annotations

import copy
import os
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Callable, Literal

try:
    from rich.console import Console

    _rich_installed_ = True
except ImportError:
    _rich_installed_ = False


this_path = Path(__file__).parent


# fmt: off
def isfile(obj): return isinstance(obj, File)
def isfolder(obj): return isinstance(obj, Folder)
def iserror(obj): return isinstance(obj, Error)
# fmt: on


def get_last_modified(path: Path):
    ts = os.path.getmtime(path)
    dt = datetime.fromtimestamp(ts)
    return dt.replace(microsecond=0)


def get_last_access(path: Path):
    ts = os.path.getatime(path)
    dt = datetime.fromtimestamp(ts)
    return dt.replace(microsecond=0)


def get_created(path: Path):
    ts = os.path.getctime(path)
    dt = datetime.fromtimestamp(ts)
    return dt.replace(microsecond=0)


def get_file_size(path: Path):
    return os.path.getsize(path)


class Error(Exception):
    def __init__(self, *args):
        self.args = args
        self.when = datetime.now().replace(microsecond=0)
        self.hidden = False

    def __str__(self):
        return f"Error{self.args} [{self.when}]"

    def hide(self):
        self.hidden = True

    def unhide(self):
        self.hidden = False


@dataclass
class File:
    path: Path

    def __post_init__(self):
        self.name = self.path.name
        self.bytes = get_file_size(self.path)
        self.created = get_created(self.path)
        self.last_access = get_last_access(self.path)
        self.last_modified = get_last_modified(self.path)
        self.hidden = False

    def __str__(self):
        return (
            f"File({self.path}, "
            f"bytes={self.bytes:,d}, "
            f"created={self.created}, "
            f"accessed={self.last_access}, "
            f"modified={self.last_modified})"
        )

    def hide(self):
        self.hidden = True

    def unhide(self):
        self.hidden = False


@dataclass
class Folder:
    path: Path
    items: list[Folder | File | Error] = field(default_factory=list)

    @property
    def bytes(self) -> float | int:
        return sum(getattr(item, "bytes", 0) for item in self.items)

    @property
    def files(self):
        return [item for item in self.items if isfile(item)]

    @property
    def deep_files(self):
        return self.files + sum([f.deep_files for f in self.folders], [])

    @property
    def folders(self):
        return [item for item in self.items if isfolder(item)]

    @property
    def deep_folders(self):
        return self.folders + sum([f.deep_folders for f in self.folders], [])

    @property
    def errors(self):
        return [item for item in self.items if iserror(item)]

    @property
    def deep_errors(self):
        return self.errors + sum([f.deep_errors for f in self.folders], [])

    def __post_init__(self):
        self.name = self.path.name
        self.created = get_created(self.path)
        self.last_access = get_last_access(self.path)
        self.last_modified = get_last_modified(self.path)
        self.hidden = False

    def __str__(self):
        return (
            f"Folder({self.path}, "
            f"bytes={self.bytes:,d}, "
            f"files=({len(self.files):,d}/{len(self.deep_files):,d}), "
            f"folders=({len(self.folders):,d}/{len(self.deep_folders):,d}), "
            f"created={self.created}, "
            f"accessed={self.last_access}, "
            f"modified={self.last_modified}, "
            f"errors=({len(self.errors):,d}/{len(self.deep_errors):,d}))"
        )

    def hide(self, deep: bool = True):
        self.hidden = True
        if deep:
            for item in self.items:
                item.hide()

    def unhide(self, deep: bool = True):
        self.hidden = False
        if deep:
            for item in self.items:
                item.unhide()


def clone(obj: Folder | File | Error):
    return copy.deepcopy(obj)


def snoop(
    path: Path | str,
    /,
    *,
    ignore_folder: Callable[[Folder], bool] = lambda folder: False,
    ignore_file: Callable[[File], bool] = lambda file: False,
    ignore_error: Callable[[Error], bool] = lambda error: False,
    raise_on_error: bool = True,
    verbosity: Literal[0, 1, 2] = 0,
    _folder: Folder | None = None,
):
    if not isinstance(path, Path):
        path = Path(path)

    if not (path.exists() and path.is_dir()):
        raise ValueError("path must be an existing directory")

    if _folder is None:
        folder = Folder(path)
    else:
        folder = _folder

    try:
        for item in (path / item for item in os.listdir(path)):
            if item.is_dir():
                subfolder = Folder(item)
                if not ignore_folder(subfolder):
                    folder.items.append(subfolder)
                    snoop(
                        item,
                        ignore_folder=ignore_folder,
                        ignore_file=ignore_file,
                        verbosity=verbosity,
                        _folder=subfolder,
                    )
            elif item.is_file():
                file = File(item)

                if verbosity >= 2:
                    print(file)

                if not ignore_file(file):
                    folder.items.append(file)

    except Exception as exc:
        if raise_on_error:
            raise exc

        error = Error(exc)

        if verbosity >= 1:
            print(error)

        if not ignore_error(error):
            folder.items.append(error)

    if verbosity >= 1:
        print(folder)

    return folder


@dataclass
class Groomer:
    def groom(self, tree: Folder, *, inplace: bool = True) -> Folder | None:
        if not inplace:
            tree = clone(tree)

        self.depth = 0

        tree = self.groom_folder(tree)
        if tree is None:
            return

        return self._groom(tree)

    def groom_folder(self, folder: Folder) -> Folder | None:
        return folder

    def groom_file(self, file: File) -> File | None:
        return file

    def groom_error(self, error: Error) -> Error | None:
        return error

    def _groom(self, folder: Folder) -> Folder | None:
        self.depth += 1

        new_items = []
        for item in folder.items:
            item = self._groom_item(item)

            if item is None:
                continue

            if isfolder(item):
                item = self._groom(item)

            new_items.append(item)

        folder.items.clear()
        folder.items.extend(new_items)

        self.depth -= 1
        return folder

    def _groom_item(self, item: Folder | File | Error):
        if isfolder(item):
            return self.groom_folder(item)
        if isfile(item):
            return self.groom_file(item)
        if iserror(item):
            return self.groom_error(item)
        raise TypeError(f"unexpected item of type {type(item)}")


_FOLDER_PREFIX = "📁 "
_FILE_PREFIX = "📄 "
_ERROR_PREFIX = "🤬 "


@dataclass
class Exhibition:
    tree: Folder
    max_depth: int = field(default=float("inf"), kw_only=True)
    max_files_display: int = field(default=float("inf"), kw_only=True)
    max_folders_display: int = field(default=float("inf"), kw_only=True)
    max_errors_display: int = field(default=float("inf"), kw_only=True)
    format_file: Callable[[File], str] = field(
        default=lambda file: str(file), kw_only=True
    )
    format_folder: Callable[[Folder], str] = field(
        default=lambda folder: str(folder), kw_only=True
    )
    format_error: Callable[[Error], str] = field(
        default=lambda error: str(error), kw_only=True
    )
    prefix_file: Callable[[Exhibition, File], str] = field(
        default=lambda exh, file: _FILE_PREFIX, kw_only=True
    )
    prefix_folder: Callable[[Exhibition, Folder], str] = field(
        default=lambda exh, folder: _FOLDER_PREFIX, kw_only=True
    )
    prefix_error: Callable[[Exhibition, Error], str] = field(
        default=lambda exh, error: _ERROR_PREFIX, kw_only=True
    )
    indent: str = field(default=" │ ", kw_only=True)
    init_prefix: str = field(default="", kw_only=True)
    display_hidden: bool = field(default=False, kw_only=True)

    def __str__(self):
        self.buffer = StringIO()
        if self.max_depth <= 0:
            return self.buffer.getvalue()

        self.depth = 0
        self._format(self.tree)
        return self.buffer.getvalue()

    def _join_append(self, *chunks: str):
        print("".join(chunks), file=self.buffer)

    def _format(self, folder: Folder):
        self._join_append(
            self.init_prefix + self.depth * self.indent,
            self.prefix_folder(self, folder),
            self.format_folder(folder),
        )

        if self.depth >= self.max_depth:
            return

        self.depth += 1

        count_table = {
            Folder: self.max_folders_display,
            File: self.max_files_display,
            Error: self.max_errors_display,
        }

        for item in folder.items:
            if item.hidden and (not self.display_hidden):
                continue

            item_type = type(item)

            count = count_table.get(item_type)
            if count is None:
                raise TypeError(f"unexpected item of type {type(item)}")

            if count_table[item_type] <= 0:
                continue

            if isfile(item):
                self._join_append(
                    self.init_prefix + self.depth * self.indent,
                    self.prefix_file(self, item),
                    self.format_file(item),
                )
            elif iserror(item):
                self._join_append(
                    self.init_prefix + self.depth * self.indent,
                    self.prefix_error(self, item),
                    self.format_error(item),
                )
            elif isfolder(item):
                self._format(item)

            count_table[item_type] -= 1

        self.depth -= 1


def visit(obj: Exhibition | str, /, *, style: str | None = None):
    if not _rich_installed_:
        warnings.warn("missing package 'rich'; displaying normally")
        return print(obj)

    if style is None:
        style = "bold medium_purple"

    Console(style=style).print(str(obj))


def snapshot(
    obj: str | Exhibition,
    /,
    *,
    filename: str | Path,
    style: str | None = None,
    silent: bool = True,
):
    if not _rich_installed_:
        raise RuntimeError("failed to save due to missing package 'rich'")

    if style is None:
        style = "medium_purple"

    console = Console(record=True, file=StringIO(), style=style)
    console.print(str(obj))
    console.save_html(filename, inline_styles=True)

    if not silent:
        print("Woof woof! 🐶✨📸")
