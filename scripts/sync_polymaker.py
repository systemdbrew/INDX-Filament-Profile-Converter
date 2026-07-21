#!/usr/bin/env python3
"""Synchronize Polymaker's PrusaSlicer profiles for the Prusa Core One."""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

INDEX_URL = "https://raw.githubusercontent.com/Polymaker3D/Polymaker-Preset/main/index.json"
RAW_BASE_URL = "https://raw.githubusercontent.com/Polymaker3D/Polymaker-Preset/main/"
TARGET = {"brand": "Prusa", "model": "Core One", "slicer": "PrusaSlicer"}
ARCHIVE_NAME = "polymaker-presets-core-one.zip"
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "INDX-profile-updater/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def select_presets(index: dict) -> list[dict]:
    presets = [
        preset
        for preset in index.get("presets", [])
        if all(preset.get(key) == value for key, value in TARGET.items())
    ]
    presets.sort(key=lambda preset: preset["path"])
    if not presets:
        raise ValueError("Polymaker index contains no exact Prusa/Core One/PrusaSlicer matches")
    return presets


def download_presets(presets: list[dict]) -> list[tuple[dict, bytes]]:
    downloaded = []
    filenames: set[str] = set()
    for preset in presets:
        filename = preset.get("filename")
        path = preset.get("path")
        if not filename or not path or not filename.lower().endswith(".ini"):
            raise ValueError(f"Unexpected preset entry: {preset!r}")
        if filename in filenames:
            raise ValueError(f"Duplicate upstream filename: {filename}")
        filenames.add(filename)
        url = urllib.parse.urljoin(RAW_BASE_URL, urllib.parse.quote(path, safe="/"))
        content = fetch(url)
        if b"filament_settings_id" not in content:
            raise ValueError(f"Downloaded file does not look like a filament preset: {path}")
        downloaded.append((preset, content))
    return downloaded


def build_manifest(index: dict, downloaded: list[tuple[dict, bytes]]) -> dict:
    return {
        "schemaVersion": 1,
        "source": INDEX_URL,
        "filter": TARGET,
        "profileCount": len(downloaded),
        "profiles": [
            {
                "path": preset["path"],
                "filename": preset["filename"],
                "updatedAt": preset.get("updatedAt"),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
            for preset, content in downloaded
        ],
    }


def write_archive(path: Path, downloaded: list[tuple[dict, bytes]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        temporary_path = Path(temporary.name)
    try:
        with zipfile.ZipFile(temporary_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            directory = zipfile.ZipInfo("polymaker-presets/", ZIP_TIMESTAMP)
            directory.external_attr = 0o755 << 16
            archive.writestr(directory, b"")
            for preset, content in downloaded:
                info = zipfile.ZipInfo(f"polymaker-presets/{preset['filename']}", ZIP_TIMESTAMP)
                info.external_attr = 0o644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, content)
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)


def synchronize(source_dir: Path, manifest_path: Path, index_url: str) -> bool:
    index = json.loads(fetch(index_url))
    presets = select_presets(index)
    downloaded = download_presets(presets)
    manifest = build_manifest(index, downloaded)
    manifest_text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    old_manifest = manifest_path.read_text(encoding="utf-8") if manifest_path.exists() else None
    archive_path = source_dir / ARCHIVE_NAME

    if old_manifest == manifest_text and archive_path.exists():
        print(f"Polymaker Core One profiles are current ({len(downloaded)} profiles).")
        return False

    write_archive(archive_path, downloaded)
    for old_archive in source_dir.glob("*.zip"):
        if old_archive != archive_path:
            old_archive.unlink()
    manifest_path.write_text(manifest_text, encoding="utf-8")
    print(f"Updated {archive_path} with {len(downloaded)} profiles.")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=Path("source"))
    parser.add_argument("--manifest", type=Path, default=Path("source/polymaker-manifest.json"))
    parser.add_argument("--index-url", default=INDEX_URL)
    args = parser.parse_args()
    synchronize(args.source_dir, args.manifest, args.index_url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
