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


def draw_top_header_rule(canvas_obj, exp_number, exp_type, date_str, config):
    """
    Draws top experiment header and line based on configurable template layout_style:
    - centered: EXPERIMENT NO. centered, DATE on left
    - split_top: DATE on top-left, EXPERIMENT NO. on top-right
    """
    canvas_obj.saveState()
    
    margin_left = config.margin_left
    margin_top = config.margin_top
    printable_w = config.printable_width
    page_h = config.page_height

    top_y = page_h - margin_top

    # Configurable options
    layout_style = config.get("experiment_header", "layout_style", default="centered")
    exp_offset_y = float(config.get("experiment_header", "exp_no_offset_y", default=8))
    date_offset_y = float(config.get("experiment_header", "date_offset_y", default=-2))
    rule_offset_y = float(config.get("experiment_header", "rule_offset_y", default=-6))
    show_date = config.get("experiment_header", "show_date", default=True)
    show_rule = config.get("experiment_header", "show_rule", default=True)

    font_name = config.get_font("title")
    font_size = float(config.get("experiment_header", "font_size", default=14))
    exp_y = top_y + exp_offset_y
    date_y = top_y + date_offset_y

    formatted_type = format_experiment_type(exp_type)

    if layout_style == "split_top":
        if formatted_type:
            exp_text = f"EXPERIMENT NO. : {exp_number} ({formatted_type})"
        else:
            exp_text = f"EXPERIMENT NO. {exp_number}"

        # Right-aligned experiment header
        canvas_obj.setFont(font_name, font_size)
        right_x = margin_left + printable_w
        canvas_obj.drawRightString(right_x, exp_y, exp_text)

        # Left-aligned date string
        if date_str and show_date:
            date_font = config.get_font("header")
            date_font_size = float(config.get("font_sizes", "header", default=11))
            canvas_obj.setFont(date_font, date_font_size)
            canvas_obj.drawString(margin_left, date_y, f"DATE: {date_str}")

    else:
        # centered layout style
        if formatted_type:
            exp_text = f"EXPERIMENT NO. : {exp_number} ({formatted_type})"
        else:
            exp_text = f"EXPERIMENT NO. : {exp_number}"

        canvas_obj.setFont(font_name, font_size)
        center_x = margin_left + printable_w / 2.0
        canvas_obj.drawCentredString(center_x, exp_y, exp_text)

        if date_str and show_date:
            date_font = config.get_font("header")
            date_font_size = float(config.get("font_sizes", "header", default=11))
            canvas_obj.setFont(date_font, date_font_size)
            canvas_obj.drawString(margin_left, date_y, f"DATE: {date_str}")

    # Horizontal rule line below header
    if show_rule:
        rule_y = min(exp_y, date_y) + rule_offset_y
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
        self.number = str(number)
        self.title = str(title).upper()
        self.config = config

        self.font_name = config.get_font("heading")
        self.font_size = float(config.get("font_sizes", "section_heading", default=12))
        self.width = config.printable_width
        self.height = self.font_size * 1.5 + 8

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
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
