LabRecord Engine is a Python-based document typesetting and PDF generation engine specifically designed for engineering laboratory records (e.g. VLSI, Microelectronics, Circuit Design).

The engine parses document structure and content written in standard JSON files, applies template styling configurations, handles page flow and breaks, renders LaTeX math expressions and tables, computes image layout trees, and outputs clean, publication-ready A4 PDF files.

---

## 1. Installation

Install the package and the `labfile` command line tool:

```bash
# Clone the repository
git clone <repo-url>
cd labrecord-engine

# Make executable available in PATH
chmod +x labfile
mkdir -p ~/.local/bin
cp labfile ~/.local/bin/
```

Verify installation:

```bash
labfile --help
```

---

## 2. CLI Usage (`labfile`)

The `labfile` CLI executable provides project initialization, template listing, PDF generation, and image scanning commands:

```bash
LabRecord Engine — PDF Typesetting & Build CLI

Commands:
  init       Initialize a LabRecord project
  generate   Generate PDFs from main.json
  scan       Scan directory for images and add them to document JSON
  templates  List available document templates
```

---

## 3. Template System

LabRecord Engine includes a configuration-driven template architecture. Built-in templates:

1. **`default`**: Standard document formatting layout.
2. **`vd`**: Lab record format reproducing VD laboratory record reference structure with split top experiment header (`DATE` left, `EXPERIMENT NO.` right) and section-resetting table (`Table 4.1`) and figure (`Figure 6.1`) numbering.

### Listing Available Templates
```bash
labfile templates
```

### Template vs. Document Content
- **Template (`templates/<name>/template.json`)**: Controls **HOW** the document is rendered (page margins, fonts, font sizes, experiment header layout, section heading styles, table numbering style, figure caption format, spacing).
- **Document JSON (`record.json`)**: Controls **WHAT** the document contains (experiment number, type, date, section titles like `AIM`, `THEORY`, `TABLE`, `CALCULATION`, `RESULT`, text paragraphs, LaTeX formulas, table data, image layouts).

Templates **do NOT** contain hardcoded section content or experiment titles.

### Specifying Template in Document JSON
```json
{
    "template": "vd",
    "document": {
        "title": "ENGINEERING LAB RECORD",
        "date": "13/08/2026"
    },
    "images": [ ... ],
    "experiments": [ ... ]
}
```
If `"template"` is omitted, `"default"` is used automatically as fallback.

---

## 4. Project Initialization (`labfile init`)

To create a new LabRecord Engine project:

```bash
# Basic initialization using default template
labfile init

# Initialize project using VD template
labfile init -t vd
# or:
labfile init --template vd

# Specify a target directory
labfile init /path/to/my_project -t vd

# Initialize and automatically scan a directory for images
labfile init --scan screenshots/ -t vd
```

Default files created:
- `main.json` (Build manifest)
- `config.json` (Optional user styling overrides)
- `record.json` (Document content & global image registry configured with chosen template)
- `output/` (Directory for generated PDFs)

---

## 5. Image Registry & Layout Engine (`labfile scan`)

Images are declared in the top-level `images` array (Global Image Registry) and referenced by unique ID in section layout nodes:

```json
{
    "images": [
        {
            "id": "schematic",
            "path": "../cadence/schematic.png",
            "title": "CMOS Inverter Schematic"
        }
    ]
}
```

Scan any directory for images and automatically add them to `record.json`:

```bash
labfile scan screenshots/ -r record.json
```

---

## 6. Generating PDFs (`labfile generate`)

Run generation from inside a project directory or from **any arbitrary directory**:

```bash
# Generate PDFs using project in current directory
labfile generate

# Generate PDFs using explicit manifest path
labfile generate /path/to/my_project/main.json
```

---

## 7. Directory Structure

```text
labrecord-engine/
├── labfile               # Executable CLI launcher script
├── generate.py           # Legacy script wrapper
├── main.json             # Multi-job build manifest
├── config.json           # Styling configuration defaults
├── Makefile              # Build automation & test runner
├── README.md             # Documentation
├── pyproject.toml        # Python package metadata
│
├── templates/            # Built-in document templates
│   ├── default/
│   │   └── template.json # Default template configuration
│   └── vd/
│       └── template.json # VD lab record template configuration
│
├── schema/
│   └── lab_schema.json   # Document JSON schema specification
│
├── renderer/
│   ├── __init__.py
│   ├── cli.py            # CLI entry point (init, generate, scan, templates)
│   ├── template_loader.py# Shared template loader & validator
│   ├── scanner.py        # Image directory scanner & registry merger
│   ├── templates.py      # Project template generator (init)
│   ├── config.py         # Configuration loader & margin calculations
│   ├── document.py       # Document models & Global Image Registry
│   ├── layout.py         # Aspect-ratio space distribution & recursive layout
│   ├── pages.py          # Top experiment header & section headings
│   ├── text.py           # Paragraph builder & LaTeX mathtext parser
│   ├── tables.py         # Table flowables (Row & Column modes)
│   ├── images.py         # Pillow image reader, rotation, scaling & drawing
│   └── pdf.py            # ReportLab document compiler
│
├── labs/
│   ├── example_lab.json     # Reference default lab JSON
│   └── vd_example_lab.json  # Reference VD lab JSON
│
├── tests/                # Comprehensive regression test suite
└── output/               # Directory where generated PDFs are stored
```

