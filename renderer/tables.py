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
    ref_pattern = r'\b(?:re\d+|rc\d+|ce\d+|cr\d+|r\d+e\d+|r\d+c\d+|c\d+e\d+|c\d+r\d+)\b'
    func_pattern = r'\b(?:avg|mean|perr|abs|sum|min|max)\s*\('
    return bool(re.search(ref_pattern, text, re.IGNORECASE) or re.search(func_pattern, text, re.IGNORECASE))


def resolve_cell_value(matrix, target_r, target_c, cache, visited):
    cell_key = (target_r, target_c)
    if cell_key in cache:
        return cache[cell_key]

    if cell_key in visited:
        return 0.0

    visited.add(cell_key)

    if 0 <= target_r < len(matrix) and 0 <= target_c < len(matrix[target_r]):
        raw = matrix[target_r][target_c]
        if contains_expression(raw):
            val_str = evaluate_single_cell_content(raw, matrix, target_r, target_c, cache, visited)
            num_val = extract_number(val_str)
        else:
            num_val = extract_number(raw)
    else:
        num_val = 0.0

    cache[cell_key] = num_val
    return num_val


def parse_and_eval_math_expr(expr_str, is_perr=False):
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
        "abs": _abs,
        "sum": _sum,
        "min": _min,
        "max": _max,
    }

    try:
        res = eval(expr_str, {"__builtins__": None}, allowed_names)
        if isinstance(res, (int, float)):
            if is_perr:
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


def replace_references_in_expr(expr_text, matrix, curr_r, curr_c, cache, visited):
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

        val = resolve_cell_value(matrix, t_r, t_c, cache, visited)
        return str(val)

    return re.sub(ref_pattern, replacer, expr_text, flags=re.IGNORECASE)


def evaluate_single_cell_content(cell_text, matrix, curr_r, curr_c, cache, visited):
    if not isinstance(cell_text, str) or not contains_expression(cell_text):
        return cell_text

    text = cell_text.strip()

    # Case 1: Wrapped in $...$ e.g. "$perr(re1, re2)$"
    if text.startswith('$') and text.endswith('$') and len(text) > 2:
        inner = text[1:-1].strip()
        is_perr = 'perr' in inner.lower()
        eval_inner = replace_references_in_expr(inner, matrix, curr_r, curr_c, cache, visited)
        return parse_and_eval_math_expr(eval_inner, is_perr=is_perr)

    # Case 2: Starts with = e.g. "=r1e1 - r2e2"
    if text.startswith('='):
        inner = text[1:].strip()
        is_perr = 'perr' in inner.lower()
        eval_inner = replace_references_in_expr(inner, matrix, curr_r, curr_c, cache, visited)
        return parse_and_eval_math_expr(eval_inner, is_perr=is_perr)

    # Case 3: Wrapped in {...} e.g. "{re1 - re2}"
    if text.startswith('{') and text.endswith('}'):
        inner = text[1:-1].strip()
        is_perr = 'perr' in inner.lower()
        eval_inner = replace_references_in_expr(inner, matrix, curr_r, curr_c, cache, visited)
        return parse_and_eval_math_expr(eval_inner, is_perr=is_perr)

    # Case 4: Unwrapped expression cell e.g. "re1 - re2" or "avg(re1, re2)"
    is_perr = 'perr' in text.lower()
    eval_text = replace_references_in_expr(text, matrix, curr_r, curr_c, cache, visited)
    return parse_and_eval_math_expr(eval_text, is_perr=is_perr)


def process_table_matrix_expressions(matrix):
    """
    Evaluates all cell expressions in a 2D table matrix in-place.
    """
    if not matrix:
        return matrix

    cache = {}
    new_matrix = []

    for r_idx, row in enumerate(matrix):
        new_row = []
        for c_idx, cell_val in enumerate(row):
            visited = set()
            if isinstance(cell_val, str) and contains_expression(cell_val):
                res_val = evaluate_single_cell_content(cell_val, matrix, r_idx, c_idx, cache, visited)
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

    matrix = process_table_matrix_expressions(matrix)


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

    # Styles
    cell_font_size = config.get("font_sizes", "table_cell", default=10)
    font_body = config.get_font("body")
    font_bold = config.get_font("heading")

    header_style = ParagraphStyle(
        'TableHeader',
        fontName=font_bold,
        fontSize=cell_font_size,
        leading=cell_font_size * 1.2,
        alignment=0
    )

    cell_style = ParagraphStyle(
        'TableCell',
        fontName=font_body,
        fontSize=cell_font_size,
        leading=cell_font_size * 1.2,
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
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
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

    caption_para = Paragraph(caption_text, caption_style)

    # Return list of flowables (Caption + Table + Spacer)
    return [caption_para, rl_table, Spacer(1, config.get("table", "spacing_after", default=10))]

