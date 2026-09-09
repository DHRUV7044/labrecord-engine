# Code Sections & File Imports Guide

LabRecord Engine provides built-in code formatting sections (`"type": "code"`) designed specifically for HDL designs (Verilog, VHDL), C/C++, Python scripts, Spice netlists, and assembly code.

---

## 1. Importing Code from External Files

Specify `"type": "code"` and provide the file path using `"file"`, `"path"`, `"code_file"`, or `"source"`.

```json
{
  "type": "code",
  "number": "3.1",
  "title": "Verilog Module for 8-bit RCA",
  "file": "rtl/rca8.v",
  "language": "Verilog",
  "show_line_numbers": true
}
```

### File Resolution Rules
- **Relative Paths**: Resolved relative to the directory containing your document JSON (`record.json`). Example: `"file": "rtl/adder.v"` resolves to `./rtl/adder.v`.
- **Absolute Paths**: Resolved directly from the root filesystem. Example: `"file": "/home/user/proj/top.v"`.

---

## 2. Inline Code Blocks

If you want to write code snippets directly in your document JSON without an external file, use `"code"`:

```json
{
  "type": "code",
  "title": "Testbench Simulation Loop",
  "code": "initial begin\n    clk = 0;\n    forever #5 clk = ~clk;\nend",
  "language": "Verilog",
  "show_line_numbers": false
}
```

You can also provide a list of lines for `"code"`:

```json
{
  "type": "code",
  "title": "Python Script",
  "code": [
    "def calculate_margin(voh, vih):",
    "    return voh - vih",
    "",
    "print(calculate_margin(1.8, 1.0))"
  ],
  "language": "Python"
}
```

---

## 3. Section Parameter Reference

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `"type"` | `string` | `"code"` | Section type identifier (`"code"`). |
| `"file"` / `"path"` / `"code_file"` | `string` | `None` | Path to code file to read from disk. |
| `"code"` | `string`/`array` | `""` | Inline code content string or array of line strings. |
| `"title"` | `string` | `""` | Optional section title displayed above code box. |
| `"number"` | `string`/`int` | `""` | Optional section number (e.g., `"3.1"`). Omit to hide section numbers. |
| `"language"` / `"lang"` | `string` | `""` | Language identifier tag (e.g. `"Verilog"`, `"VHDL"`, `"Python"`, `"C++"`). |
| `"show_line_numbers"` | `boolean` | `true` | Show or hide line numbers in left margin of code box. |

---

## 4. Visual Formatting & Code Box Features

1. **Language & Path Badge Header**: If `"language"` or file path is provided, a styled top header bar (`[Verilog] rtl/rca8.v`) is rendered at the top of the code box.
2. **Line Numbers**: Line numbers are rendered right-aligned in a dim gray margin (`#888888`).
3. **Monospace Font**: Rendered in Courier monospace font.
4. **Preserved Formatting**: Exact indentation, spaces, and tabs are preserved.
5. **Page Break Splitting**: Long code files automatically split cleanly across page breaks line-by-line.

---

## 5. Customizing Code Box Styling (`config.json`)

You can customize code block fonts, sizes, colors, and line spacing in `config.json`:

```json
{
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
