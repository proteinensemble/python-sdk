# src/protein_ensemble/cli/cli.py

from __future__ import annotations

import logging
import shutil
import sys
from pathlib import Path

import click

from protein_ensemble.hashing import compute_content_hash_file
from protein_ensemble.manifest.manifest_builder import ManifestBuilder
from protein_ensemble.shared.models import Member, Structure

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

DEFAULT_MEMBERS_SUBDIR = "members"
DEFAULT_STRUCTURE_GLOB = "*"
DEFAULT_HASH_ALGORITHM = "blake3"


def sync_structure(source_path: Path, dest_path: Path, source_hash: str, hash_algorithm: str) -> None:
    if dest_path.is_file():
        dest_hash = compute_content_hash_file(dest_path, algorithm=hash_algorithm)
        if dest_hash == source_hash:
            logger.info("unchanged, skipping copy: %s", source_path.name)
            return
        logger.info("changed, re-copying: %s", source_path.name)
    shutil.copyfile(source_path, dest_path)


@click.command(help="Generate a Protein Ensemble manifest bundle from a directory of structure files.")
@click.option(
    "--input",
    "input_path",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Directory containing one structure file per ensemble member.",
)
@click.option(
    "--output",
    "output_path",
    type=click.Path(path_type=Path),
    required=True,
    help="Output bundle directory (will contain manifest.json and members/).",
)
@click.option(
    "--id",
    "ensemble_id",
    type=str,
    required=True,
    help="Identifier for the ensemble.",
)
@click.option(
    "--members",
    type=str,
    default=DEFAULT_MEMBERS_SUBDIR,
    show_default=True,
    help="Name of the subdirectory under --out that structure files are copied into.",
)
@click.option(
    "--hash-algorithm",
    type=str,
    default=DEFAULT_HASH_ALGORITHM,
    show_default=True,
    help="Content hash algorithm to use for structureHash (must be registered in hashing.py).",
)
@click.option(
    "--structure-glob",
    type=str,
    default=DEFAULT_STRUCTURE_GLOB,
    show_default=True,
    help="Glob pattern (relative to --structures-dir) selecting structure files.",
)
def generate_manifest(
    input_path: Path,
    output_path: Path,
    ensemble_id: str,
    members: str,
    hash_algorithm: str,
    structure_glob: str,
) -> None:
    structure_paths = sorted(p for p in input_path.glob(structure_glob) if p.is_file())
    if not structure_paths:
        raise click.ClickException(f"no files matching {structure_glob!r} found under {input_path}")

    members_dir = output_path / members
    members_dir.mkdir(parents=True, exist_ok=True)

    builder = ManifestBuilder(id=ensemble_id)

    for source_path in structure_paths:
        member_id = source_path.stem
        dest_path = members_dir / source_path.name

        source_hash = compute_content_hash_file(source_path, algorithm=hash_algorithm)
        sync_structure(source_path, dest_path, source_hash, hash_algorithm)

        member = Member(
            structure=Structure(uri=f"{members}/{source_path.name}"),
            structure_hash=source_hash,
        )
        builder.add_member(member_id, member)
        logger.info("added member: %s (%s)", member_id, source_path.name)

    manifest = builder.build(manifest_dir=output_path)
    manifest.save()
    logger.info("wrote manifest bundle: %s (%d members)", output_path, len(structure_paths))
