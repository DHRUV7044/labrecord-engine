import os
import json
import csv
import tempfile
import pytest

from renderer.document import DocumentModel
from renderer.pdf import generate_document_pdf
from renderer.csv_importer import add_csv_to_record, load_csv_matrix
from renderer.templates import init_project


def test_load_csv_matrix():
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "test.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Param", "Value"])
            writer.writerow(["VDD", "1.8V"])

        matrix = load_csv_matrix(csv_path)
        assert matrix == [["Param", "Value"], ["VDD", "1.8V"]]


def test_render_csv_table_pdf():
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_file = os.path.join(tmpdir, "data.csv")
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Header 1", "Header 2", "Header 3"])
            writer.writerow(["Row 1 Col 1", "$V_{DD}$", "1.8V"])
            writer.writerow(["Row 2 Col 1", "Width", "180nm"])

        doc_data = {
            "title": "CSV Render Test",
            "experiments": [
                {
                    "number": 1,
                    "title": "CSV Experiment",
                    "sections": [
                        {
                            "type": "table",
                            "title": "Imported Table",
                            "csv": "data.csv"
                        }
                    ]
                }
            ]
        }

        doc_path = os.path.join(tmpdir, "record.json")
        with open(doc_path, "w", encoding="utf-8") as f:
            json.dump(doc_data, f)

        doc = DocumentModel(doc_data, doc_path=doc_path)
        tbl = doc.experiments[0].sections[0].tables[0]
        assert tbl.csv_matrix == [
            ["Header 1", "Header 2", "Header 3"],
            ["Row 1 Col 1", "$V_{DD}$", "1.8V"],
            ["Row 2 Col 1", "Width", "180nm"]
        ]

        pdf_path = os.path.join(tmpdir, "output.pdf")
        generate_document_pdf(doc, pdf_path)
        assert os.path.exists(pdf_path)
        assert os.path.getsize(pdf_path) > 0


def test_add_csv_to_record():
    with tempfile.TemporaryDirectory() as tmpdir:
        init_project(tmpdir)
        rec_path = os.path.join(tmpdir, "record.json")
        csv_path = os.path.join(tmpdir, "results.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Col1", "Col2"])
            writer.writerow(["10", "20"])

        add_csv_to_record(csv_path, record_json_path=rec_path, title="Custom Title")

        with open(rec_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        exp = data["experiments"][0]
        last_sec = exp["sections"][-1]
        assert last_sec["type"] == "table"
        assert last_sec["title"] == "Custom Title"
        assert last_sec["csv"] == "results.csv"
