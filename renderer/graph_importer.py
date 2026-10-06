import os
import json


def add_graph_to_record(
    csv_path,
    record_json_path="record.json",
    title=None,
    number=None,
    x_col=0,
    y_cols=None,
    graph_type="line",
    x_label=None,
    y_label=None,
    grid=True,
    legend=None
):
    """
    Adds a CSV graph section entry to record.json.
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

    if y_cols is None:
        y_cols = [1]
    elif isinstance(y_cols, str):
        if "," in y_cols:
            y_cols = [y.strip() for y in y_cols.split(",") if y.strip()]
        else:
            y_cols = [y_cols.strip()]

    graph_section = {
        "type": "graph",
        "csv": rel_csv_path,
        "x": x_col,
        "y": y_cols if isinstance(y_cols, list) and len(y_cols) > 1 else (y_cols[0] if isinstance(y_cols, list) and len(y_cols) == 1 else y_cols),
        "graph_type": graph_type
    }

    if number is not None:
        graph_section["number"] = number

    if title:
        graph_section["title"] = title
    else:
        basename = os.path.splitext(os.path.basename(csv_path))[0]
        graph_section["title"] = basename.replace("_", " ").title()

    if x_label is not None:
        graph_section["x_label"] = x_label
    if y_label is not None:
        graph_section["y_label"] = y_label

    if grid is False:
        graph_section["grid"] = False
    if legend is not None:
        graph_section["legend"] = legend

    experiments = data.get("experiments", [])
    if not experiments:
        experiments.append({
            "title": "Experiment 1",
            "sections": []
        })
        data["experiments"] = experiments

    exp = experiments[0]
    sections = exp.get("sections", [])
    sections.append(graph_section)
    exp["sections"] = sections

    with open(rec_abs, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return graph_section
