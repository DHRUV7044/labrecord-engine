import os
import tempfile
import pytest
from renderer.graph import GraphObject, render_graph_to_image


def test_graph_object_label_map_validation():
    # Valid label_map
    data = {
        "csv": "tp.csv",
        "x": "x",
        "y": ["y1", "y2", "y3"],
        "label_map": {"y1": "tp1", "y2": "tp2", "y3": "tp3"}
    }
    graph_obj = GraphObject(data)
    assert graph_obj.label_map == {"y1": "tp1", "y2": "tp2", "y3": "tp3"}

    # Invalid label_map type
    invalid_data = {
        "csv": "tp.csv",
        "x": "x",
        "y": ["y1"],
        "label_map": ["tp1", "tp2"]
    }
    with pytest.raises(ValueError, match="label_map"):
        GraphObject(invalid_data)


def test_render_graph_with_label_map():
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = os.path.join(tmp_dir, "tp.csv")
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write("x , y1 , y2 , y3\n")
            f.write("1 , 2 , 3 , 4\n")
            f.write("2 , 3 , 4 , 5\n")
            f.write("3 , 4 , 5 , 6\n")

        data = {
            "csv": "tp.csv",
            "x": "x",
            "y": ["y1", "y2", "y3"],
            "label_map": {
                "y1": "tp1",
                "y2": "tp2",
                "y3": "tp3"
            }
        }
        graph_obj = GraphObject(data, doc_dir=tmp_dir)
        png_path = render_graph_to_image(graph_obj, output_dir=tmp_dir)

        assert os.path.exists(png_path)
        assert os.path.getsize(png_path) > 0


def test_render_graph_backward_compatibility():
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = os.path.join(tmp_dir, "tp.csv")
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write("x,y\n")
            f.write("1,2\n")
            f.write("2,3\n")

        data = {
            "csv": "tp.csv",
            "x": "x",
            "y": "y"
        }
        graph_obj = GraphObject(data, doc_dir=tmp_dir)
        assert graph_obj.label_map == {}
        png_path = render_graph_to_image(graph_obj, output_dir=tmp_dir)

        assert os.path.exists(png_path)
        assert os.path.getsize(png_path) > 0
