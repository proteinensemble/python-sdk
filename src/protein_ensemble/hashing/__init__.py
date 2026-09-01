# src/protein_ensemble/hashing/__init__.py


from .blake3 import Blake3Hasher
from .exceptions import InvalidContentHashError, UnsupportedHashAlgorithmError
from .operations import (
    compute_content_hash,
    compute_content_hash_file,
    compute_manifest_content_hash,
    format_content_hash,
    parse_content_hash,
    verify_content_hash,
    verify_manifest_content_hash,
    verify_structure_content_hash,
)
from .registry import Hasher, get_hasher, register_hasher

__all__ = [
    "Hasher",
    "Blake3Hasher",
    "InvalidContentHashError",
    "UnsupportedHashAlgorithmError",
    "compute_content_hash",
    "compute_content_hash_file",
    "compute_manifest_content_hash",
    "format_content_hash",
    "parse_content_hash",
    "verify_content_hash",
    "verify_manifest_content_hash",
    "verify_structure_content_hash",
    "get_hasher",
    "register_hasher",
]

register_hasher(Blake3Hasher())
