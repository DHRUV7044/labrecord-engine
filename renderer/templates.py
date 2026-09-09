import os
import json
from .template_loader import list_available_templates


DEFAULT_MAIN_JSON = {
    "jobs": [
        {
            "input": "record.json",
            "output": "output/lab_record.pdf"
        }
    ]
}

DEFAULT_CONFIG_JSON = {
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
        "caption": 10
    },
    "experiment_header": {
        "font_size": 14,
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
    "header": {
        "show_header": True,
        "rule": True
    }
}

DEFAULT_RECORD_JSON = {
    "template": "default",
    "document": {
        "title": "ENGINEERING LAB RECORD",
        "date": "13/08/2026"
    },
    "images": [
        {
            "id": "example_image",
            "path": "example.png",
            "title": "Example Circuit Diagram"
        }
    ],
    "experiments": [
        {
            "number": 1,
            "type": "main_experiment",
            "title": "CMOS Inverter Characterization",
            "date": "13/08/2026",
            "sections": [
                {
                    "type": "text",
                    "number": 1,
                    "title": "AIM",
                    "new_page": False,
                    "text": "To design and simulate a static CMOS inverter using 180 nm technology and determine its DC voltage transfer characteristics and noise margins."
                },
                {
                    "type": "text",
                    "number": 2,
                    "title": "THEORY",
                    "new_page": False,
                    "text": [
                        "A static CMOS inverter consists of a PMOS pull-up and an NMOS pull-down transistor. The switching threshold voltage $V_{TH}$ occurs where $V_{in} = V_{out}$.",
                        "The noise margins are defined as $NM_H = V_{OH} - V_{IH}$ and $NM_L = V_{IL} - V_{OL}$."
                    ]
                },
                {
                    "type": "table",
                    "number": 3,
                    "title": "DESIGN PARAMETERS",
                    "new_page": False,
                    "element_type": "column",
                    "elements": [
                        {
                            "title": "Parameter",
                            "entries": ["Technology", "$V_{DD}$", "PMOS Width ($W_p$)", "NMOS Width ($W_n$)"]
                        },
                        {
                            "title": "Value",
                            "entries": ["180 nm", "1.8 V", "400 nm", "400 nm"]
                        }
                    ]
                },
                {
                    "type": "text",
                    "number": 4,
                    "title": "RESULT",
                    "new_page": False,
                    "text": "The static CMOS inverter was successfully modeled and simulated."
                }
            ]
        }
    ]
}

