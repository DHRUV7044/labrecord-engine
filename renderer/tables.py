from reportlab.platypus import Table as RLTable, TableStyle, Paragraph, Spacer, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from .text import process_text_with_latex

def build_table_matrix(table_obj):
    """
    Constructs a 2D matrix of cell content strings from a TableObject.
    Validates structural consistency and raises ValueError if invalid.
    """
    table_obj.validate()

    elements = table_obj.elements
    if not elements:
        return []

    elem_type = table_obj.element_type

    if elem_type == "row":
        matrix = []
        for elem in elements:
            if isinstance(elem, dict):
                title = elem.get("title")
                entries = elem.get("entries", [])
                row = ([str(title)] if title is not None else []) + [str(e) for e in entries]
            elif isinstance(elem, list):
                row = [str(e) for e in elem]
            else:
                row = [str(elem)]
            matrix.append(row)
        return matrix

    elif elem_type == "column":
        # Extract headers and columns
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

    else:
        raise ValueError(f'ERROR: Table {table_obj.number} contains invalid element_type "{elem_type}".')


def create_table_flowable(table_obj, config, section_num=None, table_index=1):
    """
    Creates ReportLab Flowables for a table (caption paragraph + Table flowable).
    """
    matrix = build_table_matrix(table_obj)
    if not matrix:
        return []

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

