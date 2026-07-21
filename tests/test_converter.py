import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from convert import COMPATIBILITY, convert_profile


class ConverterTests(unittest.TestCase):
    def test_coreone_profile_is_converted_for_supported_indx_models(self):
        source = """filament_settings_id = Test PLA @Prusa Core One
inherits = Generic PLA @COREONE
compatible_printers_condition = printer_model=~/(COREONE)/ and nozzle_diameter[0]==0.4
"""
        converted = convert_profile(source)
        self.assertIn("inherits = Generic PLA @COREONEINDX HF0.4", converted)
        self.assertIn("filament_settings_id = Test PLA @Prusa CORE One INDX HF0.4", converted)
        self.assertIn(f"compatible_printers_condition = {COMPATIBILITY}", converted)
        for model in ("COREONE_INDX4T", "COREONE_INDX8T"):
            self.assertIn(model, converted)
        self.assertNotIn("COREONEL", converted)

    def test_existing_indx_parent_is_not_modified_twice(self):
        source = "inherits = Generic PLA @COREONEINDX HF0.4\n"
        converted = convert_profile(source)
        self.assertIn("inherits = Generic PLA @COREONEINDX HF0.4", converted)
        self.assertNotIn("HF0.4INDX", converted)


if __name__ == "__main__":
    unittest.main()
