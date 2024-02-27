from __future__ import annotations

import copy
import os
import sys
import time
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Callable, Literal

from .terminal import Colors, Commands

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


# fmt: off
_PROG_BEGIN = Commands.MOVE_UP * 2
_PROG_ITER = "".join((
    Commands.MOVE_DOWN * 2,
    "\n",
    Colors.BLUE,
    "Elapsed [sec]: {:.1f} | ",
    Colors.GREEN,
    "Folders: {:,d} | ",
    "Files: {:,d} | ",
    Colors.RED,
    "Errors: {:,d}",
    Colors.DEFAULT,
    Commands.MOVE_UP,
    Commands.CLEAR_LINE,
    Colors.DEFAULT,
    r"{}",
))
_PROG_END = "".join((
    Commands.MOVE_DOWN,
    "\n",
))
# fmt: on


@dataclass
class Dog:
    name: str = field(default="Snoopy")
    ignore_folder: Callable[[Folder], bool] = field(
        default=lambda folder: False, kw_only=True
    )
    ignore_file: Callable[[File], bool] = field(
        default=lambda file: False, kw_only=True
    )
    ignore_error: Callable[[Error], bool] = field(
        default=lambda error: False, kw_only=True
    )
    raise_on_error: bool = field(default=True, kw_only=True)
    verbosity: Literal[0, 1, 2] = field(default=0, kw_only=True)

    def bark(self):
        print("Woof woof! 🐶")

    def snoop(self, path: Path | str | None = None):
        if path is None:
            path = Path(os.getcwd())
        elif not isinstance(path, Path):
            path = Path(path)

        self.folder_count = 0
        self.file_count = 0
        self.error_count = 0

        if self.verbosity >= 1:
            sys.stdout.write(_PROG_BEGIN)

        self.tic = time.time()

        tree = self._snoop(path, Folder(path))

        if self.verbosity >= 1:
            sys.stdout.write(_PROG_END)

        return tree

    def _display(self, item: Error | File | Folder):
        msg = _PROG_ITER.format(
            time.time() - self.tic,
            self.folder_count,
            self.file_count,
            self.error_count,
            item,
        )
        sys.stdout.write(msg)

    def _snoop(self, path: Path, folder: Folder):
        if not (path.exists() and path.is_dir()):
            raise ValueError("path must be an existing directory")

        self.folder_count += 1

        try:
            for item in path.iterdir():
                if item.is_dir():
                    subfolder = Folder(item)
                    if not self.ignore_folder(subfolder):
                        folder.items.append(subfolder)
                        self._snoop(item, subfolder)

                elif item.is_file():
                    self.file_count += 1

                    file = File(item)
                    if self.verbosity >= 2:
                        self._display(file.path)

                    if not self.ignore_file(file):
                        folder.items.append(file)

        except Exception as exc:
            self.error_count += 1

            if self.raise_on_error:
                raise exc

            error = Error(exc)
            if self.verbosity >= 1:
                self._display(error)

            if not self.ignore_error(error):
                folder.items.append(error)

        if self.verbosity >= 1:
            self._display(folder.path)

        return folder


def snoop(
    path: Path | str | None = None,
    *,
    ignore_folder: Callable[[Folder], bool] = lambda folder: False,
    ignore_file: Callable[[File], bool] = lambda file: False,
    ignore_error: Callable[[Error], bool] = lambda error: False,
    raise_on_error: bool = True,
    verbosity: Literal[0, 1, 2] = 0,
):
    return Dog(
        ignore_folder=ignore_folder,
        ignore_file=ignore_file,
        ignore_error=ignore_error,
        raise_on_error=raise_on_error,
        verbosity=verbosity,
    ).snoop(path)


@dataclass
class Transformer:
    def __call__(self, tree: Folder, *, inplace: bool = True):
        if not inplace:
            tree = clone(tree)

        self.depth = 0

        tree = self.visit_folder(tree)
        if tree is None:
            return

        return self._visit(tree)

    def visit_folder(self, folder: Folder) -> Folder | None:
        return folder

    def visit_file(self, file: File) -> File | None:
        return file

    def visit_error(self, error: Error) -> Error | None:
        return error

    def visit_item(self, item: Folder | File | Error):
        if isfolder(item):
            return self.visit_folder(item)
        if isfile(item):
            return self.visit_file(item)
        if iserror(item):
            return self.visit_error(item)
        raise TypeError(f"unexpected item of type {type(item)}")

    def _visit(self, folder: Folder) -> Folder | None:
        self.depth += 1

        new_items = []
        for item in folder.items:
            item = self.visit_item(item)

            if item is None:
                continue

            if isfolder(item):
                item = self._visit(item)

            new_items.append(item)

        folder.items.clear()
        folder.items.extend(new_items)

        self.depth -= 1
        return folder


