from dataclasses import dataclass
from typing import Literal

B = "B"
KB = "KB"
MB = "MB"
GB = "GB"
TB = "TB"

BYTE = "B"
KILO_BYTE = "KB"
MEGA_BYTE = "MB"
GIGA_BYTE = "GB"
TERA_BYTE = "TB"

_to_bytes = {
    BYTE: 1024**0,
    KILO_BYTE: 1024**1,
    MEGA_BYTE: 1024**2,
    GIGA_BYTE: 1024**3,
    TERA_BYTE: 1024**4,
}


@dataclass
class UnitConverter:
    from_unit: Literal["TB", "GB", "MB", "KB", "B"]
    to_unit: Literal["TB", "GB", "MB", "KB", "B"]

    def __call__(self, value: int | float):
        bytes = value * _to_bytes[self.from_unit]
        return bytes / _to_bytes[self.to_unit]


def convert(
    value: float | int,
    from_unit: Literal["TB", "GB", "MB", "KB", "B"],
    to_unit: Literal["TB", "GB", "MB", "KB", "B"],
):
    return UnitConverter(from_unit, to_unit)(value)