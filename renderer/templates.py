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
        "date": "20/08/2026"
    },
    "images": [
        {
            "id": 9,
            "path": "dc post layout.png",
            "title": "Dc Post Layout",
            "rotation": 270
        },
        {
            "id": 8,
            "path": "dc pre layout.png",
            "title": "Dc Pre Layout",
            "rotation": 270
        },
        {
            "id": 10,
            "path": "dc pre vs post.png",
            "title": "Dc Pre Vs Post",
            "rotation": 270
        },
        {
            "id": 3,
            "path": "drc.png",
            "title": "Drc",
            "rotation": 270
        },
        {
            "id": 2,
            "path": "layout.png",
            "title": "Layout",
            "rotation": 270
        },
        {
            "id": 4,
            "path": "lvs.png",
            "title": "Lvs",
            "rotation": 270
        },
        {
            "id": 5,
            "path": "quantus.png",
            "title": "Quantus",
            "rotation": 270
        },
        {
            "id": 1,
            "path": "schematic.png",
            "title": "Schematic",
            "rotation": 270
        },
        {
            "id": 6,
            "path": "symbol.png",
            "title": "Symbol",
            "rotation": 270
        },
        {
            "id": 7,
            "path": "tb.png",
            "title": "Tb",
            "rotation": 270
        },
        {
            "id": 12,
            "path": "tran post layout.png",
            "title": "Tran Post Layout",
            "rotation": 270
        },
        {
            "id": 11,
            "path": "tran pre layout.png",
            "title": "Tran Pre Layout",
            "rotation": 270
        },
        {
            "id": 13,
            "path": "tran pre vs post.png",
            "title": "Tran Pre Vs Post",
            "rotation": 270
        }
    ],
    "experiments": [
        {
            "number": 2,
            "type": "assignment",
            "title": "CMOS Inverter Design & Analysis",
            "date": "20/08/2026",
            "sections": [
                {
                    "type": "text",
                    "number": 1,
                    "title": "AIM",
                    "text": "To design and verify the schematic and layout of a Dynamic CMOS 2 input nand using 180 nm technology, and compare its pre-layout and post-layout simulation results"
                },
                {
                    "type": "text",
                    "number": 2,
                    "title": "TOOL",
                    "text": "Cadence Virtuoso"
                },
                {
                    "type": "text",
                    "number": 3,
                    "title": "THEORY",
                    "text": [
                        "A 2-input Dynamic CMOS NAND gate operates in two distinct phases: precharge and evaluation, controlled by a clock signal.",
                        "During the precharge phase, when the clock is LOW, the precharge PMOS transistor is ON and charges the output node to $V_{dd}$. The pull-down network (PDN) is disabled during this phase, so the output is precharged to logic HIGH.",
                        "During the evaluation phase, when the clock becomes HIGH, the precharge transistor is turned OFF and the PDN is enabled. The PDN consists of two NMOS transistors connected in series and controlled by inputs $A$ and $B$. The output discharges to LOW only when both $A$ and $B$ are HIGH. For any other input combination, the output retains its precharged HIGH state.",
                        "The logic function of the 2-input Dynamic CMOS NAND gate is $Y=\\overline{A\\cdot B}$. Since the output is already precharged to HIGH before evaluation, no LOW-to-HIGH transition occurs during evaluation. Therefore, $t_{pLH}=0$ for the evaluation operation, while the relevant delay is $t_{pHL}$ during discharge through the PDN.",
                        "The schematic of the 2-input Dynamic CMOS NAND gate is designed and simulated using 180 nm CMOS technology in Cadence Virtuoso. The corresponding physical layout is designed and verified using design-rule checking (DRC) and layout-versus-schematic (LVS) verification.",
                        "Pre-layout and post-layout simulations are then performed and compared to analyze the effect of layout parasitics on propagation delay and overall circuit performance."
                    ]
                },
                {
                    "type": "table",
                    "number": 4,
                    "title": "Tables",
                    "tables": [
                        {
                            "title": "CMOS Inverter Design Parameters",
                            "csv": "parameter.csv"
                        },
                        {
                            "title": "Result comparision (pre layout vs post layout)",
                            "csv": "pre_vs_post.csv"
                        },
                        {
                            "title": "Result comparision (static vs dynamic for pre layout)",
                            "csv": "pre_static_vs_dyna.csv"
                        },
                        {
                            "title": "Result comparision (static vs dynamic for post layout)",
                            "csv": "post_static_vs_dyna.csv"
                        }
                    ]
                },
                {
                    "type": "text",
                    "number": 5,
                    "title": "CALCULATION",
                    "new_page": True,
                    "text": [
                        "$N_{MH}=V_{OH}-V_{IH}=1.8-0.836654=0.963346V\\approx0.9633V$",
                        "$N_{ML}=V_{IL}-V_{OL}=0.555495-0=0.555495V$",
                        "$N_{MH(post)}=V_{OH}-V_{IH}=1.8-0.8369212=0.9630788V\\approx0.9631V$",
                        "$N_{ML(post)}=V_{IL}-V_{OL}=0.5554912-0=0.5554912V$",
                        "$t_{HL(pre)}=(37.0219-37.0075)*1000=14.4ps$",
                        "$t_{HL(post)}=(37.0302-37.0075)*1000=22.7ps$",
                        "$t_{LH(pre)}=0ps$",
                        "$t_{LH(post)}=0ps$",
                        "$t_{p(pre)}=37.0219ps$",
                        "$t_{p(post)}=37.0302ps$",
                        "$t_{r(pre)}=(20.0648-20.0185)*1000=46.3ps$",
                        "$t_{r(post)}=(20.1034-20.0234)*1000=80.0ps$",
                        "$t_{f(pre)}=(37.0376-37.0137)*1000=23.9ps$",
                        "$t_{f(post)}=(37.056-37.0154)*1000=40.6ps$",
                        "$Error_{V_{th}}=(0.0004/715.711)*100=0.0001%$",
                        "$Error_{V_{IH}}=(0.2672/836.654)*100=0.0319%$",
                        "$Error_{V_{IL}}=(0.0038/555.495)*100=0.0007%$",
                        "$Error_{N_{MH}}=(0.0002/0.9633)*100=0.0208%$",
                        "$Error_{N_{ML}}=(0.0000038/0.555495)*100=0.0007%$",
                        "$Error_{t_p}=(0.0083/37.0219)*100=0.0224%$"
                    ]
                },
                {
                    "type": "image",
                    "title": "Circuit Diagrams & Waveforms",
                    "new_page": True,
                    "subsections": [
                        {
                            "title": "Page 1",
                            "layout": {
                                "type": "column",
                                "elements": [
                                    "1"
                                ]
                            }
                        },
                        {
                            "title": "Page 2",
                            "layout": {
                                "type": "column",
                                "elements": [
                                    "2"
                                ]
                            }
                        },
                        {
                            "title": "Page 3",
                            "layout": {
                                "type": "column",
                                "elements": [
                                    "3"
                                ]
                            }
                        },
                        {
                            "title": "Page 4",
                            "layout": {
                                "type": "column",
                                "elements": [
                                    "4"
                                ]
                            }
                        },
                        {
                            "title": "Page 5",
                            "layout": {
                                "type": "column",
                                "elements": [
                                    "5"
                                ]
                            }
                        },
                        {
                            "title": "Page 6",
                            "layout": {
                                "type": "column",
                                "elements": [
                                    "6"
                                ]
                            }
                        },
                        {
                            "title": "Page 7",
                            "layout": {
                                "type": "column",
                                "elements": [
                                    "7"
                                ]
                            }
                        },
                        {
                            "title": "Page 8",
                            "layout": {
                                "type": "column",
                                "elements": [
                                    "8"
                                ]
                            }
                        },
                        {
                            "title": "Page 9",
                            "layout": {
                                "type": "column",
                                "elements": [
                                    "9"
                                ]
                            }
                        },
                        {
                            "title": "Page 10",
                            "layout": {
                                "type": "column",
                                "elements": [
                                    "10"
                                ]
                            }
                        },
                        {
                            "title": "Page 11",
                            "layout": {
                                "type": "column",
                                "elements": [
                                    "11"
                                ]
                            }
                        },
                        {
                            "title": "Page 12",
                            "layout": {
                                "type": "column",
                                "elements": [
                                    "12"
                                ]
                            }
                        },
                        {
                            "title": "Page 13",
                            "layout": {
                                "type": "column",
                                "elements": [
                                    "13"
                                ]
                            }
                        }
                    ]
                },
                {
                    "type": "text",
                    "number": 7,
                    "title": "RESULT",
                    "text": [
                        "The 2-input Dynamic CMOS NAND gate was successfully designed and verified using 180 nm CMOS technology, and the pre-layout and post-layout simulation results were compared to evaluate the effect of layout parasitics on circuit performance."
                    ]
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

import copy

def init_project(target_dir=".", template_name="default", make_image_dir=False, force=False, name=None, roll_number=None):
    target_dir = os.path.abspath(target_dir)
    os.makedirs(target_dir, exist_ok=True)

    template_key = template_name.lower() if template_name else "default"
    available = list_available_templates()
    if template_key not in available:
        avail_str = "\n  ".join(available)
        raise ValueError(f"ERROR: Template '{template_name}' not found.\nAvailable templates:\n  {avail_str}")

    template_files = copy.deepcopy(TEMPLATES.get(template_key, TEMPLATES["default"]))
    if name:
        template_files["record.json"].setdefault("document", {})["name"] = name
    if roll_number:
        template_files["record.json"].setdefault("document", {})["roll_number"] = roll_number

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

