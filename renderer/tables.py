import os
import csv
import re
from reportlab.platypus import Table as RLTable, TableStyle, Paragraph, Spacer, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


from .text import process_text_with_latex

def split_by_comma_smart(text):
    """
    Splits a string by commas outside of LaTeX math ($...$ or $$...$$).
    Trims leading/trailing whitespace around each token.
    """
    if not isinstance(text, str):
        return [str(text)] if text is not None else []

    parts = []
    current = []
    in_math = False
    i = 0
    n = len(text)

    while i < n:
        char = text[i]
        if char == '$':
            in_math = not in_math
            current.append(char)
        elif char == ',' and not in_math:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        i += 1

    if current or not parts:
        parts.append("".join(current).strip())

    return parts


def build_table_matrix(table_obj):
    """
    Constructs a 2D matrix of cell content strings from a TableObject.
    Supports CSV imports, row-based, column-based, and shorthand comma-separated entry formats.
    """
    table_obj.validate()

    if getattr(table_obj, "csv_matrix", None) is not None:
        return table_obj.csv_matrix

    elements = table_obj.elements
    if not elements:
        return []

    elem_type = table_obj.element_type

    # 1. Shorthand string elements array: ["Header 1 , Header 2", "Val 1 , Val 2"]
    if all(isinstance(e, str) for e in elements):
        matrix = []
        for elem_str in elements:
            matrix.append(split_by_comma_smart(elem_str))
        return matrix

    # 2. Single dict element containing comma-separated entries
    if len(elements) == 1 and isinstance(elements[0], dict):
        elem = elements[0]
        entries = elem.get("entries", [])
        title = elem.get("title")

        has_comma_entries = any(isinstance(e, str) and ',' in e for e in entries)
        has_comma_title = isinstance(title, str) and ',' in title

        if has_comma_entries or has_comma_title:
            matrix = []
            if title is not None:
                matrix.append(split_by_comma_smart(title))
            for entry in entries:
                if isinstance(entry, str):
                    matrix.append(split_by_comma_smart(entry))
                elif isinstance(entry, list):
                    row = []
                    for item in entry:
                        row.extend(split_by_comma_smart(str(item)))
                    matrix.append(row)
                else:
                    matrix.append([str(entry)])
            return matrix

    # 3. Row-based tables
    if elem_type == "row":
        matrix = []
        for elem in elements:
            if isinstance(elem, dict):
                title = elem.get("title")
                entries = elem.get("entries", [])
                row = []
                if title is not None:
                    row.extend(split_by_comma_smart(title))
                for e in entries:
                    if isinstance(e, str) and ',' in e:
                        row.extend(split_by_comma_smart(e))
                    else:
                        row.append(str(e))
                matrix.append(row)
            elif isinstance(elem, list):
                row = []
                for item in elem:
                    if isinstance(item, str) and ',' in item:
                        row.extend(split_by_comma_smart(item))
                    else:
                        row.append(str(item))
                matrix.append(row)
            elif isinstance(elem, str):
                matrix.append(split_by_comma_smart(elem))
            else:
                matrix.append([str(elem)])
        return matrix

    # 4. Column-based tables (or default multi-column elements)
    headers = []
    columns = []
    max_rows = 0

    for elem in elements:
        if isinstance(elem, dict):
            headers.append(str(elem.get("title", "")))
            entries = [str(e) for e in elem.get("entries", [])]
            columns.append(entries)
            max_rows = max(max_rows, len(entries))
        elif isinstance(elem, list):
            headers.append("")
            entries = [str(e) for e in elem]
            columns.append(entries)
            max_rows = max(max_rows, len(entries))
        else:
            headers.append("")
            columns.append([str(elem)])
            max_rows = max(max_rows, 1)

    matrix = []
    if any(h != "" for h in headers):
        matrix.append(headers)

    for r in range(max_rows):
        row = []
        for c in range(len(columns)):
            if r < len(columns[c]):
                row.append(columns[c][r])
            else:
                row.append("")
        matrix.append(row)

    return matrix


def extract_number(val_str):
    """
    Extracts the first floating point or integer number from a string.
    E.g. "180 nm" -> 180.0, "$1.8V$" -> 1.8, "15.02 ps" -> 15.02, "46.80%" -> 46.80
    """
    if isinstance(val_str, (int, float)):
        return float(val_str)
    if not isinstance(val_str, str):
        return 0.0

    match = re.search(r'[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?', val_str)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return 0.0
    return 0.0