VD_RECORD_JSON = {
    "template": "vd",
    "document": {
        "title": "ENGINEERING LAB RECORD",
        "date": "13/08/2026"
    },
    "images": [
        {
            "id": "example_image",
            "path": "example.png",
            "title": "Example Circuit Diagram"
        }
    ],
    "experiments": [
        {
            "number": 1,
            "title": "CMOS Inverter Design & Analysis",
            "date": "13/08/2026",
            "sections": [
                {
                    "type": "text",
                    "number": 1,
                    "title": "AIM",
                    "text": "To design and simulate a CMOS inverter using Cadence Virtuoso and analyze its DC characteristics."
                },
                {
                    "type": "text",
                    "number": 2,
                    "title": "TOOL",
                    "text": "Cadence Virtuoso, Spectre Simulator, 180nm PDK."
                },
                {
                    "type": "text",
                    "number": 3,
                    "title": "THEORY",
                    "text": "The CMOS inverter consists of an NMOS driver and PMOS load. The switching threshold $V_{TH}$ is determined when $V_{in} = V_{out}$."
                },
                {
                    "type": "table",
                    "number": 4,
                    "title": "DESIGN PARAMETERS",
                    "tables": [
                        {
                            "title": "CMOS Inverter Design Parameters",
                            "element_type": "column",
                            "elements": [
                                {
                                    "title": "Parameter",
                                    "entries": ["Technology", "$V_{DD}$", "$W_p / L_p$", "$W_n / L_n$"]
                                },
                                {
                                    "title": "Value",
                                    "entries": ["180 nm", "1.8 V", "2.0", "1.0"]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "text",
                    "number": 5,
                    "title": "CALCULATION",
                    "text": "Calculated noise margin: $NM_H = V_{OH} - V_{IH} = 1.8V - 1.0V = 0.8V$."
                },
                {
                    "type": "text",
                    "number": 6,
                    "title": "RESULT",
                    "text": "The static CMOS inverter was successfully designed and simulated."
                }
            ]
        }
    ]
}

CAO_RECORD_JSON = {
    "template": "cao",
    "document": {
        "title": "COMPUTER ARCHITECTURE & ORGANIZATION LAB RECORD"
    },
    "images": [
        {
            "id": "design",
            "path": "design.png",
            "title": "Design",
            "rotation": 0
        },
        {
            "id": "tb",
            "path": "tb.png",
            "title": "Tb",
            "rotation": 0
        },
        {
            "id": "waveform",
            "path": "waveform.png",
            "title": "Waveform",
            "rotation": 0
        }
    ],
    "experiments": [
        {
            "title": "Lab 1: Ripple Carry Adder (RCA)",
            "sections": [
                {
                    "type": "code",
                    "language": "Verilog"
                },
                {
                    "type": "code",
                    "language": "Verilog"
                },
                {
                    "type": "code",
                    "language": "Verilog"
                },
                {
                    "type": "code",
                    "language": "Verilog"
                },
                {
                    "type": "image",
                    "title": "Screenshot of Code",
                    "new_page": True,
                    "subsections": [
                        {
                            "title": "Page 1 - Circuit & Simulation Layout",
                            "layout": {
                                "type": "column",
                                "elements": [
                                    "design",
                                    "tb"
                                ]
                            }
                        }
                    ]
                },
                {
                    "type": "image",
                    "title": "Waveform",
                    "new_page": False,
                    "subsections": [
                        {
                            "title": "Page 1 - Circuit & Simulation Layout",
                            "layout": {
                                "type": "column",
                                "elements": [
                                    "waveform"
                                ]
                            }
                        }
                    ]
                }
            ]
        }
    ]
}

TEMPLATES = {
    "default": {
        "main.json": DEFAULT_MAIN_JSON,
        "config.json": DEFAULT_CONFIG_JSON,
        "record.json": DEFAULT_RECORD_JSON
    },
    "vd": {
        "main.json": DEFAULT_MAIN_JSON,
        "config.json": DEFAULT_CONFIG_JSON,
        "record.json": VD_RECORD_JSON
    },
    "cao": {
        "main.json": DEFAULT_MAIN_JSON,
        "config.json": DEFAULT_CONFIG_JSON,
        "record.json": CAO_RECORD_JSON
    }
}

def init_project(target_dir=".", template_name="default", make_image_dir=False, force=False):
    target_dir = os.path.abspath(target_dir)
    os.makedirs(target_dir, exist_ok=True)

    template_key = template_name.lower() if template_name else "default"
    available = list_available_templates()
    if template_key not in available:
        avail_str = "\n  ".join(available)
        raise ValueError(f"ERROR: Template '{template_name}' not found.\nAvailable templates:\n  {avail_str}")

    template_files = TEMPLATES.get(template_key, TEMPLATES["default"])

    print(f"Initializing LabRecord project in {target_dir} (template: '{template_key}')...")

    # Create files
    for filename, content_dict in template_files.items():
        file_path = os.path.join(target_dir, filename)
        if os.path.exists(file_path) and not force:
            print(f"  {filename} already exists - skipped")
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(content_dict, f, indent=4)
            print(f"  created {filename}")

    # Ensure output directory exists
    output_dir = os.path.join(target_dir, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print("  created output/")

    # Optional image directory flag
    if make_image_dir:
        images_dir = os.path.join(target_dir, "images")
        if not os.path.exists(images_dir):
            os.makedirs(images_dir, exist_ok=True)
            print("  created images/")
        else:
            print("  images/ already exists")

    print("\nProject initialized successfully.")

