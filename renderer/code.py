import html
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors


def create_code_flowable(section, config):
    """
    Creates ReportLab flowables for a code section.
    """
    code_text = section.code_text if section.code_text is not None else ""

    font_code = config.get("fonts", "code", default="Courier")
    code_font_size = float(config.get("code", "font_size", default=config.get("font_sizes", "code", default=9)))
    line_spacing = float(config.get("code", "line_spacing", default=1.2))
    leading = code_font_size * line_spacing

    bg_color = config.get("code", "background_color", default="#f8f9fa")
    border_color = config.get("code", "border_color", default="#cccccc")
    line_num_color = config.get("code", "line_number_color", default="#888888")
    header_bg = config.get("code", "header_background", default="#eaeded")
    spacing_after = float(config.get("code", "spacing_after", default=10))

    show_line_numbers = section.show_line_numbers
    if show_line_numbers is None:
        show_line_numbers = config.get("code", "show_line_numbers", default=True)

    page_w = config.page_width
    margin_l = config.margin_left
    margin_r = config.margin_right
    avail_w = page_w - margin_l - margin_r

    lines = code_text.splitlines()
    if not lines:
        lines = [""]

    style_num = ParagraphStyle(
        'CodeLineNum',
        fontName=font_code,
        fontSize=code_font_size,
        leading=leading,
        textColor=colors.HexColor(line_num_color),
        alignment=2  # Right aligned
    )

    style_code = ParagraphStyle(
        'CodeLineText',
        fontName=font_code,
        fontSize=code_font_size,
        leading=leading,
        textColor=colors.HexColor('#111111')
    )

    table_data = []

    # Optional header badge row if language or code_path is provided
    has_header = bool(section.language or section.code_path)
    if has_header:
        header_parts = []
        if section.code_path:
            header_parts.append(section.code_path)
        if section.language:
            header_parts.append(f"[{section.language}]")
        header_text = " ".join(header_parts)

        style_header = ParagraphStyle(
            'CodeHeader',
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#555555')
        )
        header_p = Paragraph(html.escape(header_text), style_header)
        if show_line_numbers:
            table_data.append([header_p, ''])
        else:
            table_data.append([header_p])

    num_col_w = 30 if show_line_numbers else 0
    code_col_w = avail_w - num_col_w if show_line_numbers else avail_w

    for idx, line in enumerate(lines, 1):
        escaped = html.escape(line).replace(' ', '&nbsp;').replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
        code_p = Paragraph(escaped if escaped else '&nbsp;', style_code)

        if show_line_numbers:
            num_p = Paragraph(str(idx), style_num)
            table_data.append([num_p, code_p])
        else:
            table_data.append([code_p])

    col_widths = [num_col_w, code_col_w] if show_line_numbers else [code_col_w]
    t = Table(table_data, colWidths=col_widths)

    ts = [
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg_color)),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor(border_color)),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#f0f0f0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
    ]

    if has_header:
        if show_line_numbers:
            ts.append(('SPAN', (0, 0), (1, 0)))
        ts.append(('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header_bg)))
        ts.append(('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor(border_color)))
        ts.append(('TOPPADDING', (0, 0), (-1, 0), 3.5))
        ts.append(('BOTTOMPADDING', (0, 0), (-1, 0), 3.5))

    t.setStyle(TableStyle(ts))

    return [t, Spacer(1, spacing_after)]
