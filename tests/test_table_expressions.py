import os
import tempfile
import pytest

from renderer.document import TableObject, DocumentModel
from renderer.tables import build_table_matrix, process_table_matrix_expressions
from renderer.pdf import generate_document_pdf


def test_row_element_subtraction():
    matrix = [
        ["100.0", "40.0"],
        ["50.0", "10.0"],
        ["r1e1 - r2e2", "r1e2 - r2e1"]
    ]
    res = process_table_matrix_expressions(matrix)
    # Row 3 Col 1 (r1e1 - r2e2): 100.0 - 10.0 = 90
    assert res[2][0] == "90"
    # Row 3 Col 2 (r1e2 - r2e1): 40.0 - 50.0 = -10
    assert res[2][1] == "-10"


def test_same_row_and_same_col_references():
    matrix = [
        ["Param", "Val1", "Val2"],
        ["TestA", "10.0", "re2 + 5"],
        ["TestB", "30.0", "re2 * 2"],
        ["Sum", "ce2 + ce3", "avg(ce2, ce3)"]
    ]
    res = process_table_matrix_expressions(matrix)
    # Row 2 (index 1): re2 (10.0) + 5 = 15
    assert res[1][2] == "15"
    # Row 3 (index 2): re2 (30.0) * 2 = 60
    assert res[2][2] == "60"
    # Row 4 Col 2 (index 3, 1): ce2 (Row 2 Col 2 = 10.0) + ce3 (Row 3 Col 2 = 30.0) = 40
    assert res[3][1] == "40"
    # Row 4 Col 3: avg(ce2, ce3) -> avg(15, 60) = 37.5
    assert res[3][2] == "37.5"


def test_avg_and_perr_functions():
    matrix = [
        ["Parameter", "Without RC", "With RC", "Diff", "Error (%)"],
        ["Delay", "15.02 ps", "22.05 ps", "re3 - re2", "$perr(re2, re3)$"],
        ["Rise Time", "48.89 ps", "78.75 ps", "re3 - re2", "$perr(re2, re3)$"],
        ["Average Delay", "$avg(ce2, ce3)$", "$avg(ce2, ce3)$", "re3 - re2", "$perr(re2, re3)$"]
    ]
    res = process_table_matrix_expressions(matrix)
    
    # Row 1 Diff (22.05 - 15.02) = 7.03
    assert res[1][3] == "7.03"
    # Row 1 Error (%) (perr(15.02, 22.05)) = 46.8043%
    assert res[1][4] == "46.8043%"

    # Row 3 Without RC Avg (avg(15.02, 48.89)) = 31.955
    assert res[3][1] == "31.955"
    # Row 3 With RC Avg (avg(22.05, 78.75)) = 50.4
    assert res[3][2] == "50.4"


def test_render_table_calculations_pdf():
    with tempfile.TemporaryDirectory() as tmpdir:
        doc_data = {
            "template": "vd",
            "experiments": [
                {
                    "number": 1,
                    "title": "TABLE CALCULATIONS TEST",
                    "sections": [
                        {
                            "type": "table",
                            "number": 1,
                            "title": "RESULTS",
                            "tables": [
                                {
                                    "title": "Calculated Parameters",
                                    "elements": [
                                        "Parameter , Without RC , With RC , Difference , Error (%)",
                                        "$V_{TH}$ , 713.958 mV , 712.969 mV , re3 - re2 , $perr(re2, re3)$",
                                        "$t_{pHL}$ , 15.02 ps , 22.05 ps , re3 - re2 , $perr(re2, re3)$",
                                        "$t_{pLH}$ , 33.70 ps , 48.06 ps , re3 - re2 , $perr(re2, re3)$"
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        doc_model = DocumentModel(doc_data)
        out_pdf = os.path.join(tmpdir, "table_calc_test.pdf")
        generate_document_pdf(doc_model, out_pdf)
        assert os.path.exists(out_pdf)
        assert os.path.getsize(out_pdf) > 0
