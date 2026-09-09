import os
import json
import tempfile
import pytest
from renderer.document import DocumentModel, Section
from renderer.pdf import generate_document_pdf


def test_code_section_from_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a sample code file
        code_dir = os.path.join(tmpdir, "verilog")
        os.makedirs(code_dir, exist_ok=True)
        code_file = os.path.join(code_dir, "inverter.v")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write("module inverter(input a, output y);\n    assign y = ~a;\nendmodule\n")

        doc_data = {
            "title": "Code Test Lab",
            "experiments": [
                {
                    "number": "1",
                    "title": "Code Test",
                    "sections": [
                        {
                            "type": "code",
                            "number": "1.1",
                            "title": "Verilog Code",
                            "file": "verilog/inverter.v",
                            "language": "Verilog"
                        }
                    ]
                }
            ]
        }

        doc_path = os.path.join(tmpdir, "record.json")
        with open(doc_path, "w", encoding="utf-8") as f:
            json.dump(doc_data, f)

        doc = DocumentModel(doc_data, doc_path=doc_path)
        sec = doc.experiments[0].sections[0]

        assert sec.type == "code"
        assert sec.code_path == "verilog/inverter.v"
        assert sec.language == "Verilog"
        assert "module inverter" in sec.code_text
        assert "assign y = ~a;" in sec.code_text

        # Test PDF rendering
        pdf_path = os.path.join(tmpdir, "output.pdf")
        generate_document_pdf(doc, pdf_path)
        assert os.path.exists(pdf_path)
        assert os.path.getsize(pdf_path) > 0


def test_code_section_inline():
    doc_data = {
        "title": "Inline Code Test",
        "experiments": [
            {
                "number": "2",
                "title": "Inline Code",
                "sections": [
                    {
                        "type": "code",
                        "title": "Python Script",
                        "code": "def hello():\n    print('Hello World')",
                        "language": "Python",
                        "show_line_numbers": False
                    }
                ]
            }
        ]
    }

    doc = DocumentModel(doc_data, doc_path="test.json")
    sec = doc.experiments[0].sections[0]

    assert sec.type == "code"
    assert sec.show_line_numbers is False
    assert "def hello():" in sec.code_text


def test_missing_code_file_error():
    doc_data = {
        "title": "Missing File Test",
        "experiments": [
            {
                "number": "3",
                "sections": [
                    {
                        "type": "code",
                        "file": "non_existent_file.v"
                    }
                ]
            }
        ]
    }

    with pytest.raises(FileNotFoundError):
        DocumentModel(doc_data, doc_path="/tmp/fake_path/record.json")
