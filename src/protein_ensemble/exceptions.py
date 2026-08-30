# src/protein_ensemble/shared/exceptions.py


class ProteinEnsembleError(Exception):
    pass


class MemberNotFoundError(ProteinEnsembleError):
    def __init__(self, member_id: str) -> None:
        self.member_id = member_id
        super().__init__(f"No member with id {member_id!r} in manifest")


class DuplicateMemberError(ProteinEnsembleError):
    def __init__(self, member_id: str) -> None:
        self.member_id = member_id
        super().__init__(f"Member with id {member_id!r} already added to this builder")


class EmptyManifestError(ProteinEnsembleError):
    def __init__(self) -> None:
        super().__init__("cannot finalize a manifest with no members")


class UnsupportedHashAlgorithmError(ProteinEnsembleError):
    def __init__(self, algorithm: str) -> None:
        self.algorithm = algorithm
        super().__init__(f"no hasher registered for algorithm {algorithm!r}")


class InvalidContentHashError(ProteinEnsembleError):
    def __init__(self, content_hash: str) -> None:
        self.content_hash = content_hash
        super().__init__(f"content hash {content_hash!r} does not match 'algorithm:hexdigest' format")


class ManifestContentHashMismatchError(ProteinEnsembleError):
    def __init__(self, expected: str, actual: str) -> None:
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"manifest content hash mismatch: computed {expected!r} but manifest declares {actual!r}. "
            "The manifest file may have been modified or corrupted since it was created."
        )


class StructureContentHashMismatchError(ProteinEnsembleError):
    def __init__(self, member_id: str, expected: str, actual: str) -> None:
        self.member_id = member_id
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"structure content hash mismatch for member {member_id!r}: "
            f"computed {expected!r} but member declares {actual!r}. "
            "The referenced structure content may have changed since this member was added."
        )


class MissingDependencyError(ProteinEnsembleError):
    def __init__(self, feature: str, package: str) -> None:
        self.feature = feature
        self.package = package
        super().__init__(
            f"The {feature!r} accessor requires the dependency {package!r}. "
            f"Install it with: pip install protein_ensemble[{feature}]"
        )


class UnsupportedAccessorFormatError(ProteinEnsembleError):
    def __init__(self, format: str, available: list[str]) -> None:
        self.format = format
        self.available = available
        super().__init__(
            f"no accessor registered for format {format!r}. "
            f"Available: {available!r}. "
            "The accessor's optional dependency may not be installed, or the module "
            "hasn't been imported yet (accessors self-register on import)."
        )
