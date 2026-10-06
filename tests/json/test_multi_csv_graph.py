import os
import tempfile
import pytest
from renderer.graph import GraphObject, render_graph_to_image


def test_multi_csv_graph_via_series_list():
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv1 = os.path.join(tmp_dir, "data1.csv")
        csv2 = os.path.join(tmp_dir, "data2.csv")

        with open(csv1, "w", encoding="utf-8") as f:
            f.write("x,y1\n1,10\n2,20\n3,30\n")
        with open(csv2, "w", encoding="utf-8") as f:
            f.write("x,y2\n1,15\n2,25\n3,35\n")

        data = {
            "title": "Multi-CSV Series Test",
            "series": [
                {"csv": "data1.csv", "x": "x", "y": "y1", "label": "Trial 1", "color": "blue"},
                {"csv": "data2.csv", "x": "x", "y": "y2", "label": "Trial 2", "color": "red"}
            ]
        }
        graph_obj = GraphObject(data, doc_dir=tmp_dir)
        graph_obj.validate()

        assert len(graph_obj.series_specs) == 2
        png_path = render_graph_to_image(graph_obj, output_dir=tmp_dir)

        assert os.path.exists(png_path)
        assert os.path.getsize(png_path) > 0


def test_multi_csv_graph_via_csv_list():
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv1 = os.path.join(tmp_dir, "c1.csv")
        csv2 = os.path.join(tmp_dir, "c2.csv")

        with open(csv1, "w", encoding="utf-8") as f:
            f.write("time,voltage\n0,0\n1,5\n2,10\n")
        with open(csv2, "w", encoding="utf-8") as f:
            f.write("time,voltage\n0,1\n1,6\n2,11\n")

        data = {
            "title": "CSV List Test",
            "csv": ["c1.csv", "c2.csv"],
            "x": "time",
            "y": "voltage"
        }
        graph_obj = GraphObject(data, doc_dir=tmp_dir)
        graph_obj.validate()

        assert len(graph_obj.series_specs) == 2
        png_path = render_graph_to_image(graph_obj, output_dir=tmp_dir)

        assert os.path.exists(png_path)
        assert os.path.getsize(png_path) > 0


def test_graph_dimensions_in_mm():
    # Defaults: width = 165 mm, height = 100 mm
    data0 = {"csv": "dummy.csv"}
    g0 = GraphObject(data0)
    assert g0.width_mm == 165.0
    assert g0.height_mm == 100.0

    # Test numeric mm (e.g. height=90 -> 90mm)
    data1 = {"height": 90, "width": 150, "csv": "dummy.csv"}
    g1 = GraphObject(data1)
    assert g1.height_mm == 90.0
    assert g1.width_mm == 150.0

    # Test explicit string unit (e.g. height="95mm")
    data2 = {"height": "95mm", "width": "160mm", "csv": "dummy.csv"}
    g2 = GraphObject(data2)
    assert g2.height_mm == 95.0
    assert g2.width_mm == 160.0

    # Test height_mm and width_mm properties
    data3 = {"height_mm": 110, "width_mm": 170, "csv": "dummy.csv"}
    g3 = GraphObject(data3)
    assert g3.height_mm == 110.0
    assert g3.width_mm == 170.0
