#!/usr/bin/env python3
"""Convert Prusa CORE One filament presets for Bondtech INDX HF nozzles."""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

SUPPORTED_MODELS = (
    "COREONE_INDX4T",
    "COREONE_INDX8T",
    "COREONEL_INDX4T",
    "COREONEL_INDX8T",
)
COMPATIBILITY = (
    "printer_model=~/(" + "|".join(SUPPORTED_MODELS) + ")/ "
    "and nozzle_diameter[0]==0.4 and nozzle_high_flow[0]"
)

# Known PrusaSlicer parent profiles. Unknown @COREONE parents are converted
# mechanically so the script remains useful as source packs evolve.
INHERIT_MAP = {
    "Generic PLA @COREONE": "Generic PLA @COREONEINDX HF0.4",
    "Prusament PLA @COREONE": "Prusament PLA @COREONEINDX HF0.4",
    "Generic PETG @COREONE": "Generic PETG @COREONEINDX HF0.4",
    "Prusament PETG @COREONE": "Prusament PETG @COREONEINDX HF0.4",
    "Generic ASA @COREONE": "Generic ASA @COREONEINDX HF0.4",
    "Prusament ASA @COREONE": "Prusament ASA @COREONEINDX HF0.4",
    "Generic ABS @COREONE": "Generic ABS @COREONEINDX HF0.4",
    "Generic FLEX @COREONE": "Generic FLEX @COREONEINDX HF0.4",
    "Generic PC @COREONE": "Generic PC @COREONEINDX HF0.4",
    "Generic PP @COREONE": "Generic PP @COREONEINDX HF0.4",
    "Generic PA @COREONE": "Generic PA @COREONEINDX HF0.4",
}


def convert_inherits(value: str) -> str:
    value = value.strip()
    if value in INHERIT_MAP:
        return INHERIT_MAP[value]
    if "@COREONE" in value and "@COREONEINDX" not in value:
        return value.replace("@COREONE", "@COREONEINDX HF0.4")
    return value


def convert_profile(text: str) -> str:
    lines = text.splitlines()
    converted: list[str] = []
    saw_compatibility = False

    for line in lines:
        if re.match(r"^inherits\s*=", line):
            key, value = line.split("=", 1)
            line = f"{key.strip()} = {convert_inherits(value)}"
        elif re.match(r"^compatible_printers_condition\s*=", line):
            line = f"compatible_printers_condition = {COMPATIBILITY}"
            saw_compatibility = True
        elif re.match(r"^compatible_printers_condition_cummulative\s*=", line):
            line = f"compatible_printers_condition_cummulative = {COMPATIBILITY}"
        elif re.match(r"^filament_settings_id\s*=", line):
            key, value = line.split("=", 1)
            value = value.strip()
            value = re.sub(
                r"\s*@Prusa\s+Core\s+One(?:\s+INDX(?:\s+HF0\.4)?)?$",
                " @Prusa CORE One INDX HF0.4",
                value,
                flags=re.IGNORECASE,
            )
            line = f"{key.strip()} = {value}"
        converted.append(line)

    if not saw_compatibility:
        converted.append(f"compatible_printers_condition = {COMPATIBILITY}")

    return "\n".join(converted).rstrip() + "\n"


def collect_ini_files(source: Path, temp_dir: Path) -> list[Path]:
    if source.is_dir():
        return sorted(source.rglob("*.ini"))
    if source.suffix.lower() == ".zip":
        with zipfile.ZipFile(source) as archive:
            archive.extractall(temp_dir)
        return sorted(temp_dir.rglob("*.ini"))
    if source.suffix.lower() == ".ini":
        return [source]
    raise ValueError("Source must be an .ini file, a directory, or a ZIP archive")


def build_bundle(files: list[Path], destination: Path) -> None:
    # PrusaSlicer accepts concatenated exported filament sections as a config bundle.
    chunks: list[str] = []
    for profile in files:
        text = profile.read_text(encoding="utf-8-sig")
        chunks.append(text.rstrip())
    destination.write_text("\n\n".join(chunks) + "\n", encoding="utf-8")


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

        converted_files: list[Path] = []
        for profile in source_files:
            converted = convert_profile(profile.read_text(encoding="utf-8-sig"))
            destination = individual / profile.name
            destination.write_text(converted, encoding="utf-8")
            converted_files.append(destination)

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