def contains_expression(text):
    if not isinstance(text, str):
        return False
    t = text.strip()
    if t.startswith('='):
        return True

    ref_pattern = r'\b(?:re\d+|rc\d+|ce\d+|cr\d+|r\d+e\d+|r\d+c\d+|c\d+e\d+|c\d+r\d+)\b'
    cross_csv_pattern = r'\b[a-zA-Z0-9_\-\.]+?:(?:re\d+|rc\d+|ce\d+|cr\d+|r\d+e\d+|c\d+e\d+|\d+)\b'
    func_pattern = r'\b(?:avg|mean|sperr|signed_perr|s_perr|perr|abs|sum|min|max)\s*\('
    math_op_pattern = r'[\d.]+\s*[-+*/^]\s*[\d.]+'
    paren_math_pattern = r'\([\d.\s]+[-+*/^][\d.\s)]+'

    # Do not treat pure LaTeX math symbols like $V_{DD}$ or $V_{th}$ as numeric math expressions
    if re.search(r'^\$[a-zA-Z_]+\{?[a-zA-Z0-9_]*\}?\$', t) and not re.search(r'[\d.]+\s*[-+*/^]\s*[\d.]+', t):
        return False

    return bool(
        re.search(ref_pattern, t, re.IGNORECASE) or
        re.search(cross_csv_pattern, t, re.IGNORECASE) or
        re.search(func_pattern, t, re.IGNORECASE) or
        re.search(math_op_pattern, t) or
        re.search(paren_math_pattern, t)
    )


def resolve_cell_value(matrix, target_r, target_c, cache, visited, doc_dir=".", file_sources=None, ext_csv_cache=None):
    cell_key = (target_r, target_c)
    if cell_key in cache:
        return cache[cell_key]

    if cell_key in visited:
        return 0.0

    visited.add(cell_key)

    if 0 <= target_r < len(matrix) and 0 <= target_c < len(matrix[target_r]):
        raw = matrix[target_r][target_c]
        if contains_expression(raw):
            val_str = evaluate_single_cell_content(raw, matrix, target_r, target_c, cache, visited, doc_dir=doc_dir, file_sources=file_sources, ext_csv_cache=ext_csv_cache)
            num_val = extract_number(val_str)
        else:
            num_val = extract_number(raw)
    else:
        num_val = 0.0

    cache[cell_key] = num_val
    return num_val


