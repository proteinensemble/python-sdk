# src/protein_ensemble/accessors/__init__.py

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from protein_ensemble.shared.exceptions import UnsupportedAccessorFormatError
from protein_ensemble.shared.models import Member


class Accessor(Protocol):
    def __call__(self, member: Member, structure_path: Path, **kwargs: Any) -> Any: ...


_ACCESSORS: dict[str, Accessor] = {}


def register_accessor(format: str, accessor: Accessor) -> None:
    _ACCESSORS[format] = accessor


def get_accessor(format: str) -> Accessor:
    try:
        return _ACCESSORS[format]
    except KeyError:
        raise UnsupportedAccessorFormatError(format, sorted(_ACCESSORS)) from None


def available_formats() -> list[str]:
    return sorted(_ACCESSORS)
