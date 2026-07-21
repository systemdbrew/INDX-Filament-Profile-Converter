import hashlib
import unittest

from scripts.sync_polymaker import build_manifest, select_presets


class SyncPolymakerTests(unittest.TestCase):
    def test_selects_only_exact_prusa_core_one_prusaslicer_entries(self):
        wanted = {
            "material": "Test PLA",
            "brand": "Prusa",
            "model": "Core One",
            "slicer": "PrusaSlicer",
            "path": "preset/Test.ini",
            "filename": "Test.ini",
        }
        index = {
            "presets": [
                {**wanted, "model": "Core One L", "path": "preset/L.ini"},
                {**wanted, "slicer": "OrcaSlicer", "path": "preset/Orca.ini"},
                wanted,
            ]
        }
        self.assertEqual(select_presets(index), [wanted])

    def test_manifest_tracks_timestamp_and_content_hash(self):
        preset = {
            "path": "preset/Test.ini",
            "filename": "Test.ini",
            "updatedAt": "2026-01-02T03:04:05Z",
        }
        manifest = build_manifest({}, [(preset, b"profile contents")])
        self.assertEqual(manifest["profileCount"], 1)
        self.assertEqual(
            manifest["profiles"][0]["sha256"],
            hashlib.sha256(b"profile contents").hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
