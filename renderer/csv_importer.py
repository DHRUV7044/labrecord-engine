import os
import json
import csv


def load_csv_matrix(csv_path, doc_dir=".", delimiter=","):
    """
    Reads a CSV file and returns a 2D matrix (list of lists of cell strings).
    """
    abs_path = csv_path if os.path.isabs(csv_path) else os.path.normpath(os.path.join(doc_dir, csv_path))
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f'ERROR: CSV file not found "{abs_path}" in {doc_dir}')

    matrix = []
    with open(abs_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            matrix.append([cell.strip() for cell in row])

    return matrix


def add_csv_to_record(csv_path, record_json_path="record.json", title=None, number=None, embed=False, delimiter=","):
    """
    Adds a CSV file table section entry to record.json.
    """
    rec_abs = os.path.abspath(record_json_path)
    if not os.path.exists(rec_abs):
        raise FileNotFoundError(f"Record file not found: {record_json_path}")

    with open(rec_abs, "r", encoding="utf-8") as f:
        data = json.load(f)

    rec_dir = os.path.dirname(rec_abs)
    csv_abs = os.path.abspath(csv_path)

    if not os.path.exists(csv_abs):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    try:
        rel_csv_path = os.path.relpath(csv_abs, rec_dir)
    except ValueError:
        rel_csv_path = csv_abs

    table_section = {
        "type": "table"
    }

    if number is not None:
        table_section["number"] = number

    if title:
        table_section["title"] = title
    else:
        basename = os.path.splitext(os.path.basename(csv_path))[0]
        table_section["title"] = basename.replace("_", " ").title()

    if embed:
        matrix = load_csv_matrix(csv_abs, doc_dir=rec_dir, delimiter=delimiter)
        table_section["elements"] = matrix
    else:
        table_section["csv"] = rel_csv_path
        if delimiter != ",":
            table_section["delimiter"] = delimiter

    experiments = data.get("experiments", [])
    if not experiments:
        experiments.append({
            "title": "Experiment 1",
            "sections": []
        })
        data["experiments"] = experiments

    exp = experiments[0]
    sections = exp.get("sections", [])
    sections.append(table_section)
    exp["sections"] = sections

    with open(rec_abs, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return table_section
