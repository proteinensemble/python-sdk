# src/protein_ensemble/manifest/manifest.py

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from protein_ensemble.hashing import compute_content_hash_file, compute_manifest_content_hash, parse_content_hash
from protein_ensemble.manifest.io import resolve_structure_path, stage_manifest_bundle
from protein_ensemble.shared.exceptions import (
    ManifestContentHashMismatchError,
    MemberNotFoundError,
    StructureContentHashMismatchError,
)
from protein_ensemble.shared.models import CapabilitiesRequiredItem, Member, ProteinEnsemble, WeightScheme


class Manifest:
    def __init__(self, protein_ensemble: ProteinEnsemble, *, manifest_dir: Path) -> None:
        self._protein_ensemble = protein_ensemble
        self._manifest_dir = manifest_dir

    @classmethod
    def load(
        cls,
        uri: str,
        *,
        verify: bool = True,
        dest_dir: Path | None = None,
    ) -> Manifest:
        manifest_dir = stage_manifest_bundle(uri, dest_dir=dest_dir)
        manifest_path = manifest_dir / "manifest.json"
        with manifest_path.open("rb") as f:
            raw = json.load(f)
        protein_ensemble = ProteinEnsemble.model_validate(raw)
        if verify:
            expected = compute_manifest_content_hash(protein_ensemble)
            if expected != protein_ensemble.content_hash:
                raise ManifestContentHashMismatchError(expected=expected, actual=protein_ensemble.content_hash)
        return cls(protein_ensemble, manifest_dir=manifest_dir)

    @classmethod
    def create(
        cls,
        *,
        id: str,
        members: dict[str, Member],
        weight_scheme: WeightScheme | None = None,
        capabilities_required: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        manifest_dir: Path,
    ) -> Manifest:
        protein_ensemble = ProteinEnsemble(
            schema_version="0.1.0",
            id=id,
            content_hash="pending:0",
            weight_scheme=weight_scheme,
            capabilities_required=(
                [CapabilitiesRequiredItem(root=item) for item in capabilities_required]
                if capabilities_required is not None
                else None
            ),
            metadata=metadata,
            members=members,
        )
        protein_ensemble.content_hash = compute_manifest_content_hash(protein_ensemble)
        return cls(protein_ensemble, manifest_dir=manifest_dir)

    def save(self, manifest_dir: Path | None = None) -> None:
        target_dir = manifest_dir if manifest_dir is not None else self._manifest_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        payload = self._protein_ensemble.model_dump(mode="json", by_alias=True, exclude_none=True)
        with (target_dir / "manifest.json").open("w") as f:
            json.dump(payload, f, indent=2)

    @property
    def protein_ensemble(self) -> ProteinEnsemble:
        return self._protein_ensemble

    @property
    def manifest_dir(self) -> Path:
        return self._manifest_dir

    @property
    def members(self) -> dict[str, Member]:
        return self._protein_ensemble.members

    def get_member(self, member_id: str) -> Member:
        try:
            return self._protein_ensemble.members[member_id]
        except KeyError:
            raise MemberNotFoundError(member_id) from None

    def structure_path(self, member_id: str) -> Path:
        member = self.get_member(member_id)
        return resolve_structure_path(member.structure, manifest_dir=self._manifest_dir)

    def verify_structure_content(self, member_id: str) -> None:
        member = self.get_member(member_id)
        path = resolve_structure_path(member.structure, manifest_dir=self._manifest_dir)
        algorithm, _ = parse_content_hash(member.structure_hash)
        actual = compute_content_hash_file(path, algorithm=algorithm)
        if actual != member.structure_hash:
            raise StructureContentHashMismatchError(member_id, expected=actual, actual=member.structure_hash)

    def __repr__(self) -> str:
        return f"Manifest(id={self._protein_ensemble.id!r}, members={len(self._protein_ensemble.members)})"
