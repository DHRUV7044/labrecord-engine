import os
import json
import tempfile
import pytest

from renderer.cli import main, find_manifest
from renderer.template_loader import list_available_templates


def test_cli_templates_command(capsys):
    sys_argv = ["labfile", "templates"]
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("sys.argv", sys_argv)
        main()
    captured = capsys.readouterr()
    assert "Available templates:" in captured.out
    assert "default" in captured.out
    assert "vd" in captured.out



def test_cli_init_default(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        sys_argv = ["labfile", "init", tmpdir, "-t", "default"]
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("sys.argv", sys_argv)
            main()
        captured = capsys.readouterr()
        assert "Initializing LabRecord project" in captured.out
        rec_path = os.path.join(tmpdir, "record.json")
        assert os.path.exists(rec_path)
        with open(rec_path, "r") as f:
            data = json.load(f)
        assert data.get("template") == "default"


def test_cli_init_vd(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        sys_argv = ["labfile", "init", tmpdir, "--template", "vd"]
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("sys.argv", sys_argv)
            main()
        captured = capsys.readouterr()
        assert "Initializing LabRecord project" in captured.out
        rec_path = os.path.join(tmpdir, "record.json")
        assert os.path.exists(rec_path)
        with open(rec_path, "r") as f:
            data = json.load(f)
        assert data.get("template") == "vd"


def test_cli_init_invalid_template(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        sys_argv = ["labfile", "init", tmpdir, "-t", "nonexistent_template"]
        with pytest.raises(SystemExit) as exc:
            with pytest.MonkeyPatch.context() as mp:
                mp.setattr("sys.argv", sys_argv)
                main()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "ERROR:" in captured.out
        assert "nonexistent_template" in captured.out


def test_find_manifest_discovery():
    with tempfile.TemporaryDirectory() as tmpdir:
        manifest_p = os.path.join(tmpdir, "main.json")
        with open(manifest_p, "w") as f:
            f.write('{"jobs":[]}')
        
        found = find_manifest(tmpdir)
        assert found == manifest_p
