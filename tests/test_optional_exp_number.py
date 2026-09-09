import os
import tempfile
import pytest

from renderer.document import DocumentModel, Experiment
from renderer.pdf import generate_document_pdf


def test_experiment_number_optional():
    doc_data = {
        "template": "vd",
        "experiments": [
            {
                # "number" omitted intentionally
                "title": "NO EXP NUMBER TEST",
                "type": "main_experiment",
                "sections": [
                    {
                        "type": "text",
                        "number": 1,
                        "title": "AIM",
                        "text": "Testing experiment without number."
                    }
                ]
            }
        ]
    }
    model = DocumentModel(doc_data)
    assert model.experiments[0].number is None

    with tempfile.TemporaryDirectory() as tmpdir:
        out_pdf = os.path.join(tmpdir, "no_exp_num.pdf")
        generate_document_pdf(model, out_pdf)
        assert os.path.exists(out_pdf)
        assert os.path.getsize(out_pdf) > 0


def test_experiment_header_section_disabled():
    doc_data = {
        "template": "vd",
        "experiments": [
            {
                "sections": [
                    {
                        "type": "text",
                        "number": 1,
                        "title": "AIM",
                        "text": "Testing document without any experiment header section."
                    }
                ]
            }
        ]
    }
    model = DocumentModel(doc_data)
    from renderer.config import load_config
    config = load_config(template_name="vd")
    config.data["experiment_header"]["show_header"] = False

    with tempfile.TemporaryDirectory() as tmpdir:
        out_pdf = os.path.join(tmpdir, "disabled_header.pdf")
        generate_document_pdf(model, out_pdf, config=config)
        assert os.path.exists(out_pdf)
        assert os.path.getsize(out_pdf) > 0

