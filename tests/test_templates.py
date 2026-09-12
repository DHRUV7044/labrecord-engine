import os
import json
import pytest
import tempfile
import shutil

from renderer.template_loader import list_available_templates, load_template
from renderer.document import DocumentModel, load_document
from renderer.config import load_config
from renderer.pdf import generate_document_pdf, build_manifest
from renderer.templates import init_project


def test_list_available_templates():
    templates = list_available_templates()
    assert "default" in templates
    assert "vd" in templates
    assert "cao" in templates


def test_load_template_cao():
    data = load_template("cao")
    assert data["name"] == "cao"
    assert "page" in data
    assert "code" in data


def test_load_template_default():
    data = load_template("default")
    assert data["name"] == "default"
    assert "page" in data
    assert "experiment_header" in data
    assert data["experiment_header"]["layout_style"] == "centered"


def test_load_template_vd():
    data = load_template("vd")
    assert data["name"] == "vd"
    assert "page" in data
    assert "experiment_header" in data
    assert data["experiment_header"]["layout_style"] == "centered"
    assert data["table"]["numbering_style"] == "section_based"
    assert data["figure"]["numbering_style"] == "section_based"


def test_invalid_template_error():
    with pytest.raises(ValueError) as excinfo:
        load_template("nonexistent_template")
    err_msg = str(excinfo.value)
    assert "ERROR: Template 'nonexistent_template' not found." in err_msg
    assert "default" in err_msg
    assert "vd" in err_msg
    assert "cao" in err_msg


def test_document_model_template_attribute():
    doc_data_vd = {
        "template": "vd",
        "experiments": [
            {
                "number": 1,
                "sections": []
            }
        ]
    }
    model_vd = DocumentModel(doc_data_vd)
    assert model_vd.template_name == "vd"

    doc_data_default = {
        "experiments": [
            {
                "number": 1,
                "sections": []
            }
        ]
    }
    model_default = DocumentModel(doc_data_default)
    assert model_default.template_name is None


def test_init_project_templates():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test default init
        default_dir = os.path.join(tmpdir, "proj_default")
        init_project(default_dir, template_name="default")
        rec_path = os.path.join(default_dir, "record.json")
        assert os.path.exists(rec_path)
        with open(rec_path, "r") as f:
            rec_data = json.load(f)
        assert rec_data.get("template") == "default"

        # Test vd init
        vd_dir = os.path.join(tmpdir, "proj_vd")
        init_project(vd_dir, template_name="vd")
        rec_path_vd = os.path.join(vd_dir, "record.json")
        assert os.path.exists(rec_path_vd)
        with open(rec_path_vd, "r") as f:
            rec_data_vd = json.load(f)
        assert rec_data_vd.get("template") == "vd"

        # Test cao init
        cao_dir = os.path.join(tmpdir, "proj_cao")
        init_project(cao_dir, template_name="cao")
        rec_path_cao = os.path.join(cao_dir, "record.json")
        assert os.path.exists(rec_path_cao)
        with open(rec_path_cao, "r") as f:
            rec_data_cao = json.load(f)
        assert rec_data_cao.get("template") == "cao"


def test_render_vd_document():
    with tempfile.TemporaryDirectory() as tmpdir:
        doc_path = os.path.join("labs", "vd_example_lab.json")
        assert os.path.exists(doc_path)

        doc_model = load_document(doc_path)
        assert doc_model.template_name == "vd"

        out_pdf = os.path.join(tmpdir, "vd_out.pdf")
        generate_document_pdf(doc_model, out_pdf)
        assert os.path.exists(out_pdf)
        assert os.path.getsize(out_pdf) > 0


def test_student_info_parsing():
    doc_data = {
        "document": {
            "title": "Engineering Lab Record",
            "name": "Dhruv",
            "roll_number": "220101"
        },
        "experiments": [
            {
                "number": 1,
                "title": "Inverter",
                "sections": [
                    {
                        "type": "text",
                        "title": "AIM",
                        "text": "Sample text"
                    }
                ]
            }
        ]
    }
    model = DocumentModel(doc_data)
    assert model.name == "Dhruv"
    assert model.roll_number == "220101"


