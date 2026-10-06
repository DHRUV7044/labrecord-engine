import os
import csv
import re
import tempfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from reportlab.platypus import Paragraph, Spacer, KeepTogether
from reportlab.lib.styles import ParagraphStyle

from .text import process_text_with_latex, Paragraph


class SeriesSpec:
    """
    Represents a single data series or data source within a graph.
    """
    def __init__(self, data, doc_dir=".", default_csv=None, default_x=0, default_y=1, default_style=None, default_show_values=False, default_value_format=None):
        self.doc_dir = doc_dir
        csv_rel = (
            data.get("csv") or
            data.get("csv_file") or
            data.get("file") or
            data.get("path") or
            data.get("data") or
            default_csv
        )
        self.csv_path = None
        if csv_rel:
            if os.path.isabs(csv_rel):
                self.csv_path = csv_rel
            else:
                self.csv_path = os.path.normpath(os.path.join(doc_dir, csv_rel))

        self.x_col = data.get("x") if "x" in data else (data.get("x_col") or data.get("x_column") or default_x)

        y_val = data.get("y") if "y" in data else (data.get("y_col") or data.get("y_column") or default_y)
        if isinstance(y_val, (list, tuple)):
            self.y_cols = list(y_val)
        elif y_val is not None:
            self.y_cols = [y_val]
        else:
            self.y_cols = [1]

        self.label = data.get("label") or data.get("name") or data.get("title")
        self.color = data.get("color")
        self.line_style = data.get("line_style") or data.get("linestyle")
        self.marker = data.get("marker")
        self.graph_type = data.get("graph_type") or data.get("chart_type") or data.get("style") or default_style
        self.show_values = data.get("show_values") if "show_values" in data else (data.get("annotate") if "annotate" in data else default_show_values)
        self.value_format = data.get("value_format") or data.get("val_format") or default_value_format


def _parse_mm(val, default_mm):
    if val is None:
        return float(default_mm)
    if isinstance(val, (int, float)):
        return float(val)

    val_str = str(val).strip().lower()
    if val_str.endswith("mm"):
        try:
            return float(val_str[:-2].strip())
        except ValueError:
            return float(default_mm)
    elif val_str.endswith("cm"):
        try:
            return float(val_str[:-2].strip()) * 10.0
        except ValueError:
            return float(default_mm)
    elif val_str.endswith("in") or val_str.endswith("inch") or val_str.endswith("inches"):
        clean_str = re.sub(r'[a-z]', '', val_str).strip()
        try:
            return float(clean_str) * 25.4
        except ValueError:
            return float(default_mm)
    elif val_str.endswith("pt"):
        try:
            return (float(val_str[:-2].strip()) / 72.0) * 25.4
        except ValueError:
            return float(default_mm)
    else:
        try:
            return float(val_str)
        except ValueError:
            return float(default_mm)


