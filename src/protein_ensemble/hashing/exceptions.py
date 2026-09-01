# src/protein_ensemble/hashing/exceptions.py

from protein_ensemble.shared.exceptions import ProteinEnsembleError


class UnsupportedHashAlgorithmError(ProteinEnsembleError):
    def __init__(self, algorithm: str) -> None:
        self.algorithm = algorithm
        super().__init__(f"no hasher registered for algorithm {algorithm!r}")


class InvalidContentHashError(ProteinEnsembleError):
    def __init__(self, content_hash: str) -> None:
        self.content_hash = content_hash
        super().__init__(f"content hash {content_hash!r} does not match 'algorithm:hexdigest' format")
