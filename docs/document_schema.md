# Document JSON Specification & Section Components

In LabRecord Engine, documents are defined using JSON structures (typically `record.json`). The JSON file specifies **WHAT** content to render, while `config.json` and templates control **HOW** it is styled.

---

## Top-Level Document Structure

```json
{
  "template": "default",
  "document": {
    "title": "ENGINEERING LAB RECORD",
    "date": "13/08/2026",
    "name": "Dhruv",
    "roll_number": "220101"
  },
  "images": [ ... ],
  "experiments": [ ... ]
}
```

### Top-Level Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `"template"` | `string` | No | Name of template styling to use (`"default"`, `"vd"`, `"cao"`). Fallback: `"default"`. |
| `"document"` | `object` | No | Metadata about the overall document (e.g. `"title"`, `"date"`, `"name"`, `"roll_number"`). |
| `"name"` / `"student_name"` | `string` | No | Student name displayed at the top of every page above experiment header. |
| `"roll_number"` / `"roll_no"` | `string` | No | Student roll number displayed at the top of every page above experiment header. |
| `"images"` | `array` | No | **Global Image Registry**: Array of image object definitions. |
| `"experiments"` | `array` | **Yes** | Array of experiment objects containing sections and content. |

---

## Experiment Object

Each entry in the `"experiments"` array represents a lab experiment.

```json
{
  "number": 1,
  "type": "main_experiment",
  "title": "CMOS Inverter Design & Analysis",
  "date": "13/08/2026",
  "sections": [ ... ]
}
```

### Experiment Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `"number"` | `integer`/`string` | No | Experiment number (e.g. `1`, `"EXP-01"`). If omitted, `EXPERIMENT NO.` header is suppressed. |
| `"title"` | `string` | **Yes** | Title of the experiment. |
| `"type"` | `string` | No | Optional experiment category or tag (e.g., `"main_experiment"`). |
| `"date"` | `string` | No | Experiment date string (e.g., `"13/08/2026"`). |
| `"sections"` | `array` | **Yes** | Array of section objects belonging to this experiment. |

---

## Section Components

Sections are the primary building blocks of an experiment. LabRecord Engine supports four core section types:
1. [`text`](#1-text-section) — Written paragraphs and LaTeX math formulas.
2. [`code`](#2-code-section) — Code blocks loaded from files or inline code strings.
3. [`table`](#3-table-section) — Data tables, CSV file imports, and calculated expressions.
4. [`image`](#4-image-section) — Multi-image grid layouts, column stacks, and freeboxes.

---

### Common Section Parameters

Every section object supports these common fields:

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `"type"` | `string` | `"text"` | Type of section: `"text"`, `"code"`, `"table"`, or `"image"`. |
| `"title"` | `string` | `""` | Section title (e.g. `"AIM"`, `"THEORY"`, `"VERILOG CODE"`). |
| `"number"` | `integer`/`string` | `""` | Optional section number (e.g., `1`, `"2.1"`). Omit to hide section numbers. |
| `"new_page"` | `boolean` | `false` | If `true`, forces a page break before rendering this section. |

---

### 1. `text` Section

Used for explanatory prose, list items, and mathematical equations.

```json
{
  "type": "text",
  "number": 1,
  "title": "THEORY",
  "new_page": false,
  "text": [
    "A static CMOS inverter consists of PMOS pull-up and NMOS pull-down transistors.",
    "The switching threshold occurs where $V_{in} = V_{out}$. Noise margins: $NM_H = V_{OH} - V_{IH}$."
  ]
}
```

#### Parameters
- `"text"`: `string` or `array of strings`. Each string becomes a formatted paragraph.
- **LaTeX Math Parsing**:
  - Inline math: `$V_{DD} = 1.8V$`
  - Display math: `$$\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$$`

---

### 2. `code` Section

Used for displaying source code files (Verilog, VHDL, Python, C++, Spice) or inline code strings.

```json
{
  "type": "code",
  "number": "2.1",
  "title": "Half Adder Design Code",
  "file": "rtl/ha.vhd",
  "language": "VHDL",
  "show_line_numbers": true
}
```

#### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `"file"` / `"path"` / `"code_file"` | `string` | `None` | Path to source code file (relative to document dir). |
| `"code"` | `string`/`array` | `""` | Inline code string or list of lines (used if no file path is specified). |
| `"language"` / `"lang"` | `string` | `""` | Language name badge displayed in top header (e.g. `"Verilog"`, `"Python"`). |
| `"show_line_numbers"` | `boolean` | `true` | Show or hide line numbers in code margin. |

---

### 3. `table` Section

Used for data tables, CSV file imports, and calculation tables.

#### A. CSV File Import
```json
{
  "type": "table",
  "title": "Experimental Data",
  "csv": "data/results.csv",
  "delimiter": ","
}
```

#### B. Row / Column Based Tables
```json
{
  "type": "table",
  "title": "Design Parameters",
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
}
```

#### C. Comma-Shorthand Rows
```json
{
  "type": "table",
  "title": "Shorthand Table",
  "elements": [
    "Parameter , Technology , $V_{DD}$ , PMOS Width",
    "Value     , 180 nm     , 1.8 V  , 400 nm"
  ]
}
```

#### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `"csv"` / `"csv_file"` | `string` | `None` | Path to `.csv` file to render as table. |
| `"delimiter"` | `string` | `","` | CSV column delimiter character. |
| `"element_type"` | `string` | `"row"` | Table orientation: `"row"` or `"column"`. |
| `"elements"` | `array` | `[]` | Array of row/column dictionaries or shorthand strings. |
| `"tables"` | `array` | `[]` | Array of sub-table objects (used when multiple tables exist in one section). |

---

### 4. `image` Section

Used for placing schematics, waveforms, and layout screenshots with aspect-ratio tree structures.

```json
{
  "type": "image",
  "title": "Simulation Waveforms",
  "images": [
    {
      "id": "schematic",
      "path": "images/schematic.png",
      "title": "Circuit Schematic"
    },
    {
      "id": "waveform",
      "path": "images/waveform.png",
      "title": "Transient Response"
    }
  ],
  "subsections": [
    {
      "title": "Page 1 - Circuit & Simulation Layout",
      "layout": {
        "type": "column",
        "elements": [
          "schematic",
          "waveform"
        ]
      }
    }
  ]
}
```

#### Image Registry Entry Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `"id"` | `string` | **Required** | Unique image identifier referenced in layout nodes. |
| `"path"` | `string` | **Required** | Path to image file (`.png`, `.jpg`, `.svg`). |
| `"title"` | `string` | `""` | Figure caption text. |
| `"rotation"` | `integer` | `0` | Image rotation angle in degrees (`0`, `90`, `180`, `270`). |

#### Layout Node Types

| Node Type | Description |
| :--- | :--- |
| `"column"` | Stacks child elements vertically. |
| `"row"` | Places child elements side-by-side horizontally. |
| `"ref"` / `string` | Image ID reference string. |
| `"freebox"` | Absolutely positioned overlay box (`position: {x, y}`, `size: {width, height}`). |
