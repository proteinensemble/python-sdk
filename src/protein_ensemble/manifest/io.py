# src/protein_ensemble/io.py

from __future__ import annotations

import tempfile
from pathlib import Path

import fsspec
from fsspec.implementations.local import LocalFileSystem

from protein_ensemble.shared.models import Structure


def stage_manifest_bundle(uri: str, *, dest_dir: Path | None = None) -> Path:
    fs, remote_path = fsspec.core.url_to_fs(uri)
    remote_dir = str(Path(remote_path).parent)

    if isinstance(fs, LocalFileSystem):
        return Path(remote_dir)

    local_dir = dest_dir if dest_dir is not None else Path(tempfile.mkdtemp(prefix="protein_ensemble_"))
    local_dir.mkdir(parents=True, exist_ok=True)
    fs.get(remote_dir, str(local_dir), recursive=True)
    return local_dir


def resolve_structure_path(structure: Structure, *, manifest_dir: Path) -> Path:
    return manifest_dir / structure.uri
