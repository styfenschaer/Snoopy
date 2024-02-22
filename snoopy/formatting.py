from dataclasses import dataclass, field
from typing import Literal

from .structure import File, Folder

_to_bytes = {
    "B": 1024**0,
    "KB": 1024**1,
    "MB": 1024**2,
    "GB": 1024**3,
    "TB": 1024**4,
}


@dataclass
class UnitConverter:
    from_unit: Literal["TB", "GB", "MB", "KB", "B"]
    to_unit: Literal["TB", "GB", "MB", "KB", "B"]

    def __call__(self, value: int | float):
        bytes = value * _to_bytes[self.from_unit]
        return bytes / _to_bytes[self.to_unit]


@dataclass
class SizeOnly:
    unit: Literal["TB", "GB", "MB", "KB", "B"] = field(default="B", kw_only=True)

    def __post_init__(self):
        self.convert = UnitConverter("B", self.unit.upper())

    def __call__(self, folder: Folder | File):
        return f"{folder.name}({self.unit}={self.convert(folder.bytes):.2f})"


@dataclass
class NumFilesOnly:
    deep: bool = field(default=False, kw_only=True)

    def __call__(self, folder: Folder):
        files = (folder.files, folder.deep_files)[self.deep]
        return f"{folder.name}(files={len(files):,d})"


@dataclass
class NameOnly:
    include_path: bool = field(default=False, kw_only=True)

    def __call__(self, folder: Folder | File):
        return str((folder.name, folder.path)[self.include_path])