def test_init_project_with_student_info():
    with tempfile.TemporaryDirectory() as tmpdir:
        init_project(tmpdir, template_name="vd", name="Dhruv", roll_number="220101")
        rec_path = os.path.join(tmpdir, "record.json")
        assert os.path.exists(rec_path)
        with open(rec_path, "r") as f:
            rec_data = json.load(f)
        assert rec_data["document"]["name"] == "Dhruv"
        assert rec_data["document"]["roll_number"] == "220101"


def test_student_info_pdf_rendering():
    doc_data = {
        "template": "vd",
        "document": {
            "title": "Engineering Lab Record",
            "name": "Dhruv",
            "roll_no": "220101"
        },
        "experiments": [
            {
                "number": 1,
                "title": "Inverter",
                "sections": [
                    {
                        "type": "text",
                        "title": "AIM",
                        "text": "Sample text for student header testing."
                    }
                ]
            }
        ]
    }
    model = DocumentModel(doc_data)
    with tempfile.TemporaryDirectory() as tmpdir:
        out_pdf = os.path.join(tmpdir, "student_header_test.pdf")
        generate_document_pdf(model, out_pdf)
        assert os.path.exists(out_pdf)
        assert os.path.getsize(out_pdf) > 0


def test_update_project_command():
    from renderer.updater import update_project
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create an incomplete config.json missing student_offset_y and other options
        cfg_path = os.path.join(tmpdir, "config.json")
        incomplete_cfg = {
            "page": {"size": "A4"},
            "experiment_header": {
                "font_size": 14
            }
        }
        with open(cfg_path, "w") as f:
            json.dump(incomplete_cfg, f)

        rec_path = os.path.join(tmpdir, "record.json")
        incomplete_rec = {
            "document": {
                "title": "Old Record"
            }
        }
        with open(rec_path, "w") as f:
            json.dump(incomplete_rec, f)

        res = update_project(tmpdir)
        assert res["config_updated"] is True
        assert res["record_updated"] is True

        with open(cfg_path, "r") as f:
            updated_cfg = json.load(f)
        assert "student_offset_y" in updated_cfg["experiment_header"]
        assert "exp_no_offset_y" in updated_cfg["experiment_header"]

        with open(rec_path, "r") as f:
            updated_rec = json.load(f)
        assert "name" in updated_rec["document"]
        assert "roll_number" in updated_rec["document"]


def test_custom_header_offsets_rendering():
    doc_data = {
        "template": "vd",
        "document": {
            "title": "Engineering Lab Record",
            "name": "Dhruv",
            "roll_no": "220101"
        },
        "experiments": [
            {
                "number": 1,
                "sections": [
                    {
                        "type": "text",
                        "title": "AIM",
                        "text": "Testing custom offsets."
                    }
                ]
            }
        ]
    }
    model = DocumentModel(doc_data)
    cfg = load_config("vd")
    cfg.data["experiment_header"]["student_offset_y"] = 12
    cfg.data["experiment_header"]["exp_no_offset_y"] = 0
    cfg.data["experiment_header"]["date_offset_y"] = -10
    cfg.data["experiment_header"]["rule_offset_y"] = -18

    with tempfile.TemporaryDirectory() as tmpdir:
        out_pdf = os.path.join(tmpdir, "custom_offsets.pdf")
        generate_document_pdf(model, out_pdf, config=cfg)
        assert os.path.exists(out_pdf)
        assert os.path.getsize(out_pdf) > 0


