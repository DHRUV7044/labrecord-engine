import os
import json

# Locate built-in templates directory
PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(PACKAGE_ROOT, "templates")

def list_available_templates():
    """
    Scans templates/ directory and returns a sorted list of template names.
    """
    if not os.path.exists(TEMPLATES_DIR):
        return ["default", "vd"]
    
    templates = []
    for item in sorted(os.listdir(TEMPLATES_DIR)):
        item_path = os.path.join(TEMPLATES_DIR, item)
        if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "template.json")):
            templates.append(item)
    return templates if templates else ["default", "vd"]


def load_template(template_name=None):
    """
    Loads template configuration for template_name.
    If template_name is None, defaults to 'default'.
    If explicitly specified invalid template_name, raises ValueError.
    """
    if not template_name:
        template_key = "default"
    else:
        template_key = str(template_name).strip().lower()

    available = list_available_templates()

    template_file = os.path.join(TEMPLATES_DIR, template_key, "template.json")
    if not os.path.exists(template_file):
        avail_str = ", ".join(available)
        raise ValueError(f"ERROR: Template '{template_name}' not found. Available templates: {avail_str}")

    with open(template_file, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in template file '{template_file}': {e}")