class GraphObject:
    """
    Represents a graph / plot specification loaded from a section dictionary.
    Supports single or multiple CSV data sources.
    """
    def __init__(self, data, doc_dir=".", default_title="", default_number=""):
        self.doc_dir = doc_dir
        self.number = data.get("number", default_number)
        self.title = data.get("title", default_title)

        # CSV file path (relative to document directory)
        csv_rel = (
            data.get("csv") or
            data.get("csv_file") or
            data.get("file") or
            data.get("path") or
            data.get("data")
        )
        self.csv_path = None
        if isinstance(csv_rel, str):
            if os.path.isabs(csv_rel):
                self.csv_path = csv_rel
            else:
                self.csv_path = os.path.normpath(os.path.join(doc_dir, csv_rel))

        # Optional mapping from CSV header names to custom legend labels
        self.label_map = data.get("label_map", {})
        if self.label_map is not None and not isinstance(self.label_map, dict):
            raise ValueError("'label_map' must be a dictionary mapping CSV column names to legend labels")

        # X column & Y column defaults
        self.x_col = data.get("x") or data.get("x_col") or data.get("x_column") or 0
        y_val = data.get("y") or data.get("y_col") or data.get("y_column") or 1
        if isinstance(y_val, (list, tuple)):
            self.y_cols = list(y_val)
        else:
            self.y_cols = [y_val]

        # Graph type: line, scatter, bar, step
        raw_type = data.get("graph_type") or data.get("chart_type") or data.get("kind") or data.get("style") or "line"
        self.graph_type = str(raw_type).lower().strip()

        # Data point value annotation options
        self.show_values = bool(data.get("show_values") or data.get("annotate") or data.get("show_labels") or data.get("show_point_values") or False)
        self.value_format = data.get("value_format") or data.get("val_format")

        # Parse Series definitions (Multi-CSV / Multi-series support)
        self.series_specs = []
        raw_series = data.get("series") or data.get("sources")
        if isinstance(raw_series, list) and len(raw_series) > 0 and isinstance(raw_series[0], dict):
            for s_item in raw_series:
                self.series_specs.append(SeriesSpec(s_item, doc_dir=doc_dir, default_csv=csv_rel if isinstance(csv_rel, str) else None, default_x=self.x_col, default_y=self.y_cols, default_style=self.graph_type, default_show_values=self.show_values, default_value_format=self.value_format))
        elif isinstance(csv_rel, list):
            for csv_item in csv_rel:
                s_dict = {"csv": csv_item}
                self.series_specs.append(SeriesSpec(s_dict, doc_dir=doc_dir, default_x=self.x_col, default_y=self.y_cols, default_style=self.graph_type, default_show_values=self.show_values, default_value_format=self.value_format))
        else:
            s_dict = {"csv": csv_rel, "x": self.x_col, "y": self.y_cols}
            self.series_specs.append(SeriesSpec(s_dict, doc_dir=doc_dir, default_style=self.graph_type, default_show_values=self.show_values, default_value_format=self.value_format))

        self.x_label = data.get("x_label") or data.get("xlabel") or ""
        self.y_label = data.get("y_label") or data.get("ylabel") or ""

        self.grid = bool(data.get("grid", True))
        
        # Calculate total series count for default legend
        total_series_count = sum(len(spec.y_cols) for spec in self.series_specs)
        self.legend = bool(data.get("legend", True if total_series_count > 1 or len(self.series_specs) > 1 else False))

        self.line_style = data.get("line_style") or data.get("linestyle") or "-"
        self.marker = data.get("marker", "o" if self.graph_type == "scatter" else None)
        self.color = data.get("color") or data.get("colors")

        raw_w = data.get("width") or data.get("width_mm") or data.get("w")
        raw_h = data.get("height") or data.get("height_mm") or data.get("h")

        # Dimensions in mm (defaults: width=165 mm, height=100 mm)
        self.width_mm = _parse_mm(raw_w, default_mm=165.0)
        self.height_mm = _parse_mm(raw_h, default_mm=100.0)

        # Internal inches conversion for matplotlib figure creation
        self.width_inches = self.width_mm / 25.4
        self.height_inches = self.height_mm / 25.4

        self.dpi = int(data.get("dpi", 300))

        self.dpi = int(data.get("dpi", 300))

    def validate(self):
        for spec in self.series_specs:
            if spec.csv_path and not os.path.exists(spec.csv_path):
                raise FileNotFoundError(f'ERROR: Graph CSV file not found "{spec.csv_path}" in {self.doc_dir}')
        if self.csv_path and not os.path.exists(self.csv_path):
            raise FileNotFoundError(f'ERROR: Graph CSV file not found "{self.csv_path}" in {self.doc_dir}')


