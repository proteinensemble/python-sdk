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


@click.command(help="Generate a PCE manifest bundle from a directory of structure files.")
@click.option(
    "--structures-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Directory containing one structure file per ensemble member.",
)
@click.option(
    "--out",
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
    "--structure-glob",
    type=str,
    default=DEFAULT_STRUCTURE_GLOB,
    show_default=True,
    help="Glob pattern (relative to --structures-dir) selecting structure files.",
)
@click.option(
    "--members-subdir",
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
def generate_manifest(
    structures_dir: Path,
    out: Path,
    ensemble_id: str,
    structure_glob: str,
    members_subdir: str,
    hash_algorithm: str,
) -> None:
    structure_paths = sorted(p for p in structures_dir.glob(structure_glob) if p.is_file())
    if not structure_paths:
        raise click.ClickException(f"no files matching {structure_glob!r} found under {structures_dir}")

    members_dir = out / members_subdir
    members_dir.mkdir(parents=True, exist_ok=True)

    builder = ManifestBuilder(id=ensemble_id)

    for source_path in structure_paths:
        member_id = source_path.stem
        dest_path = members_dir / source_path.name

        source_hash = compute_content_hash_file(source_path, algorithm=hash_algorithm)

        if dest_path.is_file():
            dest_hash = compute_content_hash_file(dest_path, algorithm=hash_algorithm)
            if dest_hash == source_hash:
                logger.info("unchanged, skipping copy: %s", source_path.name)
            else:
                logger.info("changed, re-copying: %s", source_path.name)
                shutil.copy2(source_path, dest_path)
        else:
            shutil.copy2(source_path, dest_path)

        member = Member(
            structure=Structure(uri=f"{members_subdir}/{source_path.name}"),
            structure_hash=source_hash,
        )
        builder.add_member(member_id, member)
        logger.info("added member: %s (%s)", member_id, source_path.name)

    manifest = builder.build(manifest_dir=out)
    manifest.save()
    logger.info("wrote manifest bundle: %s (%d members)", out, len(structure_paths))


if __name__ == "__main__":
    generate_manifest()
