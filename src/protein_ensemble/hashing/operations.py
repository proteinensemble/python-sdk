# src/protein_ensemble/hashing/operations.py

import json
from pathlib import Path

from protein_ensemble.shared.models import ProteinEnsemble

from .exceptions import InvalidContentHashError
from .registry import get_hasher


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


def compute_manifest_content_hash(protein_ensemble: ProteinEnsemble, *, algorithm: str = "blake3") -> str:
    payload = protein_ensemble.model_dump(mode="json", by_alias=True, exclude={"content_hash"}, exclude_none=True)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return compute_content_hash(canonical, algorithm=algorithm)


def verify_manifest_content_hash(protein_ensemble: ProteinEnsemble) -> bool:
    expected = compute_manifest_content_hash(protein_ensemble)
    return expected == protein_ensemble.content_hash


def verify_structure_content_hash(path: Path, structure_hash: str) -> bool:
    algorithm, expected_digest = parse_content_hash(structure_hash)
    hasher = get_hasher(algorithm)
    return hasher.hexdigest_file(path) == expected_digest