def resolve_external_cell(file_ref, cell_token, curr_r, curr_c, doc_dir=".", file_sources=None, ext_csv_cache=None, cache=None, visited=None):
    import csv
    if file_sources is None:
        file_sources = {}
    if ext_csv_cache is None:
        ext_csv_cache = {}

    rel_path = file_sources.get(file_ref, file_ref)
    if not rel_path.lower().endswith(".csv") and not os.path.exists(os.path.join(doc_dir, rel_path)):
        rel_path = rel_path + ".csv"

    abs_path = rel_path if os.path.isabs(rel_path) else os.path.normpath(os.path.join(doc_dir, rel_path))

    if abs_path not in ext_csv_cache:
        if os.path.exists(abs_path):
            rows = []
            with open(abs_path, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                for r in reader:
                    if r and r[0].strip().startswith('#'):
                        continue
                    if r and any(c.strip() for c in r):
                        rows.append([c.strip() for c in r])
            ext_csv_cache[abs_path] = rows
        else:
            ext_csv_cache[abs_path] = []

    ext_matrix = ext_csv_cache[abs_path]
    if not ext_matrix:
        return 0.0

    m_re = re.match(r'^(?:re|rc)(\d+)$', cell_token, re.IGNORECASE)
    m_ce = re.match(r'^(?:ce|cr)(\d+)$', cell_token, re.IGNORECASE)
    m_re_ec = re.match(r'^r(\d+)(?:e|c)(\d+)$', cell_token, re.IGNORECASE)
    m_ce_er = re.match(r'^c(\d+)(?:e|r)(\d+)$', cell_token, re.IGNORECASE)

    if m_re:
        t_r = curr_r
        t_c = int(m_re.group(1)) - 1
    elif m_ce:
        t_r = int(m_ce.group(1)) - 1
        t_c = curr_c
    elif m_re_ec:
        t_r = int(m_re_ec.group(1)) - 1
        t_c = int(m_re_ec.group(2)) - 1
    elif m_ce_er:
        t_c = int(m_ce_er.group(1)) - 1
        t_r = int(m_ce_er.group(2)) - 1
    elif cell_token.isdigit():
        t_r = curr_r
        t_c = int(cell_token) - 1
    else:
        return 0.0

    if 0 <= t_r < len(ext_matrix) and 0 <= t_c < len(ext_matrix[t_r]):
        val_raw = ext_matrix[t_r][t_c]
        if contains_expression(val_raw):
            val_str = evaluate_single_cell_content(val_raw, ext_matrix, t_r, t_c, cache or {}, visited or set(), doc_dir=doc_dir, file_sources=file_sources, ext_csv_cache=ext_csv_cache)
            return extract_number(val_str)
        else:
            return extract_number(val_raw)
    return 0.0


def parse_and_eval_math_expr(expr_str, is_perr=False, is_sperr=False):
    """
    Evaluates a math string (e.g. "15.02 - 22.05" or "avg(15.02, 22.05)") safely.
    """
    expr_str = expr_str.replace('^', '**')

    def _avg(*args):
        flat = []
        for a in args:
            if isinstance(a, (list, tuple)):
                flat.extend(a)
            else:
                flat.append(float(a))
        return sum(flat) / len(flat) if flat else 0.0

    def _perr(val1, val2=None):
        if val2 is None:
            return 0.0
        v1 = float(val1)
        v2 = float(val2)
        if v1 == 0.0:
            return 0.0
        return abs(v1 - v2) / abs(v1) * 100.0

    def _sperr(val1, val2=None):
        if val2 is None:
            return 0.0
        v1 = float(val1)
        v2 = float(val2)
        if v1 == 0.0:
            return 0.0
        return (v2 - v1) / abs(v1) * 100.0

    def _abs(val):
        return abs(float(val))

    def _sum(*args):
        flat = []
        for a in args:
            if isinstance(a, (list, tuple)):
                flat.extend(a)
            else:
                flat.append(float(a))
        return sum(flat)

    def _min(*args):
        flat = [float(a) for a in args]
        return min(flat) if flat else 0.0

    def _max(*args):
        flat = [float(a) for a in args]
        return max(flat) if flat else 0.0

    allowed_names = {
        "avg": _avg,
        "mean": _avg,
        "perr": _perr,
        "sperr": _sperr,
        "signed_perr": _sperr,
        "s_perr": _sperr,
        "abs": _abs,
        "sum": _sum,
        "min": _min,
        "max": _max,
    }

    try:
        res = eval(expr_str, {"__builtins__": None}, allowed_names)
        if isinstance(res, (int, float)):
            val = float(res)
            if is_sperr:
                if val > 0:
                    return f"+{val:.2f}%" if val.is_integer() else f"+{val:.4f}".rstrip('0').rstrip('.') + "%"
                elif val < 0:
                    return f"{val:.2f}%" if val.is_integer() else f"{val:.4f}".rstrip('0').rstrip('.') + "%"
                else:
                    return "0%"
            elif is_perr:
                return f"{res:.2f}%" if float(res).is_integer() else f"{res:.4f}".rstrip('0').rstrip('.') + "%"
            if isinstance(res, float) and res.is_integer():
                return f"{int(res)}"
            elif isinstance(res, float):
                return f"{res:.4f}".rstrip('0').rstrip('.')
            return str(res)
        return str(res)
    except Exception as e:
        print(f"WARNING: Math evaluation failed for '{expr_str}': {e}")
        return expr_str


def replace_references_in_expr(expr_text, matrix, curr_r, curr_c, cache, visited, doc_dir=".", file_sources=None, ext_csv_cache=None):
    if file_sources is None:
        file_sources = {}
    if ext_csv_cache is None:
        ext_csv_cache = {}

    # First replace cross-CSV references: e.g. f1:re2 or tphl.csv:re2 or tphl:re2
    cross_csv_pattern = r'\b([a-zA-Z0-9_\-\.]+?):(re\d+|rc\d+|ce\d+|cr\d+|r\d+e\d+|c\d+e\d+|\d+)\b'

    def cross_csv_replacer(match):
        file_ref = match.group(1)
        cell_token = match.group(2)
        val = resolve_external_cell(file_ref, cell_token, curr_r, curr_c, doc_dir, file_sources, ext_csv_cache, cache, visited)
        return str(val)

    text = re.sub(cross_csv_pattern, cross_csv_replacer, expr_text, flags=re.IGNORECASE)

    # Then replace intra-sheet references: e.g. re2, rc2, etc.
    ref_pattern = r'\b(re\d+|rc\d+|ce\d+|cr\d+|r\d+e\d+|r\d+c\d+|c\d+e\d+|c\d+r\d+)\b'

    def replacer(match):
        token = match.group(1).lower()
        m_re = re.match(r'^(?:re|rc)(\d+)$', token)
        m_ce = re.match(r'^(?:ce|cr)(\d+)$', token)
        m_re_ec = re.match(r'^r(\d+)(?:e|c)(\d+)$', token)
        m_ce_er = re.match(r'^c(\d+)(?:e|r)(\d+)$', token)

        if m_re:
            t_r = curr_r
            t_c = int(m_re.group(1)) - 1
        elif m_ce:
            t_r = int(m_ce.group(1)) - 1
            t_c = curr_c
        elif m_re_ec:
            t_r = int(m_re_ec.group(1)) - 1
            t_c = int(m_re_ec.group(2)) - 1
        elif m_ce_er:
            t_c = int(m_ce_er.group(1)) - 1
            t_r = int(m_ce_er.group(2)) - 1
        else:
            return token

        val = resolve_cell_value(matrix, t_r, t_c, cache, visited, doc_dir=doc_dir, file_sources=file_sources, ext_csv_cache=ext_csv_cache)
        return str(val)

    return re.sub(ref_pattern, replacer, text, flags=re.IGNORECASE)


def evaluate_single_cell_content(cell_text, matrix, curr_r, curr_c, cache, visited, doc_dir=".", file_sources=None, ext_csv_cache=None):
    if not isinstance(cell_text, str) or not contains_expression(cell_text):
        return cell_text

    text = cell_text.strip()

    # Strip wrapping braces / equals / dollar signs if it contains a formula function or cell reference
    if text.startswith('='):
        text = text[1:].strip()
    if text.startswith('{') and text.endswith('}'):
        text = text[1:-1].strip()
    if text.startswith('$') and text.endswith('$') and len(text) > 2:
        text = text[1:-1].strip()
    elif text.startswith('$') and re.search(r'^\$(?:sperr|signed_perr|s_perr|perr|avg|mean|sum|min|max|abs|\(|re\d|rc\d|ce\d|cr\d|r\d+e\d|c\d+e\d)', text, re.IGNORECASE):
        text = text[1:].strip()

    # Auto-fix missing commas inside function arguments e.g. "perr(re2  re3)" or "avg(re1 re2 re3)"
    def fix_func_commas(expr):
        def replace_args(m):
            func_name = m.group(1)
            args_str = m.group(2)
            tokens = [t.strip() for t in re.split(r'[\s,]+', args_str) if t.strip()]
            return func_name + "(" + ", ".join(tokens) + ")"
        return re.sub(r'\b(sperr|signed_perr|s_perr|perr|avg|mean|sum|min|max|abs)\s*\(([^)]+)\)', replace_args, expr, flags=re.IGNORECASE)

    text = fix_func_commas(text)

    is_sperr = any(k in text.lower() for k in ('sperr', 'signed_perr', 's_perr'))
    is_perr = ('perr' in text.lower()) and not is_sperr
    eval_text = replace_references_in_expr(text, matrix, curr_r, curr_c, cache, visited, doc_dir=doc_dir, file_sources=file_sources, ext_csv_cache=ext_csv_cache)
    return parse_and_eval_math_expr(eval_text, is_perr=is_perr, is_sperr=is_sperr)


def parse_file_sources_from_rows(raw_rows):
    """
    Parses #source lines at top of CSV into a dictionary {alias: filename}.
    Returns (cleaned_rows, file_sources_dict).
    """
    file_sources = {}
    cleaned = []
    for r in raw_rows:
        if not r:
            continue
        first_cell = r[0].strip()
        if first_cell.startswith("#"):
            m = re.match(r'^#\s*source[s]?\s+([a-zA-Z0-9_\-\.]+)\s*[:=]\s*([a-zA-Z0-9_\-\./\\]+)', first_cell, re.IGNORECASE)
            if m:
                alias = m.group(1).strip()
                target_file = m.group(2).strip()
                file_sources[alias] = target_file
            else:
                m2 = re.match(r'^#\s*source[s]?\s+(.+)$', first_cell, re.IGNORECASE)
                if m2:
                    files = [f.strip() for f in m2.group(1).split(",") if f.strip()]
                    for f in files:
                        alias = os.path.splitext(os.path.basename(f))[0]
                        file_sources[alias] = f
        else:
            cleaned.append(r)
    return cleaned, file_sources


def process_table_matrix_expressions(matrix, doc_dir=".", file_sources=None):
    """
    Evaluates all cell expressions in a 2D table matrix in-place.
    Supports cross-CSV references and file alias directives (#source f1 = filename.csv).
    """
    if not matrix:
        return matrix

    cleaned_matrix, parsed_sources = parse_file_sources_from_rows(matrix)
    merged_sources = dict(parsed_sources)
    if file_sources:
        merged_sources.update(file_sources)

    cache = {}
    ext_csv_cache = {}
    new_matrix = []

    for r_idx, row in enumerate(cleaned_matrix):
        new_row = []
        for c_idx, cell_val in enumerate(row):
            visited = set()
            if isinstance(cell_val, str) and contains_expression(cell_val):
                res_val = evaluate_single_cell_content(
                    cell_val, cleaned_matrix, r_idx, c_idx, cache, visited,
                    doc_dir=doc_dir, file_sources=merged_sources, ext_csv_cache=ext_csv_cache
                )
                new_row.append(res_val)
            else:
                new_row.append(cell_val)
        new_matrix.append(new_row)

    return new_matrix


def create_table_flowable(table_obj, config, section_num=None, table_index=1):
    """
    Creates ReportLab Flowables for a table (caption paragraph + Table flowable).
    """
    matrix = build_table_matrix(table_obj)
    if not matrix:
        return []

    doc_dir = getattr(table_obj, "doc_dir", ".")
    matrix = process_table_matrix_expressions(matrix, doc_dir=doc_dir)


    num_rows = len(matrix)
    num_cols = max(len(r) for r in matrix) if num_rows > 0 else 0

    if num_cols == 0:
        return []

    # Standardize matrix columns
    norm_matrix = []
    for row in matrix:
        r_copy = list(row)
        while len(r_copy) < num_cols:
            r_copy.append("")
        norm_matrix.append(r_copy)

    # Styles & Auto-scaling for wide tables
    base_font_size = float(config.get("font_sizes", "table_cell", default=10))
    if num_cols > 10:
        cell_font_size = max(6.5, base_font_size - 3.0)
        padding_h = 2
        padding_v = 2
    elif num_cols > 7:
        cell_font_size = max(7.5, base_font_size - 2.0)
        padding_h = 3
        padding_v = 3
    else:
        cell_font_size = base_font_size
        padding_h = 6
        padding_v = 5

    font_body = config.get_font("body")
    font_bold = config.get_font("heading")

    header_style = ParagraphStyle(
        'TableHeader',
        fontName=font_bold,
        fontSize=cell_font_size,
        leading=cell_font_size * 1.15,
        alignment=0
    )

    cell_style = ParagraphStyle(
        'TableCell',
        fontName=font_body,
        fontSize=cell_font_size,
        leading=cell_font_size * 1.15,
        alignment=0
    )

    # Build flowable cell matrix
    flowable_matrix = []
    for r_idx, row in enumerate(norm_matrix):
        flowable_row = []
        for c_idx, cell_text in enumerate(row):
            # Header row styling (row 0 if column-based table or title row)
            is_header = (r_idx == 0)
            st = header_style if is_header else cell_style
            html_text = process_text_with_latex(cell_text, font_size=cell_font_size)
            flowable_row.append(Paragraph(html_text, st))
        flowable_matrix.append(flowable_row)

    # Calculate column widths to fit printable width
    printable_w = config.printable_width
    col_w = printable_w / num_cols
    col_widths = [col_w] * num_cols

    # Table styling matching reference PDF
    t_style = TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.75, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), padding_v),
        ('BOTTOMPADDING', (0, 0), (-1, -1), padding_v),
        ('LEFTPADDING', (0, 0), (-1, -1), padding_h),
        ('RIGHTPADDING', (0, 0), (-1, -1), padding_h),
    ])

    rl_table = RLTable(flowable_matrix, colWidths=col_widths, repeatRows=1)
    rl_table.setStyle(t_style)

    # Caption style
    caption_style = ParagraphStyle(
        'TableCaption',
        fontName=config.get_font("heading"),
        fontSize=config.get("font_sizes", "caption", default=10),
        leading=config.get("font_sizes", "caption", default=10) * 1.25,
        spaceAfter=6,
        keepWithNext=True
    )

    numbering_style = config.get("table", "numbering_style", default="sequential")
    number_format = config.get("table", "number_format", default="Table {table_num}: {title}")

    sec_str = str(section_num) if section_num is not None else ""
    tbl_num_str = str(table_index)

    if numbering_style == "section_based":
        if table_obj.title:
            try:
                caption_text = number_format.format(section_num=sec_str, table_num=tbl_num_str, title=table_obj.title)
            except KeyError:
                caption_text = f"Table {sec_str}.{tbl_num_str}: {table_obj.title}"
        else:
            base_fmt = number_format.split(":")[0]
            try:
                caption_text = base_fmt.format(section_num=sec_str, table_num=tbl_num_str)
            except KeyError:
                caption_text = f"Table {sec_str}.{tbl_num_str}"
    else:
        if table_obj.title:
            try:
                caption_text = number_format.format(table_num=tbl_num_str, title=table_obj.title)
            except KeyError:
                caption_text = f"Table {tbl_num_str}: {table_obj.title}"
        else:
            base_fmt = number_format.split(":")[0]
            try:
                caption_text = base_fmt.format(table_num=tbl_num_str)
            except KeyError:
                caption_text = f"Table {tbl_num_str}"

    caption_font_size = float(config.get("font_sizes", "caption", default=10))
    html_caption = process_text_with_latex(caption_text, font_size=caption_font_size)
    caption_para = Paragraph(html_caption, caption_style)

    # Return list of flowables (Caption + Table + Spacer)
    return [caption_para, rl_table, Spacer(1, config.get("table", "spacing_after", default=10))]


