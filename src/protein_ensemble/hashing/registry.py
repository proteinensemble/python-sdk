# src/protein_ensemble/hashing/registry.py

from pathlib import Path
from typing import Protocol

from .exceptions import UnsupportedHashAlgorithmError


class Hasher(Protocol):
    algorithm: str

    def hexdigest(self, data: bytes) -> str: ...
    def hexdigest_file(self, path: Path) -> str: ...


_HASHERS: dict[str, Hasher] = {}


def register_hasher(hasher: Hasher) -> None:
    _HASHERS[hasher.algorithm] = hasher


def get_hasher(algorithm: str) -> Hasher:
    try:
        return _HASHERS[algorithm]
    except KeyError:
        raise UnsupportedHashAlgorithmError(algorithm) from None
