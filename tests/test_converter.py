import json
import re
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from convert import (
    COMPATIBILITY,
    INDX,
    INDX_COMPATIBILITY,
    STANDARD,
    STANDARD_COMPATIBILITY,
    collect_ini_files,
    convert_profile,
    reject_duplicate_output_names,
)


class ConverterTests(unittest.TestCase):
    PROFILE = """filament_settings_id = Test PLA @Prusa Core One
inherits = Generic PLA @COREONE
compatible_printers_condition = printer_model=~/(COREONE)/ and nozzle_diameter[0]==0.4
compatible_printers_condition_cummulative = printer_model=~/(COREONE|COREONEL)/ and nozzle_diameter[0]==0.4
"""

    def test_coreone_profile_is_converted_for_all_supported_indx_models(self):
        converted = convert_profile(self.PROFILE, INDX)
        self.assertIn("inherits = Generic PLA @COREONEINDX HF0.4", converted)
        self.assertIn("filament_settings_id = Test PLA @Prusa CORE One INDX HF0.4", converted)
        self.assertIn(f"compatible_printers_condition = {COMPATIBILITY}", converted)
        self.assertIn(
            f"compatible_printers_condition_cummulative = {COMPATIBILITY}", converted
        )
        for model in (
            "COREONE_INDX4T",
            "COREONE_INDX8T",
            "COREONEL_INDX4T",
            "COREONEL_INDX8T",
        ):
            self.assertIn(model, converted)

    def test_coreone_profile_is_converted_for_all_standard_hf_models(self):
        converted = convert_profile(self.PROFILE, STANDARD)
        self.assertIn("inherits = Generic PLA @COREONE HF0.4", converted)
        self.assertIn("filament_settings_id = Test PLA @Prusa CORE One HF0.4", converted)
        self.assertIn(
            f"compatible_printers_condition = {STANDARD_COMPATIBILITY}", converted
        )
        for model in (
            "COREONE",
            "COREONEOAK",
            "COREONEMMU3",
            "COREONEL",
            "COREONELMMU3",
        ):
            self.assertIn(model, converted)

    def test_existing_indx_parent_is_not_modified_twice(self):
        source = "inherits = Generic PLA @COREONEINDX HF0.4\n"
        converted = convert_profile(source)
        self.assertIn("inherits = Generic PLA @COREONEINDX HF0.4", converted)
        self.assertNotIn("HF0.4INDX", converted)

    def test_zip_extraction_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive_path = root / "unsafe.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("../../escaped.ini", "filament_settings_id = Unsafe")
            with self.assertRaisesRegex(ValueError, "Unsafe ZIP entry"):
                collect_ini_files(archive_path, root / "extract")

    def test_duplicate_output_filenames_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate output filename"):
            reject_duplicate_output_names(
                [Path("first/Profile.ini"), Path("second/profile.INI")]
            )

    def test_tracked_source_builds_complete_importable_bundle(self):
        repository = Path(__file__).resolve().parents[1]
        source = repository / "source" / "polymaker-presets-core-one.zip"
        manifest = json.loads(
            (repository / "source" / "polymaker-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        expected_count = manifest["profileCount"]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output"
            result = subprocess.run(
                [
                    sys.executable,
                    str(repository / "convert.py"),
                    str(source),
                    "--output",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            generated_count = expected_count * 2
            self.assertIn(f"Converted {generated_count} profile(s)", result.stdout)

            profiles = sorted((output / "individual").glob("*.ini"))
            self.assertEqual(len(profiles), generated_count)
            self.assertEqual(
                len({profile.name.casefold() for profile in profiles}), generated_count
            )
            for profile in profiles:
                contents = profile.read_text(encoding="utf-8")
                if "INDX HF0.4" in profile.name:
                    self.assertIn(
                        f"compatible_printers_condition = {INDX_COMPATIBILITY}",
                        contents,
                    )
                    self.assertIn("@COREONEINDX HF0.4", contents)
                else:
                    self.assertIn(
                        f"compatible_printers_condition = {STANDARD_COMPATIBILITY}",
                        contents,
                    )
                    self.assertIn("@COREONE HF0.4", contents)

            bundle = (
                output / "bundle" / "INDX-Filament-Profiles-HF0.4-config-bundle.ini"
            ).read_text(encoding="utf-8")
            sections = re.findall(r"^\[filament:[^]]+\]$", bundle, re.MULTILINE)
            self.assertEqual(len(sections), generated_count)
            self.assertEqual(len(set(sections)), generated_count)
            self.assertEqual(
                bundle.count(
                    f"compatible_printers_condition = {INDX_COMPATIBILITY}"
                ),
                expected_count,
            )
            self.assertEqual(
                bundle.count(
                    f"compatible_printers_condition = {STANDARD_COMPATIBILITY}"
                ),
                expected_count,
            )


if __name__ == "__main__":
    unittest.main()
