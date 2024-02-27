from dataclasses import dataclass, field
from typing import Literal

from .core import Error, File, Folder, clone
from .units import Converter


class ItemSize:
    unit: Literal["B", "KB", "MB", "GB", "TB"] = field(default="B")

    def __post_init__(self):
        self.convert = Converter("B", self.unit.upper())

    def __call__(self, obj: Folder | File):
        return f"{obj.name}({self.unit}={self.convert(obj.bytes):.2f})"


@dataclass
class ItemName:
    include_path: bool = field(default=False, kw_only=True)

    def __call__(self, obj: Folder | File):
        return str((obj.name, obj.path)[self.include_path])


def default(obj: Folder | File | Error):
    return str(obj)


def anonymize(obj: Folder | File):
    obj = clone(obj)
    obj.path = hash(obj.path)
    return default(obj)
