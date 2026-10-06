import os
import json
import tempfile
import pytest
from renderer.document import Section, load_document
from renderer.tables import create_side_by_side_table_flowables
from renderer.config import load_config
from renderer.pdf import generate_document_pdf


def test_side_by_side_table_section_parsing():
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv1 = os.path.join(tmp_dir, "chem.csv")
        csv2 = os.path.join(tmp_dir, "phys.csv")
        with open(csv1, "w", encoding="utf-8") as f:
            f.write("A,B\n1,2\n")
        with open(csv2, "w", encoding="utf-8") as f:
            f.write("C,D\n3,4\n")

        data = {
            "type": "table_group",
            "title": "Comparative Results",
            "tables": [
                {"csv": "chem.csv", "title": "Chemistry"},
                {"csv": "phys.csv", "title": "Physics"}
            ]
        }
        sec = Section(data, doc_dir=tmp_dir)
        assert sec.type == "table"
        assert sec.side_by_side is True
        assert len(sec.tables) == 2


def test_side_by_side_table_pdf_rendering():
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv1_path = os.path.join(tmp_dir, "chem.csv")
        csv2_path = os.path.join(tmp_dir, "phys.csv")

        with open(csv1_path, "w", encoding="utf-8") as f:
            f.write("Sample,pH,Temp\nS1,7.2,25\nS2,6.8,24\n")

        with open(csv2_path, "w", encoding="utf-8") as f:
            f.write("Wavelength,Intensity\n450,1.2e3\n500,2.4e3\n")

        doc_json = {
            "title": "Side by Side Test Document",
            "sections": [
                {
                    "type": "table",
                    "layout": "side_by_side",
                    "title": "Side-by-Side Tables",
                    "tables": [
                        {"csv": "chem.csv", "title": "Chemistry Data"},
                        {"csv": "phys.csv", "title": "Physics Data"}
                    ]
                }
            ]
        }

        json_path = os.path.join(tmp_dir, "doc.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(doc_json, f)

        doc_model = load_document(json_path)
        out_pdf = os.path.join(tmp_dir, "output.pdf")
        generate_document_pdf(doc_model, out_pdf)

        assert os.path.exists(out_pdf)
        assert os.path.getsize(out_pdf) > 0


def test_mixed_side_by_side_and_single_table_in_same_section():
    with tempfile.TemporaryDirectory() as tmp_dir:
        c_hl = os.path.join(tmp_dir, "tphl.csv")
        c_lh = os.path.join(tmp_dir, "tplh.csv")
        c_tp = os.path.join(tmp_dir, "tp.csv")

        with open(c_hl, "w", encoding="utf-8") as f:
            f.write("x,y\n1,2\n")
        with open(c_lh, "w", encoding="utf-8") as f:
            f.write("x,y\n1,3\n")
        with open(c_tp, "w", encoding="utf-8") as f:
            f.write("x,y\n1,2.5\n")

        doc_json = {
            "title": "Mixed Table Layout Document",
            "sections": [
                {
                    "type": "table",
                    "title": "Propagation Delay Analysis",
                    "tables": [
                        {
                            "side_by_side": True,
                            "tables": [
                                {"csv": "tphl.csv", "title": "High-to-Low Delay (t_PHL)"},
                                {"csv": "tplh.csv", "title": "Low-to-High Delay (t_PLH)"}
                            ]
                        },
                        {
                            "csv": "tp.csv",
                            "title": "Average Propagation Delay (t_P)"
                        }
                    ]
                }
            ]
        }

        json_path = os.path.join(tmp_dir, "doc.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(doc_json, f)

        doc_model = load_document(json_path)
        out_pdf = os.path.join(tmp_dir, "output.pdf")
        generate_document_pdf(doc_model, out_pdf)

        assert os.path.exists(out_pdf)
        assert os.path.getsize(out_pdf) > 0
