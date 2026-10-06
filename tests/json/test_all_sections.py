# tests/json/test_all_sections.py
"""Integration test that exercises every section type using a generated JSON document.

The test creates temporary CSV files for table and graph sections, builds a JSON
record containing text, code, table, image, and graph sections, renders it to a
PDF, and asserts that the PDF is produced and non‑empty.
"""
import os
import json
import tempfile
import pytest

from renderer.document import load_document
from renderer.pdf import generate_document_pdf

# Helper to write a CSV file and return its path
def _write_csv(path, rows):
    with open(path, "w", encoding="utf-8-sig") as f:
        for row in rows:
            f.write(",".join(map(str, row)) + "\n")

@pytest.fixture(scope="module")
def temp_assets():
    """Create temporary CSV files for table and graph sections.

    Returns a dict with keys ``table_csv`` and ``graph_csv`` pointing at the
    created files.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        table_csv = os.path.join(tmpdir, "table.csv")
        graph_csv = os.path.join(tmpdir, "graph.csv")

        # Simple two‑column CSV for the table
        _write_csv(table_csv, [["Header1", "Header2"], ["A", 1], ["B", 2]])

        # Simple CSV for the graph (X, Y)
        _write_csv(graph_csv, [["X", "Y"], [1, 10], [2, 20], [3, 30]])

        yield {"table_csv": table_csv, "graph_csv": graph_csv}

def test_render_all_section_types(temp_assets, tmp_path):
    # Build JSON document with every supported section type
    json_record = {
        "template": "default",
        "document": {
            "title": "All Sections Test",
            "name": "Test User",
            "roll_number": "U123456"
        },
        "experiments": [
            {
                "number": 1,
                "title": "Comprehensive Demo",
                "date": "01/01/2026",
                "sections": [
                    # Text section
                    {
                        "type": "text",
                        "number": 1,
                        "title": "Introduction",
                        "text": "This is a **bold** text example with LaTeX $E=mc^2$.",
                        "new_page": False
                    },
                    # Code section (inline code)
                    {
                        "type": "code",
                        "number": 2,
                        "title": "Sample Code",
                        "language": "python",
                        "code": "print(\"Hello, LabRecord!\")",
                        "new_page": False
                    },
                    # Table section referencing CSV
                    {
                        "type": "table",
                        "number": 3,
                        "title": "Sample Table",
                        "csv": temp_assets["table_csv"],
                        "new_page": False
                    },
                    # Image section – use a placeholder image from the repo
                    {
                        "type": "image",
                        "title": "Placeholder Image",
                        "images": [
                            {
                                "id": "placeholder",
                                "path": "images/placeholder.png",
                                "title": "Placeholder"
                            }
                        ],
                        "new_page": False
                    },
                    # Graph section referencing CSV
                    {
                        "type": "graph",
                        "title": "Sample Graph",
                        "csv": temp_assets["graph_csv"],
                        "x": "X",
                        "y": "Y",
                        "graph_type": "line",
                        "new_page": False
                    }
                ]
            }
        ]
    }

    # Write JSON to a temporary file
    json_path = tmp_path / "all_sections.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_record, f, indent=2)

    # Load the document model and generate PDF
    doc_model = load_document(str(json_path))
    pdf_path = tmp_path / "output.pdf"
    result_path = generate_document_pdf(doc_model, str(pdf_path))

    # Validate PDF existence and non‑zero size
    assert os.path.exists(result_path), "PDF was not created"
    assert os.path.getsize(result_path) > 0, "Generated PDF is empty"
