import os
import tempfile
import json
import pytest
from renderer.graph import GraphObject, render_graph_to_image
from renderer.document import load_document
from renderer.pdf import generate_document_pdf


def test_graph_show_values_annotation():
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = os.path.join(tmp_dir, "data.csv")
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write("fan in,same sizing,progressive sizing\n")
            f.write("2,10.5,20\n")
            f.write("3,15.0,30\n")
            f.write("4,25.25,40\n")

        # Test GraphObject with show_values enabled
        graph_data = {
            "title": "Annotated Graph",
            "csv": "data.csv",
            "x": "fan in",
            "y": ["same sizing"],
            "show_values": True,
            "value_format": "{:.1f}"
        }

        graph_obj = GraphObject(graph_data, doc_dir=tmp_dir)
        assert graph_obj.show_values is True
        assert graph_obj.value_format == "{:.1f}"

        img_path = render_graph_to_image(graph_obj, output_dir=tmp_dir)
        assert os.path.exists(img_path)
        assert os.path.getsize(img_path) > 0


def test_graph_show_values_in_pdf_generation():
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = os.path.join(tmp_dir, "data.csv")
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write("x,y1,y2\n1,5,10\n2,8,15\n3,12,20\n")

        doc_json = {
            "title": "Show Values Test",
            "sections": [
                {
                    "type": "graph",
                    "title": "Annotated Line Graph",
                    "csv": "data.csv",
                    "x": "x",
                    "y": ["y1", "y2"],
                    "show_values": True
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


def test_anti_collision_multiple_series():
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = os.path.join(tmp_dir, "data.csv")
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write("fan in,s1,s2,s3\n")
            f.write("2,77.08,68.85,60.62\n")
            f.write("3,92.43,89.90,87.42\n")
            f.write("4,115.2,105.1,98.3\n")

        graph_data = {
            "title": "Anti Collision Graph",
            "csv": "data.csv",
            "x": "fan in",
            "y": ["s1", "s2", "s3"],
            "show_values": True
        }

        graph_obj = GraphObject(graph_data, doc_dir=tmp_dir)
        img_path = render_graph_to_image(graph_obj, output_dir=tmp_dir)
        assert os.path.exists(img_path)
        assert os.path.getsize(img_path) > 0

