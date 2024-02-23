from dataclasses import dataclass, field
from typing import Literal

from .core import Error, File, Folder
from .units import Converter


@dataclass
class SizeOnly:
    unit: Literal["B", "KB", "MB", "GB", "TB"] = field(
        default="B",
        kw_only=True,
    )

    def __post_init__(self):
        self.convert = Converter("B", self.unit.upper())

    def __call__(self, obj: Folder | File):
        return f"{obj.name}({self.unit}={self.convert(obj.bytes):.2f})"


@dataclass
class NumFilesOnly:
    deep: bool = field(default=False, kw_only=True)

    def __call__(self, folder: Folder):
        files = (folder.files, folder.deep_files)[self.deep]
        return f"{folder.name}(files={len(files):,d})"


@dataclass
class NameOnly:
    include_path: bool = field(default=False, kw_only=True)

    def __call__(self, obj: Folder | File):
        return str((obj.name, obj.path)[self.include_path])


def default(obj: Folder | File | Error):
    return str(obj)