def load_csv_data(csv_path, delimiter=","):
    """
    Reads a CSV file and returns (headers_list, rows_of_dict_or_list).
    Evaluates cell expressions (including cross-CSV references) automatically.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    doc_dir = os.path.dirname(os.path.abspath(csv_path))

    rows = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=delimiter)
        for r in reader:
            if r and any(cell.strip() for cell in r):
                rows.append([cell.strip() for cell in r])

    if not rows:
        return [], []

    from .tables import process_table_matrix_expressions
    rows = process_table_matrix_expressions(rows, doc_dir=doc_dir)

    if not rows:
        return [], []

    # Check if first row is header (contains non-numeric strings)
    header_row = rows[0]
    has_headers = False
    for cell in header_row:
        try:
            float(cell)
        except ValueError:
            has_headers = True
            break

    if has_headers:
        headers = [h if h else f"Col_{i+1}" for i, h in enumerate(header_row)]
        data_rows = rows[1:]
    else:
        headers = [f"Col_{i+1}" for i in range(len(header_row))]
        data_rows = rows

    return headers, data_rows


def _resolve_col_index(col_spec, headers):
    """
    Resolves a column specification (header string or integer index) to zero-based integer index.
    """
    if isinstance(col_spec, int):
        # 0-based or 1-based index check
        if 0 <= col_spec < len(headers):
            return col_spec
        elif 1 <= col_spec <= len(headers):
            return col_spec - 1
        return 0

    col_str = str(col_spec).strip()

    # Numeric string
    if col_str.isdigit() or (col_str.startswith("-") and col_str[1:].isdigit()):
        idx = int(col_str)
        if 0 <= idx < len(headers):
            return idx
        elif 1 <= idx <= len(headers):
            return idx - 1
        return 0

    # Header name match (case-insensitive)
    for i, h in enumerate(headers):
        if h.lower() == col_str.lower():
            return i

    # Partial match
    for i, h in enumerate(headers):
        if col_str.lower() in h.lower():
            return i

    return 0


def _clean_matplotlib_tex(label_str):
    if not label_str:
        return ""
    # Replace \text{...} with \mathrm{...} for Matplotlib mathtext compatibility
    return re.sub(r'\\text\{([^}]*)\}', r'\\mathrm{\1}', str(label_str))


def render_graph_to_image(graph_obj, output_dir=None):
    """
    Renders a GraphObject to a PNG file using Matplotlib.
    Supports single or multiple CSV data series.
    Returns path to generated PNG.
    """
    if not graph_obj.series_specs:
        raise ValueError("No series specs defined in GraphObject")

    all_series_plot_data = []

    for spec in graph_obj.series_specs:
        if not spec.csv_path or not os.path.exists(spec.csv_path):
            raise FileNotFoundError(f"Cannot render graph: CSV file not found '{spec.csv_path}'")

        headers, data_rows = load_csv_data(spec.csv_path)
        if not headers or not data_rows:
            raise ValueError(f"No data found in CSV file '{spec.csv_path}'")

        x_idx = _resolve_col_index(spec.x_col, headers)
        y_idxs = [_resolve_col_index(y, headers) for y in spec.y_cols]

        # Extract X values
        x_vals = []
        x_is_numeric = True
        for r in data_rows:
            if x_idx < len(r):
                val_str = r[x_idx]
                try:
                    x_vals.append(float(val_str))
                except ValueError:
                    x_vals.append(val_str)
                    x_is_numeric = False
            else:
                x_vals.append(len(x_vals))

        # Extract Y values for each y column in this series spec
        for y_idx in y_idxs:
            if spec.label:
                raw_label = spec.label
            else:
                raw_label = headers[y_idx] if y_idx < len(headers) else f"Series {y_idx+1}"
            
            mapped_label = graph_obj.label_map.get(raw_label, raw_label)
            series_label = _clean_matplotlib_tex(mapped_label)

            y_vals = []
            for r in data_rows:
                if y_idx < len(r):
                    try:
                        y_vals.append(float(r[y_idx]))
                    except ValueError:
                        y_vals.append(0.0)
                else:
                    y_vals.append(0.0)

            all_series_plot_data.append({
                "label": series_label,
                "x_vals": x_vals,
                "y_vals": y_vals,
                "x_is_numeric": x_is_numeric,
                "graph_type": (spec.graph_type or graph_obj.graph_type).lower().strip(),
                "color": spec.color,
                "line_style": spec.line_style or graph_obj.line_style,
                "marker": spec.marker or graph_obj.marker,
                "show_values": spec.show_values if spec.show_values is not None else graph_obj.show_values,
                "value_format": spec.value_format or graph_obj.value_format,
                "x_header": headers[x_idx] if x_idx < len(headers) else "X",
                "y_header": headers[y_idx] if y_idx < len(headers) else "Y",
            })

    fig, ax = plt.subplots(figsize=(graph_obj.width_inches, graph_obj.height_inches), dpi=graph_obj.dpi)

    colors_palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"]
    if graph_obj.color:
        if isinstance(graph_obj.color, (list, tuple)):
            custom_colors = list(graph_obj.color)
        else:
            custom_colors = [graph_obj.color]
    else:
        custom_colors = colors_palette

    first_item = all_series_plot_data[0] if all_series_plot_data else {}
    points_to_annotate = []

    for i, sdata in enumerate(all_series_plot_data):
        c = sdata["color"] or custom_colors[i % len(custom_colors)]
        g_type = sdata["graph_type"]
        x_vals = sdata["x_vals"]
        y_vals = sdata["y_vals"]
        label = sdata["label"]
        x_is_numeric = sdata["x_is_numeric"]

        if g_type == "bar":
            if not x_is_numeric:
                x_positions = range(len(x_vals))
                width = 0.8 / len(all_series_plot_data)
                offset = (i - len(all_series_plot_data) / 2.0 + 0.5) * width
                pos = [p + offset for p in x_positions]
                ax.bar(pos, y_vals, width=width, label=label, color=c)
                ax.set_xticks(x_positions)
                ax.set_xticklabels([str(xv) for xv in x_vals], rotation=30 if len(x_vals) > 6 else 0)
            else:
                ax.bar(x_vals, y_vals, label=label, color=c, alpha=0.8)
        elif g_type == "scatter":
            ax.scatter(x_vals, y_vals, label=label, color=c, marker=sdata["marker"] or "o", s=30)
        elif g_type == "step":
            ax.step(x_vals, y_vals, label=label, color=c, where="mid")
        else:  # line (default)
            ax.plot(
                x_vals,
                y_vals,
                label=label,
                color=c,
                linestyle=sdata["line_style"],
                marker=sdata["marker"],
                linewidth=1.75
            )

        # Collect points for annotation if show_values is True
        if sdata["show_values"]:
            val_fmt = sdata["value_format"]
            for j, (xv, yv) in enumerate(zip(x_vals, y_vals)):
                if val_fmt:
                    try:
                        val_str = val_fmt.format(yv)
                    except Exception:
                        val_str = str(yv)
                else:
                    if isinstance(yv, float) and yv.is_integer():
                        val_str = str(int(yv))
                    elif isinstance(yv, float):
                        val_str = f"{yv:.2f}".rstrip('0').rstrip('.')
                    else:
                        val_str = str(yv)

                if g_type == "bar" and not x_is_numeric:
                    x_pt = pos[j]
                else:
                    x_pt = xv

                try:
                    x_key = round(float(x_pt), 4)
                except (ValueError, TypeError):
                    x_key = str(x_pt)

                points_to_annotate.append({
                    "series_idx": i,
                    "x_pt": x_pt,
                    "x_key": x_key,
                    "yv": float(yv),
                    "val_str": val_str,
                    "g_type": g_type,
                    "color": c
                })

    # Render anti-collision annotations
    if points_to_annotate:
        # Group points by x_key
        grouped_by_x = {}
        for item in points_to_annotate:
            grouped_by_x.setdefault(item["x_key"], []).append(item)

        bbox_props = dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor='none', alpha=0.75)

        for x_key, group in grouped_by_x.items():
            # Sort points at this x by y-value ascending
            group.sort(key=lambda pt: pt["yv"])
            n_pts = len(group)

            if n_pts == 1:
                pt = group[0]
                ax.annotate(
                    pt["val_str"],
                    xy=(pt["x_pt"], pt["yv"]),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha='center',
                    va='bottom',
                    fontsize=8,
                    bbox=bbox_props
                )
            else:
                # Calculate vertical offsets to prevent label collision
                split_idx = n_pts // 2
                
                # Below points (lower y-values)
                for idx in range(split_idx):
                    pt = group[idx]
                    y_offset = -8 - (split_idx - 1 - idx) * 13
                    ax.annotate(
                        pt["val_str"],
                        xy=(pt["x_pt"], pt["yv"]),
                        xytext=(0, y_offset),
                        textcoords="offset points",
                        ha='center',
                        va='top',
                        fontsize=8,
                        bbox=bbox_props
                    )

                # Above points (higher y-values)
                for idx in range(split_idx, n_pts):
                    pt = group[idx]
                    y_offset = 4 + (idx - split_idx) * 13
                    ax.annotate(
                        pt["val_str"],
                        xy=(pt["x_pt"], pt["yv"]),
                        xytext=(0, y_offset),
                        textcoords="offset points",
                        ha='center',
                        va='bottom',
                        fontsize=8,
                        bbox=bbox_props
                    )

    # Labels and Titles
    raw_xlabel = graph_obj.x_label or first_item.get("x_header", "X")
    raw_ylabel = graph_obj.y_label or (first_item.get("y_header", "Y") if len(all_series_plot_data) == 1 else "Y")

    xlabel = _clean_matplotlib_tex(raw_xlabel)
    ylabel = _clean_matplotlib_tex(raw_ylabel)

    ax.set_xlabel(xlabel, fontsize=10, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=10, fontweight="bold")

    if graph_obj.grid:
        ax.grid(True, linestyle="--", alpha=0.5)

    if graph_obj.legend and len(all_series_plot_data) > 0:
        ax.legend(loc="best", fontsize=9, frameon=True)

    fig.tight_layout()

    if not output_dir:
        output_dir = tempfile.gettempdir()
    os.makedirs(output_dir, exist_ok=True)

    out_file = os.path.join(output_dir, f"graph_{id(graph_obj)}.png")
    fig.savefig(out_file, format="png", dpi=graph_obj.dpi, bbox_inches="tight")
    plt.close(fig)

    return out_file


def create_graph_flowable(graph_obj, config, section_num=None, graph_index=1):
    """
    Creates ReportLab Flowables for a GraphObject (Graph Image + Caption).
    Uses KeepTogether to ensure the figure caption is never orphan-separated onto the next page.
    """
    from reportlab.platypus import Image as RLImage, KeepTogether

    out_img_path = render_graph_to_image(graph_obj)

    # Printable width & height constraints
    printable_w = config.printable_width
    aspect_ratio = graph_obj.height_inches / graph_obj.width_inches
    final_w = printable_w
    final_h = printable_w * aspect_ratio

    # Constrain max height so figure + caption fits on a single printable page
    max_h = (getattr(config, "printable_height", config.page_height - config.margin_top - config.margin_bottom)) - 100
    if max_h > 0 and final_h > max_h:
        final_h = max_h
        final_w = final_h / aspect_ratio

    rl_img = RLImage(out_img_path, width=final_w, height=final_h)

    caption_font = config.get_font("caption")
    caption_size = float(config.get("image", "caption_font_size", default=10))

    numbering_style = config.get("figure", "numbering_style", default="sequential")
    number_format = config.get("figure", "number_format", default="Figure {figure_num}: {title}")

    sec_str = str(section_num) if section_num is not None else ""
    g_num_str = str(graph_index)

    if numbering_style == "section_based":
        if graph_obj.title:
            try:
                caption_text = number_format.format(section_num=sec_str, figure_num=g_num_str, title=graph_obj.title)
            except KeyError:
                caption_text = f"Figure {sec_str}.{g_num_str}: {graph_obj.title}"
        else:
            base_fmt = number_format.split(":")[0]
            try:
                caption_text = base_fmt.format(section_num=sec_str, figure_num=g_num_str)
            except KeyError:
                caption_text = f"Figure {sec_str}.{g_num_str}"
    else:
        if graph_obj.title:
            try:
                caption_text = number_format.format(figure_num=g_num_str, title=graph_obj.title)
            except KeyError:
                caption_text = f"Figure {g_num_str}: {graph_obj.title}"
        else:
            base_fmt = number_format.split(":")[0]
            try:
                caption_text = base_fmt.format(figure_num=g_num_str)
            except KeyError:
                caption_text = f"Figure {g_num_str}"

    html_caption = process_text_with_latex(caption_text, font_size=caption_size)
    caption_style = ParagraphStyle(
        'GraphCaption',
        fontName=caption_font,
        fontSize=caption_size,
        leading=caption_size * 1.25,
        alignment=1,
        spaceBefore=4,
        spaceAfter=6
    )
    caption_para = Paragraph(html_caption, caption_style)

    graph_block = KeepTogether([rl_img, caption_para])

    return [graph_block, Spacer(1, config.get("figure", "spacing_after", default=10))]
