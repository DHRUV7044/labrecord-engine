import os
import json
import tempfile
import pytest

from renderer.graph import GraphObject, load_csv_data, _resolve_col_index, render_graph_to_image, create_graph_flowable
from renderer.graph_importer import add_graph_to_record
from renderer.document import DocumentModel, Section
from renderer.pdf import generate_document_pdf
from renderer.config import load_config


@pytest.fixture
def sample_csv(tmp_path):
    csv_file = tmp_path / "data.csv"
    content = "Time (s),Voltage (V),Current (mA)\n0,0.0,0.0\n1,1.5,5.2\n2,3.0,10.1\n3,4.5,15.8\n4,6.0,20.0\n"
    csv_file.write_text(content, encoding="utf-8")
    return str(csv_file)


def test_load_csv_data(sample_csv):
    headers, rows = load_csv_data(sample_csv)
    assert headers == ["Time (s)", "Voltage (V)", "Current (mA)"]
    assert len(rows) == 5
    assert rows[0] == ["0", "0.0", "0.0"]


def test_resolve_col_index():
    headers = ["Time", "Voltage", "Current"]
    assert _resolve_col_index(0, headers) == 0
    assert _resolve_col_index(1, headers) == 1
    assert _resolve_col_index("Voltage", headers) == 1
    assert _resolve_col_index("curr", headers) == 2


def test_graph_object(sample_csv):
    data = {
        "title": "Voltage vs Time",
        "csv": sample_csv,
        "x": "Time (s)",
        "y": ["Voltage (V)", "Current (mA)"],
        "graph_type": "scatter",
        "xlabel": "t (s)",
        "ylabel": "V / I"
    }
    g_obj = GraphObject(data)
    assert g_obj.title == "Voltage vs Time"
    assert g_obj.graph_type == "scatter"
    assert len(g_obj.y_cols) == 2
    g_obj.validate()


def test_render_graph_to_image(sample_csv, tmp_path):
    data = {
        "title": "V vs T",
        "csv": sample_csv,
        "x": 0,
        "y": 1,
        "graph_type": "line"
    }
    g_obj = GraphObject(data)
    out_img = render_graph_to_image(g_obj, output_dir=str(tmp_path))
    assert os.path.exists(out_img)
    assert out_img.endswith(".png")


def test_section_graph_type_inference(sample_csv):
    data = {
        "title": "Graph Section",
        "csv": sample_csv,
        "x": 0,
        "y": 1
    }
    sec = Section(data)
    assert sec.type == "graph"
    assert len(sec.graphs) == 1


def test_pdf_with_graph_section(sample_csv, tmp_path):
    doc_json = {
        "document": {
            "title": "Test Graph PDF",
            "date": "29/09/2026"
        },
        "experiments": [
            {
                "title": "Plotting Test",
                "sections": [
                    {
                        "type": "graph",
                        "title": "IV Characteristics",
                        "csv": sample_csv,
                        "x": "Time (s)",
                        "y": ["Voltage (V)", "Current (mA)"],
                        "graph_type": "line",
                        "x_label": r"Time $t \text{ (s)}$",
                        "y_label": r"Output $V_{\text{out}}$"
                    }
                ]
            }
        ]
    }
    
    json_path = tmp_path / "doc.json"
    pdf_path = tmp_path / "output.pdf"
    json_path.write_text(json.dumps(doc_json), encoding="utf-8")

    doc_model = DocumentModel(doc_json, doc_path=str(json_path))
    config = load_config()
    res_pdf = generate_document_pdf(doc_model, str(pdf_path), config=config)
    assert os.path.exists(res_pdf)
    assert os.path.getsize(res_pdf) > 0


def test_add_graph_to_record(sample_csv, tmp_path):
    rec_path = tmp_path / "record.json"
    rec_path.write_text(json.dumps({"experiments": [{"sections": []}]}), encoding="utf-8")

    sec = add_graph_to_record(
        csv_path=sample_csv,
        record_json_path=str(rec_path),
        title="Sample Plot",
        x_col="Time (s)",
        y_cols="Voltage (V)",
        graph_type="bar"
    )

    assert sec["type"] == "graph"
    assert sec["title"] == "Sample Plot"
    assert sec["graph_type"] == "bar"

    with open(rec_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["experiments"][0]["sections"]) == 1