def test_multipage_header_repetition():
    # Verify multi-page PDF generation where Page 1 has Exp No & Date while Later Pages omit them
    doc_data = {
        "template": "vd",
        "document": {
            "title": "Multi Page Test",
            "name": "Dhruv",
            "roll_number": "220101"
        },
        "experiments": [
            {
                "number": 1,
                "title": "Multi Page Exp",
                "sections": [
                    {
                        "type": "text",
                        "title": "AIM",
                        "text": "Page 1 Content"
                    },
                    {
                        "type": "text",
                        "title": "THEORY",
                        "new_page": True,
                        "text": "Page 2 Content"
                    }
                ]
            }
        ]
    }
    model = DocumentModel(doc_data)
    with tempfile.TemporaryDirectory() as tmpdir:
        out_pdf = os.path.join(tmpdir, "multipage_header.pdf")
        generate_document_pdf(model, out_pdf)
        assert os.path.exists(out_pdf)
        assert os.path.getsize(out_pdf) > 0


def test_layout_node_grid_types():
    from renderer.document import LayoutNode

    # Test 2x2 grid node
    data_2x2 = {
        "type": "2x2",
        "elements": ["1", "2", "3", "4"]
    }
    node_2x2 = LayoutNode(data_2x2)
    assert node_2x2.node_type == "column"
    assert len(node_2x2.children) == 2
    assert node_2x2.children[0].node_type == "row"
    assert len(node_2x2.children[0].children) == 2
    assert node_2x2.children[0].children[0].image_id == "1"

    # Test 3x5 grid node
    data_3x5 = {
        "type": "3x5",
        "elements": [str(i) for i in range(1, 16)]
    }
    node_3x5 = LayoutNode(data_3x5)
    assert node_3x5.node_type == "column"
    assert len(node_3x5.children) == 3
    assert len(node_3x5.children[0].children) == 5


def test_parse_page_range_str():
    from renderer.pptx_importer import parse_page_range_str

    assert parse_page_range_str("2") == {2}
    assert parse_page_range_str("1,3-5") == {1, 3, 4, 5}
    assert parse_page_range_str("1-4, 6") == {1, 2, 3, 4, 6}
    assert parse_page_range_str(None) is None
    assert parse_page_range_str("") is None


def test_pptx_importer_mock():
    import zipfile
    from renderer.pptx_importer import add_pptx_to_record

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a dummy PPTX zip file with a sample media image
        pptx_path = os.path.join(tmpdir, "sample.pptx")
        with zipfile.ZipFile(pptx_path, "w") as z:
            z.writestr("ppt/presentation.xml", '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><p:sldIdLst><p:sldId r:id="rId1"/><p:sldId r:id="rId2"/></p:sldIdLst></p:presentation>')
            z.writestr("ppt/_rels/presentation.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="slides/slide1.xml"/><Relationship Id="rId2" Target="slides/slide2.xml"/></Relationships>')
            z.writestr("ppt/slides/_rels/slide1.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="../media/image1.png"/></Relationships>')
            z.writestr("ppt/slides/_rels/slide2.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="../media/image2.png"/></Relationships>')
            z.writestr("ppt/media/image1.png", b"dummy_png_bytes_1")
            z.writestr("ppt/media/image2.png", b"dummy_png_bytes_2")

        rec_path = os.path.join(tmpdir, "record.json")
        rec_data = {
            "template": "vd",
            "document": {"title": "Test Record"},
            "experiments": [{"number": 1, "title": "Exp 1", "sections": []}]
        }
        with open(rec_path, "w") as f:
            json.dump(rec_data, f)

        # Import slide 2 with 1x1 grid
        sec, count = add_pptx_to_record(
            pptx_path=pptx_path,
            record_json_path=rec_path,
            page_numbers="2",
            grid="1x1",
            title="PPTX Slide 2",
            image_dir="images"
        )
        assert count == 1
        assert sec["title"] == "PPTX Slide 2"

        with open(rec_path, "r") as f:
            updated_rec = json.load(f)
        assert len(updated_rec["images"]) == 1
        assert updated_rec["images"][0]["id"] == "sample_slide_2_img_1"




