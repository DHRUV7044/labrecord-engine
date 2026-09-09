import os
import tempfile
import pytest

from renderer.document import TableObject, DocumentModel
from renderer.tables import build_table_matrix, split_by_comma_smart
from renderer.config import load_config
from renderer.pdf import generate_document_pdf


def test_split_by_comma_smart():
    assert split_by_comma_smart("Technology , 180nm") == ["Technology", "180nm"]
    assert split_by_comma_smart("$V_{DD}$ , 1.8v") == ["$V_{DD}$", "1.8v"]
    assert split_by_comma_smart("PMOS Width ($W_p$) , 0.9") == ["PMOS Width ($W_p$)", "0.9"]
    # Test commas inside LaTeX math mode should not be split
    assert split_by_comma_smart("PMOS ($W_p, L_p$) , 0.9 , 1.8") == ["PMOS ($W_p, L_p$)", "0.9", "1.8"]


def test_build_table_matrix_comma_entries():
    table_dict = {
        "number": 1,
        "title": "DESIGN PARAMETERS",
        "elements": [
            {
                "title": "Parameter , Value",
                "entries": [
                    "Technology , 180nm",
                    "$V_{DD}$ , 1.8v",
                    "PMOS Width ($W_p$) , 0.9",
                    "NMOS Width ($W_n$) , 0.9"
                ]
            }
        ]
    }
    tbl_obj = TableObject(table_dict["number"], table_dict["title"], "", table_dict["elements"])
    matrix = build_table_matrix(tbl_obj)

    assert len(matrix) == 5
    assert matrix[0] == ["Parameter", "Value"]
    assert matrix[1] == ["Technology", "180nm"]
    assert matrix[2] == ["$V_{DD}$", "1.8v"]
    assert matrix[3] == ["PMOS Width ($W_p$)", "0.9"]
    assert matrix[4] == ["NMOS Width ($W_n$)", "0.9"]


def test_shorthand_array_comma_table():
    table_dict = {
        "number": 1,
        "title": "DESIGN PARAMETERS",
        "elements": [
            "Parameter , Value",
            "Technology , 180nm",
            "$V_{DD}$ , 1.8v"
        ]
    }
    tbl_obj = TableObject(table_dict["number"], table_dict["title"], "", table_dict["elements"])
    matrix = build_table_matrix(tbl_obj)

    assert len(matrix) == 3
    assert matrix[0] == ["Parameter", "Value"]
    assert matrix[1] == ["Technology", "180nm"]
    assert matrix[2] == ["$V_{DD}$", "1.8v"]


def test_render_comma_table_pdf():
    with tempfile.TemporaryDirectory() as tmpdir:
        doc_data = {
            "template": "vd",
            "experiments": [
                {
                    "number": 1,
                    "title": "COMMA TABLE TEST",
                    "sections": [
                        {
                            "type": "table",
                            "number": 1,
                            "title": "PARAMETERS",
                            "tables": [
                                {
                                    "title": "Design Parameters",
                                    "elements": [
                                        {
                                            "title": "Parameter , Value",
                                            "entries": [
                                                "Technology , 180nm",
                                                "$V_{DD}$ , 1.8v",
                                                "PMOS Width ($W_p$) , 0.9",
                                                "NMOS Width ($W_n$) , 0.9"
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        doc_model = DocumentModel(doc_data)
        out_pdf = os.path.join(tmpdir, "comma_table_test.pdf")
        generate_document_pdf(doc_model, out_pdf)
        assert os.path.exists(out_pdf)
        assert os.path.getsize(out_pdf) > 0
