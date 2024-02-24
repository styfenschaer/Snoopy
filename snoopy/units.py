from dataclasses import dataclass
from typing import Literal


BYTE = B = "B"
KILO_BYTE = KB = "KB"
MEGA_BYTE = MB = "MB"
GIGA_BYTE = GB = "GB"
TERA_BYTE = TB = "TB"

_to_bytes = {
    BYTE: 1024**0,
    KILO_BYTE: 1024**1,
    MEGA_BYTE: 1024**2,
    GIGA_BYTE: 1024**3,
    TERA_BYTE: 1024**4,
}


@dataclass
class Converter:
    from_unit: Literal["B", "KB", "MB", "GB", "TB"]
    to_unit: Literal["B", "KB", "MB", "GB", "TB"]

    def __call__(self, value: int | float):
        bytes = value * _to_bytes[self.from_unit]
        return bytes / _to_bytes[self.to_unit]


def convert(
    value: float | int,
    from_unit: Literal["B", "KB", "MB", "GB", "TB"],
    to_unit: Literal["B", "KB", "MB", "GB", "TB"],
):
    return Converter(from_unit, to_unit)(value)
