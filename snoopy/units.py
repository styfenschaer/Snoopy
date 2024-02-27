from dataclasses import dataclass
from functools import partial
from typing import Literal

BYTE = B = "B"
KILO_BYTE = KB = "KB"
MEGA_BYTE = MB = "MB"
GIGA_BYTE = GB = "GB"
TERA_BYTE = TB = "TB"

_to_bytes_lut = {
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

    def __call__(self, value: float):
        bytes = value * _to_bytes_lut[self.from_unit]
        return bytes / _to_bytes_lut[self.to_unit]


def convert(
    value: float,
    from_unit: Literal["B", "KB", "MB", "GB", "TB"],
    to_unit: Literal["B", "KB", "MB", "GB", "TB"],
):
    return Converter(from_unit, to_unit)(value)


to_bytes = partial(convert, to_unit="B")
to_kilo_bytes = partial(convert, to_unit="KB")
to_mega_bytes = partial(convert, to_unit="MB")
to_giga_bytes = partial(convert, to_unit="GB")
to_tera_bytes = partial(convert, to_unit="TB")