def traverse(tree: Folder, reverse: bool = False):
    for item in tree.items:
        if not reverse:
            yield item
        if isfolder(item):
            yield from traverse(item, reverse=reverse)
        if reverse:
            yield item


_FOLDER_PREFIX = "📁 "
_FILE_PREFIX = "📄 "
_ERROR_PREFIX = "🤬 "
_REM_ITEMS_TMPL = "✂️  [Folders: {:,d} | Files: {:,d} | Errors: {:,d}]"


@dataclass
class Formatter:
    tree: Folder
    max_depth: int = field(default=float("inf"), kw_only=True)
    max_files_display: int = field(default=float("inf"), kw_only=True)
    max_folders_display: int = field(default=float("inf"), kw_only=True)
    max_errors_display: int = field(default=float("inf"), kw_only=True)
    max_items_display: int = field(default=float("inf"), kw_only=True)
    format_file: Callable[[File], str] = field(
        default=lambda file: str(file), kw_only=True
    )
    format_folder: Callable[[Folder], str] = field(
        default=lambda folder: str(folder), kw_only=True
    )
    format_error: Callable[[Error], str] = field(
        default=lambda error: str(error), kw_only=True
    )
    prefix_file: Callable[[Formatter, File], str] = field(
        default=lambda fmt, file: _FILE_PREFIX, kw_only=True
    )
    prefix_folder: Callable[[Formatter, Folder], str] = field(
        default=lambda fmt, folder: _FOLDER_PREFIX, kw_only=True
    )
    prefix_error: Callable[[Formatter, Error], str] = field(
        default=lambda fmt, error: _ERROR_PREFIX, kw_only=True
    )
    indent: str = field(default=" │ ", kw_only=True)
    init_prefix: str = field(default="", kw_only=True)
    display_hidden: bool = field(default=False, kw_only=True)
    format_remaining: Callable[[tuple[int, int, int]], str] = field(
        default=lambda n0, n1, n2: _REM_ITEMS_TMPL.format(n0, n1, n2),
        kw_only=True,
    )
    display_remaining: bool = field(default=True, kw_only=True)

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

        max_count_table = {
            Folder: self.max_folders_display,
            File: self.max_files_display,
            Error: self.max_errors_display,
        }
        count_table = {Folder: 0, File: 0, Error: 0}

        for item_count, item in enumerate(folder.items):
            item_type = type(item)
            if item_type not in max_count_table:
                raise TypeError(f"unexpected item of type {type(item)}")

            if count_table[item_type] >= max_count_table[item_type]:
                continue

            if item_count >= self.max_items_display:
                break

            if item.hidden and (not self.display_hidden):
                continue

            count_table[item_type] += 1

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

        if self.display_remaining:
            remaining = [
                len(folder.folders) - count_table[Folder],
                len(folder.files) - count_table[File],
                len(folder.errors) - count_table[Error],
            ]
            if not self.display_hidden:
                remaining[0] -= sum(1 for i in folder.folders if i.hidden)
                remaining[1] -= sum(1 for i in folder.files if i.hidden)
                remaining[2] -= sum(1 for i in folder.errors if i.hidden)

            if any(rem > 0 for rem in remaining):
                self._join_append(
                    self.init_prefix + self.depth * self.indent,
                    self.format_remaining(*remaining),
                )

        self.depth -= 1


def display(obj: Formatter | str, *, style: str | None = None):
    if not _rich_installed_:
        warnings.warn("missing package 'rich'; displaying normally")
        return print(obj)

    if style is None:
        style = "bold medium_purple"

    Console(style=style).print(str(obj))


def save_html(
    obj: str | Formatter,
    filename: str | Path,
    *,
    style: str | None = None,
):
    if not _rich_installed_:
        raise RuntimeError("failed to save due to missing package 'rich'")

    if style is None:
        style = "medium_purple"

    console = Console(record=True, file=StringIO(), style=style)
    console.print(str(obj))
    console.save_html(filename, inline_styles=True)


def save_txt(obj: str | Formatter, filename: str | Path):
    with open(filename, mode="w", encoding="utf-8") as file:
        file.write(str(obj))


def snapshot(
    obj: str | Formatter,
    filename: str | Path,
    *,
    style: str | None = None,
    silent: bool = True,
):
    if not isinstance(filename, Path):
        filename = Path(filename)

    if filename.suffix == ".html":
        save_html(obj, filename, style=style)
    else:
        save_txt(obj, filename)

    if not silent:
        print("Woof woof! 🐶✨📸")
