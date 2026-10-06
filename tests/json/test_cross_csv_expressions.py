import os
import tempfile
import json
import pytest
from renderer.tables import process_table_matrix_expressions, create_table_flowable
from renderer.graph import GraphObject, render_graph_to_image, load_csv_data
from renderer.document import load_document
from renderer.pdf import generate_document_pdf


def test_cross_csv_averaging_and_formulas_with_aliases():
    with tempfile.TemporaryDirectory() as tmp_dir:
        f1_path = os.path.join(tmp_dir, "tphl.csv")
        f2_path = os.path.join(tmp_dir, "tplh.csv")
        f3_path = os.path.join(tmp_dir, "tp.csv")

        # 1. Direct Data CSV 1
        with open(f1_path, "w", encoding="utf-8") as f:
            f.write("fan in,same sizing,progressive sizing,error\n")
            f.write("2,3,4,0%\n")
            f.write("3,4,5,0%\n")
            f.write("4,5,6,0%\n")

        # 2. Direct Data CSV 2
        with open(f2_path, "w", encoding="utf-8") as f:
            f.write("fan in,same sizing,progressive sizing,error\n")
            f.write("2,5,8,0%\n")
            f.write("3,6,9,0%\n")
            f.write("4,7,10,0%\n")

        # 3. Computed CSV 3 with #source aliases (using quoted CSV formulas or space-separated args)
        with open(f3_path, "w", encoding="utf-8") as f:
            f.write("#source f1 = tphl.csv\n")
            f.write("#source f2 = tplh.csv\n")
            f.write("fan in,same sizing,progressive sizing,error\n")
            f.write('2,"avg(f1:re2, f2:re2)","avg(f1:re3, f2:re3)",$sperr(re2  re3)\n')
            f.write('3,"avg(f1:re2, f2:re2)","avg(f1:re3, f2:re3)",$sperr(re2  re3)\n')
            f.write('4,"avg(f1:re2, f2:re2)","avg(f1:re3, f2:re3)",$sperr(re2  re3)\n')

        headers, data_rows = load_csv_data(f3_path)
        assert headers == ["fan in", "same sizing", "progressive sizing", "error"]

        # Row 1: x=2, same_sizing=avg(3,5)=4, progressive_sizing=avg(4,8)=6, error=sperr(4,6)=+50%
        assert data_rows[0][0] == "2"
        assert data_rows[0][1] == "4"
        assert data_rows[0][2] == "6"
        assert data_rows[0][3] == "+50.00%"

        # Row 2: x=3, same_sizing=avg(4,6)=5, progressive_sizing=avg(5,9)=7, error=sperr(4.5,6.5)=+44.4444% or sperr(5,7)=+40%
        assert data_rows[1][0] == "3"
        assert data_rows[1][1] == "5"
        assert data_rows[1][2] == "7"
        assert data_rows[1][3] == "+40.00%"


def test_cross_csv_direct_filename_references():
    with tempfile.TemporaryDirectory() as tmp_dir:
        f1_path = os.path.join(tmp_dir, "tphl.csv")
        f2_path = os.path.join(tmp_dir, "tplh.csv")
        f3_path = os.path.join(tmp_dir, "tp.csv")

        with open(f1_path, "w", encoding="utf-8") as f:
            f.write("fan in,same sizing\n2,10\n3,20\n")
        with open(f2_path, "w", encoding="utf-8") as f:
            f.write("fan in,same sizing\n2,30\n3,40\n")

        # Direct filename references with quotes or space separation
        with open(f3_path, "w", encoding="utf-8") as f:
            f.write("fan in,same sizing\n")
            f.write('2,"avg(tphl.csv:re2, tplh.csv:re2)"\n')
            f.write('3,"avg(tphl.csv:re2, tplh.csv:re2)"\n')

        headers, data_rows = load_csv_data(f3_path)
        assert data_rows[0] == ["2", "20"]
        assert data_rows[1] == ["3", "30"]


def test_cross_csv_in_pdf_and_graph_rendering():
    with tempfile.TemporaryDirectory() as tmp_dir:
        f1_path = os.path.join(tmp_dir, "tphl.csv")
        f2_path = os.path.join(tmp_dir, "tplh.csv")
        f3_path = os.path.join(tmp_dir, "tp.csv")

        with open(f1_path, "w", encoding="utf-8") as f:
            f.write("fan in,same sizing,progressive sizing,error\n2,2,3,0%\n3,3,4,0%\n")
        with open(f2_path, "w", encoding="utf-8") as f:
            f.write("fan in,same sizing,progressive sizing,error\n2,4,5,0%\n3,5,6,0%\n")

        with open(f3_path, "w", encoding="utf-8") as f:
            f.write("#source f1 = tphl.csv\n#source f2 = tplh.csv\n")
            f.write("fan in,same sizing,progressive sizing,error\n")
            f.write('2,"avg(f1:re2, f2:re2)","avg(f1:re3, f2:re3)",sperr(re2, re3)\n')
            f.write('3,"avg(f1:re2, f2:re2)","avg(f1:re3, f2:re3)",sperr(re2, re3)\n')

        doc_json = {
            "title": "Cross-CSV Test Document",
            "sections": [
                {
                    "type": "table",
                    "title": "Computed Average Table",
                    "csv": "tp.csv"
                },
                {
                    "type": "graph",
                    "title": "Computed Average Graph",
                    "csv": "tp.csv",
                    "x": "fan in",
                    "y": ["same sizing", "progressive sizing"]
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
