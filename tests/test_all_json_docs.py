import os
import glob
import tempfile
import pytest

from renderer.document import load_document
from renderer.pdf import generate_document_pdf, build_manifest


def get_all_test_json_files():
    files = glob.glob("labs/*.json") + glob.glob("tests/*.json")
    return sorted([f for f in files if not f.endswith("package.json")])


@pytest.mark.parametrize("json_file", get_all_test_json_files())
def test_render_individual_json_doc(json_file):
    assert os.path.exists(json_file)
    with tempfile.TemporaryDirectory() as tmpdir:
        doc_model = load_document(json_file)
        out_pdf = os.path.join(tmpdir, "output.pdf")
        res = generate_document_pdf(doc_model, out_pdf)
        assert os.path.exists(res)
        assert os.path.getsize(res) > 0


def test_build_main_manifest():
    assert os.path.exists("main.json")
    results = build_manifest("main.json")
    assert len(results) > 0
    for in_path, out_path, success, err_msg in results:
        assert success is True, f"Failed job {in_path}: {err_msg}"
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 0
