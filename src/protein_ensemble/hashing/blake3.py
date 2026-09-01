# src/protein_ensemble/hashing/blake3.py

from __future__ import annotations

from pathlib import Path

import blake3


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
