# LabRecord Engine — CLI User Guide (`labfile`)

The `labfile` command-line executable provides project initialization, PDF typesetting, image scanning, CSV table importing, and template management.

---

## Command Overview

```bash
labfile <command> [options]
```

### Available Commands

| Command | Summary |
| :--- | :--- |
| [`labfile init`](#1-labfile-init) | Initialize a new LabRecord project with template files. |
| [`labfile generate`](#2-labfile-generate) | Compile documents and render publication-ready PDFs. |
| [`labfile scan`](#3-labfile-scan) | Scan an image directory and register images into `record.json`. |
| [`labfile csv`](#4-labfile-csv) | Import a CSV file as a table section into `record.json`. |
| [`labfile templates`](#5-labfile-templates) | List all installed and available document templates. |
| [`labfile --help`](#6-global-flags) | Display general CLI help or command-specific parameters. |

---

## 1. `labfile init`

Initializes a new LabRecord Engine project directory. By default, it generates `main.json`, `config.json`, `record.json`, and an `output/` directory.

```bash
labfile init [directory] [flags]
```

### Parameters & Flags

| Flag / Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `directory` | `positional` | `.` (current dir) | Target directory to initialize project in. |
| `-t`, `--template` | `string` | `"default"` | Built-in template to use (`"default"`, `"vd"`, `"cao"`). |
| `-makeimagedir` | `flag` | `false` | Creates an `images/` folder inside the project directory. |
| `-f`, `--force` | `flag` | `false` | Force overwrite existing project files (`main.json`, `config.json`, `record.json`). |
| `--scan [DIR]` | `string` | `None` | Automatically scan the target directory (or specified `DIR`) for images upon initialization. |
| `--csv <FILE>` | `string` | `None` | Automatically import a CSV file as a table section upon initialization. |

### Examples

```bash
# Basic initialization in current directory
labfile init

# Initialize using the CAO lab template
labfile init --template cao

# Initialize in a specific folder and auto-scan an image directory
labfile init /home/user/vlsi_lab -t vd --scan /home/user/vlsi_lab/screenshots

# Initialize with a pre-linked CSV data file
labfile init --csv measurements.csv -t default
```

---

## 2. `labfile generate`

Locates `main.json` (or the specified manifest/directory), processes all PDF build jobs, and outputs compiled A4 PDF documents.

```bash
labfile generate [path]
```

### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `path` | `positional` | `None` | Path to `main.json` file or directory containing `main.json`. If omitted, automatically searches current and parent directories. |

### Project Discovery Rules
If `path` is omitted, `labfile generate` searches for `main.json` in:
1. Current working directory (`./main.json`)
2. Parent directories (`../main.json`, `../../main.json`, etc.)

### Examples

```bash
# Generate PDF using current directory's main.json
labfile generate

# Generate PDF specifying project directory
labfile generate /home/user/cadence_lab/

# Generate PDF specifying explicit manifest file
labfile generate /home/user/cadence_lab/main.json
```

---

## 3. `labfile scan`

Scans a directory for image files (`.png`, `.jpg`, `.jpeg`, `.svg`) and automatically registers them into the Global Image Registry in `record.json`.

```bash
labfile scan [directory] [flags]
```

### Parameters & Flags

| Flag / Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `directory` | `positional` | `.` (current dir) | Directory containing images to scan. |
| `-r`, `--record` | `string` | `"record.json"` | Path to document JSON file to update. |
| `--recursive` | `flag` | `false` | Recursively scan subdirectories for images. |
| `--abs` | `flag` | `false` | Store absolute image paths instead of relative paths. |
| `-f`, `--force` | `flag` | `false` | Overwrite existing image entries with matching IDs. |

### Examples

```bash
# Scan current directory for images and add to record.json
labfile scan

# Scan screenshots folder recursively and update record.json
labfile scan screenshots/ -r record.json --recursive
```

---

## 4. `labfile csv`

Imports a CSV data file as a table section into `record.json`.

```bash
labfile csv <csv_file> [flags]
```

### Parameters & Flags

| Flag / Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `csv_file` | `positional` | *Required* | Path to the `.csv` file to import. |
| `-r`, `--record` | `string` | `"record.json"` | Target document JSON file to update. |
| `-t`, `--title` | `string` | *CSV filename* | Custom title for the table section. |
| `-n`, `--number` | `string` | `None` | Table or section number (e.g., `"3.1"`). |
| `--embed` | `flag` | `false` | Embed cell matrix data directly into JSON instead of file path linking. |
| `-d`, `--delimiter`| `string` | `","` | CSV column delimiter character (e.g. `","`, `";"`, `"\t"`). |

### Examples

```bash
# Link a CSV file as a table section in record.json
labfile csv measurements.csv --title "DC Characteristics"

# Import CSV and embed matrix values directly into record.json
labfile csv results.csv --embed -n "4.1" -t "Noise Margin Data"
```

---

## 5. `labfile templates`

Lists all available built-in document templates.

```bash
labfile templates
```

Output Example:
```text
Available templates:
  cao
  default
  vd
```

---

## 6. Global Flags

| Flag | Description |
| :--- | :--- |
| `-v`, `--version` | Display LabRecord Engine version. |
| `-h`, `--help` | Display general help or help for a specific subcommand (e.g. `labfile init --help`). |
