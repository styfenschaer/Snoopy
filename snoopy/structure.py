from __future__ import annotations

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
    items: list[File | Folder | Error] = field(default_factory=list)

    @property
    def bytes(self):
        return sum(item.bytes for item in self.items if not iserror(item))

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
    def errors(self):
        return [item for item in self.items if iserror(item)]

    def __post_init__(self):
        self.name = self.path.name
        self.created = get_created(self.path)
        self.last_access = get_last_access(self.path)
        self.last_modified = get_last_modified(self.path)

    def __iadd__(self, item: File | Folder | Error):
        self.items.append(item)
        return self

    def __isub__(self, item: File | Folder | Error):
        self.items.remove(item)
        return self

    def __str__(self):
        return (
            f"Folder({self.path}, "
            f"files=({len(self.files):,d}|{len(self.deep_files):,d}), "
            f"folders={len(self.folders):,d}, "
            f"bytes={self.bytes:,d}, "
            f"created={self.created}, "
            f"accessed={self.last_access}, "
            f"modified={self.last_modified}"
        )


def tree(
    path: Path | str,
    /,
    *,
    filter_folders: Callable[[Folder], bool] = lambda folder: True,
    filter_files: Callable[[File], bool] = lambda file: True,
    filter_errors: Callable[[Error], bool] = lambda error: True,
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
                if filter_folders(subfolder):
                    folder += subfolder
                    tree(
                        item,
                        filter_folders=filter_folders,
                        filter_files=filter_files,
                        verbosity=verbosity,
                        _folder=subfolder,
                    )
            elif item.is_file():
                file = File(item)

                if verbosity >= 2:
                    print(file)

                if filter_files(file):
                    folder += file

    except Exception as exc:
        if raise_on_error:
            raise exc

        error = Error(exc)

        if verbosity >= 1:
            print(error)

        if filter_errors(error):
            folder += error

    if verbosity >= 1:
        print(folder)

    return folder


_FOLDER_PREFIX = "📁 "
_FILE_PREFIX = "📄 "
_ERROR_PREFIX = "🤬 "
_EMOJIS = (_FOLDER_PREFIX, _FILE_PREFIX, _ERROR_PREFIX)


def _pad_lines(s: str, left: int = 1, right: int = 1, symbol: str = " "):
    lines = s.split("\n")
    max_length = max(len(line) for line in lines)
    num_emojis = [sum(line.count(e) for e in _EMOJIS) for line in lines]
    max_emojis = max(num_emojis)
    lenghts = [max_length + (max_emojis - n) for n in num_emojis]
    return "\n".join(
        left * symbol + line.ljust(n) + right * symbol
        for line, n in zip(lines, lenghts)
    )


@dataclass
class Format:
    tree: Folder
    max_depth: int | None = field(default=None, kw_only=True)
    max_files_display: int | None = field(default=None, kw_only=True)
    max_folders_display: int | None = field(default=None, kw_only=True)
    max_errors_display: int | None = field(default=None, kw_only=True)
    sort_files: Callable[[list[File]], list[File]] = field(
        default=lambda files: files, kw_only=True
    )
    sort_folders: Callable[[list[Folder]], list[Folder]] = field(
        default=lambda files: files, kw_only=True
    )
    sort_errors: Callable[[list[Error]], list[Error]] = field(
        default=lambda errors: errors, kw_only=True
    )
    format_file: Callable[[File], str] = field(
        default=lambda file: str(file), kw_only=True
    )
    format_folder: Callable[[Folder], str] = field(
        default=lambda folder: str(folder), kw_only=True
    )
    format_error: Callable[[Error], str] = field(
        default=lambda error: str(error), kw_only=True
    )
    prefix_file: Callable[[Format, File], str] = field(
        default=lambda fmt, file: _FILE_PREFIX, kw_only=True
    )
    prefix_folder: Callable[[Format, Folder], str] = field(
        default=lambda fmt, folder: _FOLDER_PREFIX, kw_only=True
    )
    prefix_error: Callable[[Format, Error], str] = field(
        default=lambda fmt, error: _ERROR_PREFIX, kw_only=True
    )
    display_order: list[File | Folder | Error] = field(
        default_factory=lambda: [Error, Folder, File], kw_only=True
    )
    indent: str = field(default=" │ ", kw_only=True)
    init_prefix: str = field(default="", kw_only=True)

    def __post_init__(self):
        self.buffer = StringIO()
        self.depth = None

    def __str__(self):
        self._format(self.tree, prefix=self.init_prefix, depth=0)
        self.depth = None
        return self.buffer.getvalue()

    def _append(self, text: str):
        print(text, file=self.buffer)

    def _format(self, folder: Folder, prefix: int, depth: int):
        self.depth = depth

        pfx = prefix + self.prefix_folder(folder, depth)
        self._append(pfx + self.format_folder(folder))

        if (self.max_depth is not None) and (depth >= self.max_depth):
            return

        prefix += self.indent

        for kind in self.display_order:
            if kind is Error:
                self._format_error(folder, prefix, depth)
            elif kind is File:
                self._format_file(folder, prefix, depth)
            elif kind is Folder:
                self._format_folder(folder, prefix, depth)
            else:
                raise ValueError(f"{kind} is not a valid display order item")

    def _format_error(self, folder: Folder, prefix: str, depth: int):
        errors = self.sort_errors(folder.errors)
        for item in errors[: self.max_errors_display]:
            pfx = prefix + self.prefix_error(item, depth)
            self._append(pfx + self.format_error(item))

    def _format_file(self, folder: Folder, prefix: str, depth: int):
        files = self.sort_files(folder.files)
        for item in files[: self.max_files_display]:
            pfx = prefix + self.prefix_file(item, depth)
            self._append(pfx + self.format_file(item))

    def _format_folder(self, folder: Folder, prefix: str, depth: int):
        folders = self.sort_folders(folder.folders)
        for item in folders[: self.max_folders_display]:
            self._format(item, prefix=prefix, depth=depth + 1)

    def display(self, rich: bool = False, style: str | None = None):
        if (style is not None) and (not rich):
            warnings.warn("style is ignored when displaying without rich")

        if style is None:
            style = "bold red on white"

        if not rich:
            return print(self)

        if not _rich_installed_:
            warnings.warn("missing package 'rich'; displaying normally")
            return print(self)

        text = _pad_lines(str(self))
        Console(style=style).print(text)


def save_html(
    text: str | Format,
    /,
    *,
    filename: str | Path,
    style: str | None = None,
):
    if not _rich_installed_:
        raise RuntimeError("failed to save due to missing package 'rich'")

    if not isinstance(text, str):
        text = str(text)

    if style is None:
        style = "bold red"

    console = Console(record=True, file=StringIO(), style=style)
    console.print(text)
    console.save_html(filename, inline_styles=True)
