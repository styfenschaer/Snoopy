from dataclasses import dataclass, field
from operator import attrgetter

from .structure import File, Folder


@dataclass
class ByLastModified:
    reverse: bool = field(default=True, kw_only=True)

    def __call__(self, arg: list[File] | list[Folder]):
        return sorted(arg, key=lambda x: x.last_modified, reverse=self.reverse)


@dataclass
class ByLastAccess:
    reverse: bool = field(default=True, kw_only=True)

    def __call__(self, arg: list[File] | list[Folder]):
        return sorted(arg, key=lambda x: x.last_access, reverse=self.reverse)


@dataclass
class ByCreated:
    reverse: bool = field(default=True, kw_only=True)

    def __call__(self, arg: list[File] | list[Folder]):
        return sorted(arg, key=lambda x: x.created, reverse=self.reverse)


@dataclass
class BySize:
    reverse: bool = field(default=True, kw_only=True)

    def __call__(self, arg: list[File] | list[Folder]):
        return sorted(arg, key=lambda x: x.bytes, reverse=self.reverse)


@dataclass
class ByNumFiles:
    deep: bool = field(default=False, kw_only=True)
    reverse: bool = field(default=True, kw_only=True)

    def __post_init__(self):
        self._get = attrgetter("deep_files" if self.deep else "files")

    def __call__(self, arg: list[Folder]):
        return sorted(arg, key=lambda x: self._get(x), reverse=self.reverse)
