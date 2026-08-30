# src/protein_ensemble/manifest_builder.py

from __future__ import annotations

from pathlib import Path
from typing import Any

from .exceptions import DuplicateMemberError, EmptyManifestError
from .manifest import Manifest
from .models import Member, WeightScheme


class ManifestBuilder:
    def __init__(
        self,
        *,
        id: str,
        weight_scheme: WeightScheme | None = None,
        capabilities_required: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._id = id
        self._weight_scheme = weight_scheme
        self._capabilities_required = capabilities_required
        self._metadata = metadata
        self._members: dict[str, Member] = {}

    def add_member(self, member_id: str, member: Member) -> ManifestBuilder:
        if member_id in self._members:
            raise DuplicateMemberError(member_id)
        self._members[member_id] = member
        return self

    def build(self, *, manifest_dir: Path) -> Manifest:
        if not self._members:
            raise EmptyManifestError()
        return Manifest.create(
            id=self._id,
            members=self._members,
            weight_scheme=self._weight_scheme,
            capabilities_required=self._capabilities_required,
            metadata=self._metadata,
            manifest_dir=manifest_dir,
        )

    def __repr__(self) -> str:
        return f"ManifestBuilder(id={self._id!r}, members={len(self._members)})"