def create_side_by_side_table_flowables(tables, config, section_num=None, start_table_index=1, layout=None):
    """
    Renders multiple TableObjects side-by-side inside an outer container table.
    """
    if not tables:
        return []

    if len(tables) == 1:
        return create_table_flowable(tables[0], config, section_num=section_num, table_index=start_table_index)

    printable_w = config.printable_width
    gap_width = 14

    num_tables = len(tables)
    available_w = printable_w - (gap_width * (num_tables - 1))

    widths_spec = None
    if isinstance(layout, dict):
        widths_spec = layout.get("column_widths") or layout.get("widths")
        gap_width = float(layout.get("column_gap", gap_width))

    tbl_widths = []
    if isinstance(widths_spec, list) and len(widths_spec) == num_tables:
        for w_item in widths_spec:
            if isinstance(w_item, (int, float)):
                tbl_widths.append(float(w_item))
            elif isinstance(w_item, str) and w_item.endswith("%"):
                pct = float(w_item[:-1]) / 100.0
                tbl_widths.append(available_w * pct)
            else:
                tbl_widths.append(available_w / num_tables)
    else:
        each_w = available_w / num_tables
        tbl_widths = [each_w] * num_tables

    sub_table_containers = []
    col_widths_outer = []

    for i, tbl_obj in enumerate(tables):
        if i > 0:
            sub_table_containers.append("")  # Spacer cell
            col_widths_outer.append(gap_width)

        sub_w = tbl_widths[i]

        class SubConfigWrapper:
            def __init__(self, base_cfg, sub_w):
                self._cfg = base_cfg
                self.printable_width = sub_w
            def __getattr__(self, item):
                return getattr(self._cfg, item)

        sub_cfg = SubConfigWrapper(config, sub_w)
        tbl_flowables = create_table_flowable(tbl_obj, sub_cfg, section_num=section_num, table_index=start_table_index + i)

        sub_table_containers.append(tbl_flowables)
        col_widths_outer.append(sub_w)

    outer_matrix = [sub_table_containers]
    outer_table = RLTable(outer_matrix, colWidths=col_widths_outer)
    outer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    return [outer_table, Spacer(1, config.get("table", "spacing_after", default=10))]


