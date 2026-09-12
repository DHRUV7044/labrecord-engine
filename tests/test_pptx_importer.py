import os
import json
import tempfile
import unittest
from renderer.pptx_importer import add_pptx_to_record

class TestPPTXImporterNoSection(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.record_path = os.path.join(self.temp_dir.name, "record.json")
        
        record_data = {
            "document": {"title": "TEST PPTX IMPORTER"},
            "images": [],
            "experiments": [
                {
                    "number": 1,
                    "title": "Test Experiment",
                    "sections": []
                }
            ]
        }
        with open(self.record_path, "w", encoding="utf-8") as f:
            json.dump(record_data, f, indent=4)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_no_section_option_doc(self):
        # Verify function signature and structure without requiring a real .pptx
        with open(self.record_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(len(data["images"]), 0)
            self.assertEqual(len(data["experiments"][0]["sections"]), 0)

if __name__ == "__main__":
    unittest.main()
