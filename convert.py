#!/usr/bin/env python3
"""Convert Prusa CORE One filament presets to standard and INDX HF variants."""
from __future__ import annotations

import argparse
import re
import shutil
import stat
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

STANDARD_MODELS = (
    "COREONE",
    "COREONEOAK",
    "COREONEMMU3",
    "COREONEL",
    "COREONELMMU3",
)
INDX_MODELS = (
    "COREONE_INDX4T",
    "COREONE_INDX8T",
    "COREONEL_INDX4T",
    "COREONEL_INDX8T",
)


def compatibility_for(models: tuple[str, ...]) -> str:
    return (
        "printer_model=~/(" + "|".join(models) + ")/ "
        "and nozzle_diameter[0]==0.4 and nozzle_high_flow[0]"
    )


@dataclass(frozen=True)
class ProfileVariant:
    key: str
    label: str
    parent: str
    models: tuple[str, ...]

    @property
    def compatibility(self) -> str:
        return compatibility_for(self.models)


STANDARD = ProfileVariant("standard", "HF0.4", "@COREONE HF0.4", STANDARD_MODELS)
INDX = ProfileVariant("indx", "INDX HF0.4", "@COREONEINDX HF0.4", INDX_MODELS)
PROFILE_VARIANTS = (STANDARD, INDX)
STANDARD_COMPATIBILITY = STANDARD.compatibility
INDX_COMPATIBILITY = INDX.compatibility
# Kept as the public default for callers that previously converted INDX only.
COMPATIBILITY = INDX_COMPATIBILITY


def convert_inherits(value: str, variant: ProfileVariant = INDX) -> str:
    return re.sub(
        r"@COREONE(?:INDX)?(?:\s+HF0\.4)?",
        variant.parent,
        value.strip(),
    )


def convert_profile(text: str, variant: ProfileVariant = INDX) -> str:
    lines = text.splitlines()
    converted: list[str] = []
    saw_compatibility = False

    for line in lines:
        if re.match(r"^inherits\s*=", line):
            key, value = line.split("=", 1)
            line = f"{key.strip()} = {convert_inherits(value, variant)}"
        elif re.match(r"^compatible_printers_condition\s*=", line):
            line = f"compatible_printers_condition = {variant.compatibility}"
            saw_compatibility = True
        elif re.match(r"^compatible_printers_condition_cummulative\s*=", line):
            line = (
                "compatible_printers_condition_cummulative = "
                f"{variant.compatibility}"
            )
        elif re.match(r"^filament_settings_id\s*=", line):
            key, value = line.split("=", 1)
            value = value.strip()
            value = re.sub(
                r"\s*@Prusa\s+Core\s+One(?:\s+(?:INDX\s+)?HF0\.4)?$",
                f" @Prusa CORE One {variant.label}",
                value,
                flags=re.IGNORECASE,
            )
            line = f"{key.strip()} = {value}"
        converted.append(line)

    if not saw_compatibility:
        converted.append(
            f"compatible_printers_condition = {variant.compatibility}"
        )

    return "\n".join(converted).rstrip() + "\n"


def converted_filename(source: Path, variant: ProfileVariant) -> str:
    stem = re.sub(
        r"\s*@Prusa\s+Core\s+One$",
        f" @Prusa CORE One {variant.label}",
        source.stem,
        flags=re.IGNORECASE,
    )
    if stem == source.stem:
        stem = f"{stem} @Prusa CORE One {variant.label}"
    return f"{stem}.ini"


def collect_ini_files(source: Path, temp_dir: Path) -> list[Path]:
    if source.is_dir():
        return sorted(source.rglob("*.ini"))
    if source.suffix.lower() == ".zip":
        with zipfile.ZipFile(source) as archive:
            extracted: set[Path] = set()
            for member in archive.infolist():
                member_path = PurePosixPath(member.filename)
                if (
                    not member.filename
                    or member_path.is_absolute()
                    or ".." in member_path.parts
                    or "\\" in member.filename
                    or stat.S_ISLNK(member.external_attr >> 16)
                ):
                    raise ValueError(f"Unsafe ZIP entry: {member.filename!r}")

                destination = temp_dir.joinpath(*member_path.parts)
                if destination in extracted:
                    raise ValueError(f"Duplicate ZIP entry: {member.filename!r}")
                extracted.add(destination)

                if member.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source_file, destination.open("wb") as target:
                    shutil.copyfileobj(source_file, target)
        return sorted(temp_dir.rglob("*.ini"))
    if source.suffix.lower() == ".ini":
        return [source]
    raise ValueError("Source must be an .ini file, a directory, or a ZIP archive")


def build_bundle(files: list[Path], destination: Path) -> None:
    # Config bundles identify each preset with a typed INI section.
    chunks: list[str] = []
    for profile in files:
        text = profile.read_text(encoding="utf-8-sig")
        match = re.search(r"^filament_settings_id\s*=\s*(.+?)\s*$", text, re.MULTILINE)
        if not match:
            raise ValueError(f"Profile has no filament_settings_id: {profile}")
        chunks.append(f"[filament:{match.group(1)}]\n{text.rstrip()}")
    destination.write_text("\n\n".join(chunks) + "\n", encoding="utf-8")


def reject_duplicate_output_names(files: list[Path]) -> None:
    names: dict[str, Path] = {}
    for profile in files:
        normalized = profile.name.casefold()
        if normalized in names:
            raise ValueError(
                f"Duplicate output filename: {profile.name!r} "
                f"({names[normalized]} and {profile})"
            )
        names[normalized] = profile


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source",
        nargs="?",
        default="source",
        help="Source .ini, directory, or ZIP (default: source)",
    )
    parser.add_argument("--output", default="output", help="Output directory")
    args = parser.parse_args()

    source = Path(args.source)
    output = Path(args.output)
    individual = output / "individual"
    bundle_dir = output / "bundle"
    release_dir = output / "release"

    if not source.exists():
        print(f"Source not found: {source}", file=sys.stderr)
        return 2

    if output.exists():
        shutil.rmtree(output)
    individual.mkdir(parents=True)
    bundle_dir.mkdir(parents=True)
    release_dir.mkdir(parents=True)

    with tempfile.TemporaryDirectory() as tmp:
        source_files = collect_ini_files(source, Path(tmp))
        if not source_files:
            print("No .ini files found", file=sys.stderr)
            return 3
        reject_duplicate_output_names(source_files)

        converted_files: list[Path] = []
        for profile in source_files:
            source_text = profile.read_text(encoding="utf-8-sig")
            for variant in PROFILE_VARIANTS:
                converted = convert_profile(source_text, variant)
                destination = individual / converted_filename(profile, variant)
                destination.write_text(converted, encoding="utf-8")
                converted_files.append(destination)

        reject_duplicate_output_names(converted_files)

    bundle = bundle_dir / "INDX-Filament-Profiles-HF0.4-config-bundle.ini"
    build_bundle(converted_files, bundle)

    archive_path = release_dir / "INDX-Filament-Profiles-HF0.4.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for profile in converted_files:
            archive.write(profile, arcname=profile.name)
        archive.write(bundle, arcname=bundle.name)

    print(f"Converted {len(converted_files)} profile(s)")
    print(f"Bundle: {bundle}")
    print(f"Archive: {archive_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
