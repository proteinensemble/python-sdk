# src/protein_ensemble/hashing.py

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

import blake3

from protein_ensemble.exceptions import InvalidContentHashError, UnsupportedHashAlgorithmError
from protein_ensemble.models import Model


class Hasher(Protocol):
    algorithm: str

    def hexdigest(self, data: bytes) -> str: ...

    def hexdigest_file(self, path: Path) -> str: ...


class Blake3Hasher:
    algorithm = "blake3"

    def hexdigest(self, data: bytes) -> str:
        return blake3.blake3(data).hexdigest()

    def hexdigest_file(self, path: Path, *, chunk_size: int = 1024 * 1024) -> str:
        hasher = blake3.blake3()
        with path.open("rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()


_HASHERS: dict[str, Hasher] = {
    "blake3": Blake3Hasher(),
}


def register_hasher(hasher: Hasher) -> None:
    _HASHERS[hasher.algorithm] = hasher


def get_hasher(algorithm: str) -> Hasher:
    try:
        return _HASHERS[algorithm]
    except KeyError:
        raise UnsupportedHashAlgorithmError(algorithm) from None


def parse_content_hash(content_hash: str) -> tuple[str, str]:
    algorithm, _, digest = content_hash.partition(":")
    if not algorithm or not digest:
        raise InvalidContentHashError(content_hash)
    return algorithm, digest


def format_content_hash(algorithm: str, digest: str) -> str:
    return f"{algorithm}:{digest}"


def compute_content_hash(data: bytes, *, algorithm: str = "blake3") -> str:
    hasher = get_hasher(algorithm)
    return format_content_hash(algorithm, hasher.hexdigest(data))


def compute_content_hash_file(path: Path, *, algorithm: str = "blake3") -> str:
    hasher = get_hasher(algorithm)
    return format_content_hash(algorithm, hasher.hexdigest_file(path))


def verify_content_hash(data: bytes, content_hash: str) -> bool:
    algorithm, expected_digest = parse_content_hash(content_hash)
    hasher = get_hasher(algorithm)
    return hasher.hexdigest(data) == expected_digest


def compute_manifest_content_hash(model: Model, *, algorithm: str = "blake3") -> str:
    payload = model.model_dump(mode="json", by_alias=True, exclude={"content_hash"}, exclude_none=True)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return compute_content_hash(canonical, algorithm=algorithm)


def verify_manifest_content_hash(model: Model) -> bool:
    expected = compute_manifest_content_hash(model)
    return expected == model.content_hash


def verify_structure_content_hash(path: Path, structure_hash: str) -> bool:
    algorithm, expected_digest = parse_content_hash(structure_hash)
    hasher = get_hasher(algorithm)
    return hasher.hexdigest_file(path) == expected_digest
