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
