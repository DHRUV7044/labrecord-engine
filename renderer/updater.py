import os
import json
import copy

from .config import DEFAULT_CONFIG
from .template_loader import load_template

DEFAULT_MAIN_JSON = {
    "jobs": [
        {
            "input": "record.json",
            "output": "output/lab_record.pdf"
        }
    ]
}


def deep_update_dict(target, default):
    """
    Recursively merges missing keys from `default` dict into `target` dict.
    Preserves all existing user values in `target`.
    Returns (target, list_of_added_key_paths).
    """
    added_keys = []

    def _merge(t, d, path=""):
        for k, v in d.items():
            curr_path = f"{path}.{k}" if path else k
            if k not in t:
                t[k] = copy.deepcopy(v)
                added_keys.append(curr_path)
            elif isinstance(t[k], dict) and isinstance(v, dict):
                _merge(t[k], v, curr_path)

    _merge(target, default)
    return target, added_keys


def update_project(target_dir="."):
    """
    Updates existing project JSON files (config.json, record.json, main.json)
    by injecting missing default options added in newer template/schema versions,
    without overwriting existing user settings.
    """
    target_dir = os.path.abspath(target_dir)
    if not os.path.exists(target_dir):
        raise FileNotFoundError(f"Project directory not found: {target_dir}")

    config_path = os.path.join(target_dir, "config.json")
    record_path = os.path.join(target_dir, "record.json")
    main_path = os.path.join(target_dir, "main.json")

    results = {
        "config_updated": False,
        "config_added_keys": [],
        "record_updated": False,
        "record_added_keys": [],
        "main_updated": False,
        "main_added_keys": []
    }

    # Determine template name from record.json if available
    template_name = "default"
    if os.path.exists(record_path):
        try:
            with open(record_path, "r", encoding="utf-8") as rf:
                r_data = json.load(rf)
                template_name = r_data.get("template", "default")
        except Exception:
            pass

    # Build reference default config combining DEFAULT_CONFIG and template defaults
    base_default_config = copy.deepcopy(DEFAULT_CONFIG)
    try:
        tpl_data = load_template(template_name)
        base_default_config, _ = deep_update_dict(base_default_config, tpl_data)
    except Exception:
        pass

    # 1. Update config.json
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            try:
                user_config = json.load(f)
            except Exception as e:
                raise ValueError(f"Failed to parse existing config.json: {e}")

        updated_config, added_cfg = deep_update_dict(user_config, base_default_config)
        if added_cfg:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(updated_config, f, indent=4)
            results["config_updated"] = True
            results["config_added_keys"] = added_cfg

    # 2. Update record.json
    if os.path.exists(record_path):
        with open(record_path, "r", encoding="utf-8") as f:
            try:
                rec_data = json.load(f)
            except Exception as e:
                raise ValueError(f"Failed to parse existing record.json: {e}")

        added_rec = []
        doc_obj = rec_data.setdefault("document", {})
        if "name" not in doc_obj:
            doc_obj["name"] = ""
            added_rec.append("document.name")
        if "roll_number" not in doc_obj:
            doc_obj["roll_number"] = ""
            added_rec.append("document.roll_number")

        if added_rec:
            with open(record_path, "w", encoding="utf-8") as f:
                json.dump(rec_data, f, indent=4)
            results["record_updated"] = True
            results["record_added_keys"] = added_rec

    # 3. Update main.json
    if os.path.exists(main_path):
        with open(main_path, "r", encoding="utf-8") as f:
            try:
                main_data = json.load(f)
            except Exception:
                main_data = {}

        updated_main, added_main = deep_update_dict(main_data, DEFAULT_MAIN_JSON)
        if added_main:
            with open(main_path, "w", encoding="utf-8") as f:
                json.dump(updated_main, f, indent=4)
            results["main_updated"] = True
            results["main_added_keys"] = added_main

    return results
