# LabRecord Engine — Publication-Ready A4 Document Typesetting

**LabRecord Engine** is a python document typesetting engine designed for engineering laboratory reports (VLSI, Virtuoso, CAO, Microelectronics, and Circuit Design).

It parses document structure and content written in standard JSON files, applies template styling configurations, handles page flow and breaks, renders LaTeX math expressions and tables, computes image layout trees, formats source code files, evaluates automatic table calculations, and outputs clean, publication-ready A4 PDF files.

---

## Documentation Index

Explore detailed component references, parameter lists, and usage guides:

- 📖 **[CLI User Guide (`docs/cli.md`)](docs/cli.md)** — Complete command reference (`init`, `generate`, `scan`, `csv`, `templates`).
- 📋 **[Document JSON Schema & Components (`docs/document_schema.md`)](docs/document_schema.md)** — Section components (`text`, `code`, `table`, `image`), parameters, and layout trees.
- 📊 **[Tables, CSV Imports & Calculations (`docs/tables_and_calculations.md`)](docs/tables_and_calculations.md)** — Row/Column tables, CSV imports, relative cell references, and arithmetic functions (`$avg`, `$perr`).
- 💻 **[Code Sections & File Imports (`docs/code_sections.md`)](docs/code_sections.md)** — Importing Verilog/VHDL/Python code files, line numbers, language badges, and styling.
- 🎨 **[Configuration, Styling & Built-in Templates (`docs/configuration_and_templates.md`)](docs/configuration_and_templates.md)** — `config.json` parameters, header toggles, and built-in templates (`default`, `vd`, `cao`).

---

## Key Features

- ⚡ **Multi-Template Architecture**: Select between built-in templates (`default`, `vd`, `cao`) or create custom templates.
- 💻 **Code Import Section**: Directly render Verilog, VHDL, Python, C++, and Spice code files (`"type": "code"`) with monospace styling, line numbers, and language header badges.
- 📊 **CSV File Importing & Comma Shorthands**: Render CSV files (`"csv": "data.csv"`) or write comma-separated shorthand rows directly into tables.
- 🧮 **Automated Table Calculations**: Perform cell arithmetic (`r1e1 - r2e2`), relative references (`re1`, `ce2`), and use built-in functions (`$avg(...)`, `$perr(...)`).
- 🖼️ **Aspect-Ratio Image Layout Engine**: Flexible column, row, grid, and freebox image positioning with rotation and scaling.
- 📐 **LaTeX Math Support**: Inline (`$...$`) and display (`$$...$$`) mathematical typesetting.
- ⚙️ **Configurable Headers & Top Margins**: Hide top experiment headers (`"show_header": false`) with dynamic top margin adjustment.

---

## 1. Quick Start Installation

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

## 2. Quick Command Reference

```bash
# Initialize a new project with the CAO template
labfile init --template cao

# Initialize and scan an image folder
labfile init --scan screenshots/ -t vd

# Import a CSV file into record.json
labfile csv measurements.csv --title "DC Sweep Results"

# Generate publication-ready PDFs from main.json
labfile generate

# List all available built-in templates
labfile templates
```

---

## 3. Quick JSON Example (`record.json`)

```json
{
  "template": "cao",
  "document": {
    "title": "COMPUTER ARCHITECTURE & ORGANIZATION LAB RECORD"
  },
  "images": [
    {
      "id": "schematic",
      "path": "design.png",
      "title": "RTL Schematic"
    }
  ],
  "experiments": [
    {
      "title": "Ripple Carry Adder (RCA) Design",
      "sections": [
        {
          "type": "text",
          "title": "AIM",
          "text": "To design an 8-bit Ripple Carry Adder using VHDL and verify switching threshold $V_{TH}$."
        },
        {
          "type": "code",
          "title": "VHDL Design Code",
          "file": "rtl/rca8.vhd",
          "language": "VHDL"
        },
        {
          "type": "table",
          "title": "Experimental Measurements",
          "csv": "data/results.csv"
        },
        {
          "type": "image",
          "title": "RTL Schematic Layout",
          "subsections": [
            {
              "title": "Circuit Layout",
              "layout": {
                "type": "column",
                "elements": ["schematic"]
              }
            }
          ]
        }
      ]
    }
  ]
}
```

---

## Directory Structure

```text
labrecord-engine/
├── labfile               # Executable CLI launcher script
├── main.json             # Multi-job build manifest
├── config.json           # Styling configuration defaults
├── Makefile              # Build automation & test runner
├── README.md             # Main overview & quick start index
│
├── docs/                 # Detailed User Guides
│   ├── cli.md                        # CLI reference
│   ├── document_schema.md            # Document JSON schema & section components
│   ├── tables_and_calculations.md    # Tables, CSV import & expression engine
│   ├── code_sections.md              # Code section & file import parameters
│   └── configuration_and_templates.md# Config parameters & template guide
│
├── templates/            # Built-in document templates
│   ├── default/          # Default template configuration
│   ├── vd/               # VD lab record template configuration
│   └── cao/              # CAO lab record template configuration
│
├── renderer/             # Core typesetting & compiling engine
├── labs/                 # Example reference lab JSON documents
└── tests/                # Comprehensive regression test suite
```
