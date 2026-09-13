import os
import json
import tempfile
import unittest
from pathlib import Path
from batch_generate import batch_generate

class TestBatchGenerate(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_path = Path(self.temp_dir.name)

        # Create two project directories with all 3 JSON files
        self.proj1 = self.root_path / "proj1"
        self.proj2 = self.root_path / "proj2"
        self.proj1.mkdir()
        self.proj2.mkdir()

        record_data = {
            "template": "default",
            "document": {"title": "Batch Test"},
            "experiments": [{"number": 1, "title": "Exp 1", "sections": [{"type": "text", "text": "Hello"}]}]
        }
        main_data = {"jobs": [{"input": "record.json", "output": "output/lab_record.pdf"}]}
        config_data = {"page": {"size": "A4"}}

        for p in [self.proj1, self.proj2]:
            with open(p / "record.json", "w") as f:
                json.dump(record_data, f)
            with open(p / "main.json", "w") as f:
                json.dump(main_data, f)
            with open(p / "config.json", "w") as f:
                json.dump(config_data, f)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_batch_generate_collects_pdfs(self):
        batch_generate(str(self.root_path))
        all_pdfs = self.root_path / "all_pdfs"
        self.assertTrue(all_pdfs.exists())
        
        pdf_files = list(all_pdfs.glob("*.pdf"))
        self.assertEqual(len(pdf_files), 2)
        
        filenames = [f.name for f in pdf_files]
        self.assertTrue(any("proj1" in f for f in filenames))
        self.assertTrue(any("proj2" in f for f in filenames))

    def test_batch_generate_override(self):
        batch_generate(str(self.root_path), name="anmol", roll_number="U24EV052", overwrite=True)
        custom_folder = self.root_path / "anmol_u24ev052"
        self.assertTrue(custom_folder.exists())

        pdf_files = list(custom_folder.glob("*.pdf"))
        self.assertEqual(len(pdf_files), 2)

if __name__ == "__main__":
    unittest.main()
