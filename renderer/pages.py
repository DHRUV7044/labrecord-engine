from reportlab.pdfgen import canvas
from reportlab.platypus import PageBreak, Flowable, Spacer, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

class LabCanvas(canvas.Canvas):
    """
    Custom Canvas for two-pass page numbering or header callbacks.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            super().showPage()
        super().save()


def format_experiment_type(raw_type):
    if not raw_type:
        return ""
    cleaned = str(raw_type).replace("_", " ").strip()
    return cleaned.upper()


def draw_top_header_rule(canvas_obj, exp_number, exp_type, date_str, config, name="", roll_number=""):
    """
    Draws top experiment header and line based on configurable template layout_style:
    - centered: EXPERIMENT NO. centered, DATE on left
    - split_top: DATE on top-left, EXPERIMENT NO. on top-right
    If name or roll_number is provided, renders student info at the very top of every page above experiment header.
    """
    show_header = config.get("experiment_header", "show_header", default=None)
    if show_header is None:
        show_header = config.get("experiment_header", "enabled", default=None)
    if show_header is None:
        show_header = config.get("header", "show_header", default=True)

    has_student_info = bool((name and str(name).strip()) or (roll_number and str(roll_number).strip()))

    if not show_header and not has_student_info:
        return

    canvas_obj.saveState()

    margin_left = config.margin_left
    margin_top = config.margin_top
    printable_w = config.printable_width
    page_h = config.page_height

    top_y = page_h - margin_top

    layout_style = config.get("experiment_header", "layout_style", default="centered")
    show_date = config.get("experiment_header", "show_date", default=True)
    show_rule = config.get("experiment_header", "show_rule", default=True)

    font_name = config.get_font("title")
    header_font = config.get_font("header")
    header_font_size = float(config.get("font_sizes", "header", default=11))
    font_size = float(config.get("experiment_header", "font_size", default=14))

    student_offset_user = config.get("experiment_header", "student_offset_y", default=None)
    exp_offset_user = config.get("experiment_header", "exp_no_offset_y", default=None)
    date_offset_user = config.get("experiment_header", "date_offset_y", default=None)
    rule_offset_user = config.get("experiment_header", "rule_offset_y", default=None)

    student_offset_y = float(student_offset_user) if student_offset_user is not None else 8.0

    if has_student_info:
        student_y = top_y + student_offset_y

        name_str = str(name).strip() if name else ""
        if name_str:
            if not name_str.lower().startswith("name:"):
                name_str = f"NAME: {name_str}"
            canvas_obj.setFont(header_font, header_font_size)
            canvas_obj.drawString(margin_left, student_y, name_str)

        roll_str = str(roll_number).strip() if roll_number else ""
        if roll_str:
            if not roll_str.lower().startswith("roll"):
                roll_str = f"ROLL NO: {roll_str}"
            canvas_obj.setFont(header_font, header_font_size)
            right_x = margin_left + printable_w
            canvas_obj.drawRightString(right_x, student_y, roll_str)

        if show_header:
            default_exp = -6.0
            default_date = -6.0 if layout_style == "split_top" else -16.0
            exp_y = top_y + (float(exp_offset_user) if exp_offset_user is not None else default_exp)
            date_y = top_y + (float(date_offset_user) if date_offset_user is not None else default_date)
        else:
            exp_y = top_y
            date_y = top_y
    else:
        default_exp = 8.0
        default_date = -2.0
        exp_y = top_y + (float(exp_offset_user) if exp_offset_user is not None else default_exp)
        date_y = top_y + (float(date_offset_user) if date_offset_user is not None else default_date)

    if show_header:
        exp_has_num = (exp_number is not None and str(exp_number).strip() != "")
        formatted_type = format_experiment_type(exp_type)

        if exp_has_num:
            if layout_style == "split_top":
                exp_text = f"EXPERIMENT NO. : {exp_number} ({formatted_type})" if formatted_type else f"EXPERIMENT NO. {exp_number}"
            else:
                exp_text = f"EXPERIMENT NO. : {exp_number} ({formatted_type})" if formatted_type else f"EXPERIMENT NO. : {exp_number}"
        else:
            exp_text = formatted_type if formatted_type else ""

        if exp_text:
            canvas_obj.setFont(font_name, font_size)
            if layout_style == "split_top":
                right_x = margin_left + printable_w
                canvas_obj.drawRightString(right_x, exp_y, exp_text)
            elif layout_style == "left":
                canvas_obj.drawString(margin_left, exp_y, exp_text)
            elif layout_style == "right":
                right_x = margin_left + printable_w
                canvas_obj.drawRightString(right_x, exp_y, exp_text)
            else:
                center_x = margin_left + printable_w / 2.0
                canvas_obj.drawCentredString(center_x, exp_y, exp_text)

        if date_str and show_date:
            canvas_obj.setFont(header_font, header_font_size)
            canvas_obj.drawString(margin_left, date_y, f"DATE: {date_str}")

    # Horizontal rule line below header
    if show_rule:
        if rule_offset_user is not None:
            rule_y = top_y + float(rule_offset_user)
        elif has_student_info:
            if show_header:
                rule_y = top_y - (12.0 if layout_style == "split_top" else 22.0)
            else:
                rule_y = top_y - 2.0
        else:
            default_rule = -6.0
            rule_y = min(exp_y, date_y) + default_rule

        canvas_obj.setLineWidth(0.75)
        canvas_obj.setStrokeColor(colors.black)
        canvas_obj.line(margin_left, rule_y, margin_left + printable_w, rule_y)

    canvas_obj.restoreState()



class SectionHeadingFlowable(Flowable):
    """
    Renders section heading with bold number & title and horizontal underline:
    1. AIM
    ---------------------------------------------------
    """
    def __init__(self, number, title, config):
        super().__init__()
        self.number = str(number).strip() if number is not None else ""
        self.title = str(title).strip().upper() if title is not None else ""
        self.config = config

        self.font_name = config.get_font("heading")
        self.font_size = float(config.get("font_sizes", "section_heading", default=12))
        self.width = config.printable_width
        self.has_heading = bool(self.number or self.title)
        self.height = (self.font_size * 1.5 + 8) if self.has_heading else 0

    def wrap(self, availWidth, availHeight):
        if not self.has_heading:
            return 0, 0
        return self.width, self.height

    def draw(self):
        if not self.has_heading:
            return
        canv = self.canv
        canv.saveState()

        heading_str = f"{self.number}. {self.title}" if self.number else self.title

        text_y = 10
        canv.setFont(self.font_name, self.font_size)
        canv.drawString(0, text_y, heading_str)

        # Underline rule
        rule_y = text_y - 4
        canv.setLineWidth(0.75)
        canv.setStrokeColor(colors.black)
        canv.line(0, rule_y, self.width, rule_y)

        canv.restoreState()
