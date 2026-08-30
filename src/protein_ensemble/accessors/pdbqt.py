from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from protein_ensemble.accessors import register_accessor
from protein_ensemble.exceptions import MissingDependencyError
from protein_ensemble.models import Member

_TEMPLATE_FAILURE_PREFIX = "- Template matching failed for: "
_DEFAULT_KEEP_HETATMS = {"ZN", "MG", "CA", "FE", "HEM"}


class PdbqtPrepError(Exception):
    pass


class ResidueTemplateError(PdbqtPrepError):
    def __init__(self, failed_residues: list[str]) -> None:
        self.failed_residues = failed_residues
        super().__init__(
            f"Residue template matching failed: {', '.join(failed_residues)}. "
            "Pass allow_bad_residues=True to drop these residues instead of raising."
        )


class ReceptorPrepSubprocessError(PdbqtPrepError):
    def __init__(self, returncode: int, stderr: str) -> None:
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(f"mk_prepare_receptor failed (exit code {returncode}):\n{stderr}")


def member_to_pdbqt(
    member: Member,
    structure_path: Path,
    *,
    default_altloc: str = "A",
    allow_bad_residues: bool = False,
    keep_hetatms: set[str] | None = None,
    **kwargs: object,
) -> str:
    try:
        import gemmi  # noqa: F401
    except ImportError as e:
        raise MissingDependencyError("pdbqt", "gemmi") from e

    try:
        import meeko  # noqa: F401
    except ImportError as e:
        raise MissingDependencyError("pdbqt", "meeko") from e

    with tempfile.TemporaryDirectory(prefix="protein_ensemble_pdbqt_") as tmp:
        tmp_dir = Path(tmp)
        prepped_pdb_path = tmp_dir / "prepped.pdb"
        output_stem = tmp_dir / "receptor"
        expected_pdbqt = output_stem.with_suffix(".pdbqt")

        _clean_structure(
            structure_path,
            prepped_pdb_path,
            keep_hetatms=keep_hetatms or _DEFAULT_KEEP_HETATMS,
        )

        command = [
            sys.executable,
            "-m",
            "meeko.cli.mk_prepare_receptor",
            "-i",
            str(prepped_pdb_path),
            "-o",
            str(output_stem),
            "-p",
            "--default_altloc",
            default_altloc,
        ]
        if allow_bad_residues:
            command += ["--allow_bad_res"]

        completed = subprocess.run(command, capture_output=True, text=True)

        dropped_residues = _parse_dropped_residues(completed.stderr) or _parse_dropped_residues(completed.stdout)

        if completed.returncode != 0:
            if dropped_residues and not allow_bad_residues:
                raise ResidueTemplateError(dropped_residues)
            raise ReceptorPrepSubprocessError(completed.returncode, completed.stderr or completed.stdout)

        if not expected_pdbqt.is_file():
            raise ReceptorPrepSubprocessError(
                completed.returncode,
                f"mk_prepare_receptor exited 0 but expected output file {expected_pdbqt} was not created.",
            )

        return expected_pdbqt.read_text()


def _clean_structure(input_cif_path: Path, output_pdb_path: Path, *, keep_hetatms: set[str]) -> None:
    import gemmi

    cif_doc = gemmi.cif.read_file(str(input_cif_path))
    structure = gemmi.make_structure_from_block(cif_doc.sole_block())
    structure.remove_waters()

    for model in structure:
        for chain in model:
            for i in reversed(range(len(chain))):
                residue = chain[i]
                if residue.entity_type != gemmi.EntityType.Polymer and residue.name not in keep_hetatms:
                    del chain[i]

    structure.write_pdb(str(output_pdb_path))


def _parse_dropped_residues(stderr: str) -> list[str]:
    for line in stderr.splitlines():
        line = line.strip()
        if line.startswith(_TEMPLATE_FAILURE_PREFIX):
            remainder = line[len(_TEMPLATE_FAILURE_PREFIX) :]
            list_text = remainder[: remainder.index("]") + 1]
            return [token.strip().strip("'\"") for token in list_text.strip("[]").split(",") if token.strip()]
    return []


register_accessor("pdbqt", member_to_pdbqt)
