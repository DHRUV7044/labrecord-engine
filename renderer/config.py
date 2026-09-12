import json
import os

from .template_loader import load_template

MM = 72.0 / 25.4  # ReportLab points per millimetre
A4_WIDTH_MM = 210.0
A4_HEIGHT_MM = 297.0

DEFAULT_CONFIG = {
    "page": {
        "size": "A4",
        "margin": {
            "top": 20,
            "bottom": 20,
            "left": 22,
            "right": 22
        }
    },
    "fonts": {
        "body": "Times-Roman",
        "heading": "Helvetica-Bold",
        "title": "Helvetica-Bold",
        "caption": "Helvetica-Bold",
        "header": "Helvetica-Bold",
        "code": "Courier"
    },
    "font_sizes": {
        "header": 11,
        "experiment_title": 14,
        "section_heading": 12,
        "body": 11,
        "table_cell": 10,
        "table_header": 10,
        "caption": 10,
        "code": 9
    },
    "experiment_header": {
        "font_size": 14,
        "student_offset_y": 8,
        "exp_no_offset_y": 8,
        "date_offset_y": -2,
        "rule_offset_y": -6,
        "spacing_after": 20,
        "show_date": True,
        "show_rule": True
    },
    "paragraph": {
        "line_spacing": 1.25,
        "spacing_after": 6,
        "spacing_before": 0
    },
    "table": {
        "font_size": 10,
        "border_width": 0.5,
        "cell_padding": 5,
        "header_bold": True,
        "header_background": "#ffffff",
        "spacing_after": 10
    },
    "image": {
        "default_gap": 5,
        "caption_font_size": 10,
        "caption_spacing": 4,
        "alignment": "center"
    },
    "code": {
        "font": "Courier",
        "font_size": 9,
        "line_spacing": 1.2,
        "background_color": "#f8f9fa",
        "header_background": "#eaeded",
        "border_color": "#cccccc",
        "line_number_color": "#888888",
        "show_line_numbers": True,
        "spacing_after": 10
    },
    "header": {
        "show_header": True,
        "rule": True
    }
}

class Config:
    def __init__(self, data=None):
        self.data = DEFAULT_CONFIG.copy()
        if data:
            self._merge_dict(self.data, data)

    def _merge_dict(self, base, override):
        for key, val in override.items():
            if isinstance(val, dict) and key in base and isinstance(base[key], dict):
                self._merge_dict(base[key], val)
            else:
                base[key] = val

    def get(self, *keys, default=None):
        curr = self.data
        for k in keys:
            if isinstance(curr, dict) and k in curr:
                curr = curr[k]
            else:
                return default
        return curr

    def _get_margin_val(self, side, default_val):
        m = self.get("page", "margin_mm")
        if isinstance(m, dict) and side in m:
            return float(m[side])
        elif isinstance(m, (int, float)):
            return float(m)
        return float(self.get("page", "margin", side, default=default_val))

    @property
    def margin_top(self):
        return self._get_margin_val("top", 20) * MM

    @property
    def margin_bottom(self):
        return self._get_margin_val("bottom", 20) * MM

    @property
    def margin_left(self):
        return self._get_margin_val("left", 22) * MM

    @property
    def margin_right(self):
        return self._get_margin_val("right", 22) * MM

    @property
    def page_width(self):
        return A4_WIDTH_MM * MM

    @property
    def page_height(self):
        return A4_HEIGHT_MM * MM

    @property
    def printable_width(self):
        return self.page_width - self.margin_left - self.margin_right

    @property
    def printable_height(self):
        return self.page_height - self.margin_top - self.margin_bottom

    def get_font(self, role):
        font_name = self.get("fonts", role, default=None)
        if not font_name:
            if role == "body":
                font_name = "Times-Roman"
            elif role in ("heading", "title", "caption", "header"):
                font_name = "Helvetica-Bold"
            else:
                font_name = "Helvetica"
        return font_name


def load_config(config_path="config.json", template_name=None):
    template_data = load_template(template_name)
    cfg = Config(template_data)

    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_data = json.load(f)
                cfg._merge_dict(cfg.data, user_data)
        except Exception as e:
            print(f"WARNING: Failed to parse {config_path}: {e}. Using template defaults.")

    return cfg

