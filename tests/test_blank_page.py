import os
import json
import tempfile
import unittest
from renderer.document import load_document
from renderer.pdf import generate_document_pdf
from renderer.cli import handle_blank

class TestBlankPage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.record_path = os.path.join(self.temp_dir.name, "record.json")
        self.output_pdf = os.path.join(self.temp_dir.name, "output.pdf")
        
        record_data = {
            "document": {"title": "TEST BLANK PAGE"},
            "experiments": [
                {
                    "number": 1,
                    "title": "Test Experiment",
                    "sections": [
                        {"type": "text", "title": "Aim", "text": "This is page 1."},
                        {"type": "blank"},
                        {"type": "text", "title": "Conclusion", "text": "This is page 3."}
                    ]
                }
            ]
        }
        with open(self.record_path, "w", encoding="utf-8") as f:
            json.dump(record_data, f, indent=4)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_blank_page_section(self):
        doc_model = load_document(self.record_path)
        pdf_path = generate_document_pdf(doc_model, output_path=self.output_pdf)
        self.assertTrue(os.path.exists(pdf_path))
        
        # Verify with reportlab
        with open(pdf_path, "rb") as f:
            content = f.read()
            page_count = content.count(b"/Type /Page")
            self.assertEqual(page_count, 3)

    def test_blank_cli_command(self):
        class DummyArgs:
            record = self.record_path
            count = 2
            page_break = False

        handle_blank(DummyArgs())

        with open(self.record_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            sections = data["experiments"][0]["sections"]
            blank_secs = [s for s in sections if s.get("type") == "blank"]
            self.assertEqual(len(blank_secs), 3)

if __name__ == "__main__":
    unittest.main()
