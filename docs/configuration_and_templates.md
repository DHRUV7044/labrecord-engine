# Configuration, Styling & Built-in Templates

LabRecord Engine separates **document content** (`record.json`) from **styling & page parameters** (`config.json` and template files).

---

## 1. The Configuration Hierarchy

Styling settings are resolved in three layers (highest priority first):

$$\text{Project } \texttt{config.json} \longrightarrow \text{Template } \texttt{template.json} \longrightarrow \text{Built-in } \texttt{DEFAULT\_CONFIG}$$

1. **`config.json`**: Located in your project folder. Overrides specific styling keys for your document.
2. **Template `template.json`**: Located in `templates/<name>/template.json`. Provides defaults for chosen template.
3. **Engine `DEFAULT_CONFIG`**: Hardcoded fallback values.

---

## 2. Complete `config.json` Parameter Reference

```json
{
  "page": {
    "size": "A4",
    "margin_mm": {
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
    "layout_style": "centered",
    "font_size": 14,
    "student_offset_y": 8,
    "exp_no_offset_y": -6,
    "date_offset_y": -16,
    "rule_offset_y": -22,
    "show_header": true,
    "show_date": true,
    "show_rule": true,
    "spacing_after": 20
  },
  "paragraph": {
    "line_spacing": 1.25,
    "spacing_after": 6,
    "spacing_before": 0
  },
  "table": {
    "number_format": "Table {table_num}: {title}",
    "numbering_style": "sequential",
    "font_size": 10,
    "border_width": 0.5,
    "cell_padding": 5,
    "header_bold": true,
    "header_background": "#ffffff",
    "spacing_after": 10
  },
  "figure": {
    "number_format": "Figure {figure_num}: {title}",
    "numbering_style": "sequential"
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
    "show_line_numbers": true,
    "spacing_after": 10
  }
}
```

---

## 3. Disabling the Experiment Header Section

If you do not want the top header section (`EXPERIMENT NO.`, `DATE`, and horizontal rule line) to appear on your pages, disable it in `config.json`:

```json
{
  "experiment_header": {
    "show_header": false
  }
}
```

### Behavior When Disabled:
- Suppresses rendering of `EXPERIMENT NO.`, `DATE`, and rule line.
- Top document margin dynamically tightens to `margin_top` (removing the top header offset).

---

## 4. Built-in Templates

LabRecord Engine comes with three built-in templates:

### 1. `default`
- **Layout Style**: Centered top experiment header.
- **Numbering Style**: Sequential table (`Table 1`) and figure (`Figure 1`) numbering.
- **Usage**: General engineering lab reports.

### 2. `vd`
- **Layout Style**: Split top header (`DATE` left, `EXPERIMENT NO.` right).
- **Numbering Style**: Section-based table (`Table 4.1`) and figure (`Figure 6.1`) numbering.
- **Usage**: Microelectronics & Virtuoso lab records.

### 3. `cao`
- **Layout Style**: Clean header format without mandatory dates or section numbers.
- **Code Settings**: Configured specifically for HDL designs (Verilog/VHDL), RTL schematics, and simulation waveforms.
- **Usage**: Computer Architecture & Organization lab records.

---

## 5. Creating a Custom Template

To create a custom template:

1. Create a folder under `templates/`:
   ```bash
   mkdir -p templates/my_template
   ```
2. Create `templates/my_template/template.json`:
   ```json
   {
     "name": "my_template",
     "page": {
       "size": "A4",
       "margin_mm": { "top": 15, "bottom": 15, "left": 15, "right": 15 }
     },
     "fonts": {
       "body": "Times-Roman",
       "code": "Courier"
     }
   }
   ```
3. Use it in your document JSON:
   ```json
   {
     "template": "my_template",
     "experiments": [ ... ]
   }
   ```
