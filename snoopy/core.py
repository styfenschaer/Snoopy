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

    def __str__(self):
        return f"Error{self.args} [{self.when}]"


@dataclass
class File:
    path: Path

    def __post_init__(self):
        self.name = self.path.name
        self.bytes = get_file_size(self.path)
        self.created = get_created(self.path)
        self.last_access = get_last_access(self.path)
        self.last_modified = get_last_modified(self.path)

    def __str__(self):
        return (
            f"File({self.path}, "
            f"bytes={self.bytes:,d}, "
            f"created={self.created}, "
            f"accessed={self.last_access}, "
            f"modified={self.last_modified})"
        )


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
    def groom(self, tree: Folder) -> Folder | None:
        tree = self.groom_folder(tree)
        if tree is None:
            return None

        new_items = []
        for item in tree.items:
            item = self._groom__item(item)
            if item is None:
                continue
            if isfolder(item):
                item = self.groom(item)
            new_items.append(item)

        tree.items.clear()
        tree.items.extend(new_items)
        return tree

    def _groom__item(self, item: Folder | File | Error):
        if isfolder(item):
            return self.groom_folder(item)
        if isfile(item):
            return self.groom_file(item)
        if iserror(item):
            return self.groom_error(item)
        raise TypeError(f"unexpected item of type {type(item)}")

    def groom_folder(self, folder: Folder) -> Folder | None:
        return folder

    def groom_file(self, file: File) -> File | None:
        return file

    def groom_error(self, error: Error) -> Error | None:
        return error


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

    def __str__(self):
        self.buffer = StringIO()
        self._format(self.tree, prefix=self.init_prefix, depth=0)
        return self.buffer.getvalue()

    def _format(self, folder: Folder, prefix: int, depth: int):
        self.depth = depth

        pfx = prefix + self.prefix_folder(self, folder)
        print(pfx + self.format_folder(folder), file=self.buffer)

        if depth >= self.max_depth:
            return

        prefix += self.indent

        max_counts = {
            Folder: self.max_folders_display,
            File: self.max_files_display,
            Error: self.max_errors_display,
        }
        counts = {Folder: 0, File: 0, Error: 0}

        for item in folder.items:
            item_type = type(item)

            count = counts.get(item_type)
            if count is None:
                raise TypeError(f"unexpected item of type {type(item)}")

            if count < max_counts[item_type]:
                counts[item_type] += 1

                if isfile(item):
                    pfx = prefix + self.prefix_file(self, item)
                    print(pfx + self.format_file(item), file=self.buffer)
                elif iserror(item):
                    pfx = prefix + self.prefix_error(self, item)
                    print(pfx + self.format_error(item), file=self.buffer)
                elif isfolder(item):
                    self._format(item, prefix=prefix, depth=depth + 1)


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

    if not isinstance(obj, str):
        obj = str(obj)

    if style is None:
        style = "medium_purple"

    console = Console(record=True, file=StringIO(), style=style)
    console.print(obj)
    console.save_html(filename, inline_styles=True)
    
    if not silent:
        print("Woof woof! 🐶✨")
