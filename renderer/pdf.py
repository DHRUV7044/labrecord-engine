import os
import json
import sys

from reportlab.platypus import SimpleDocTemplate, PageBreak, Spacer, Paragraph, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from .config import load_config, Config
from .document import load_document, DocumentModel
from .pages import draw_top_header_rule, SectionHeadingFlowable, LabCanvas, SuppressHeaderFlowable
from .text import create_paragraph
from .tables import create_table_flowable
from .images import ImagePageFlowable
from .code import create_code_flowable


def generate_document_pdf(doc_model, output_path, config=None, name=None, roll_number=None):
    """
    Renders a DocumentModel object to an A4 PDF at output_path.
    """
    if name is not None:
        doc_model.name = name
    if roll_number is not None:
        doc_model.roll_number = roll_number

    if config is None:
        config = load_config(template_name=doc_model.template_name)

    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)

    # Margins and page size
    page_w = config.page_width
    page_h = config.page_height
    margin_l = config.margin_left
    margin_r = config.margin_right
    margin_t = config.margin_top
    margin_b = config.margin_bottom

    show_header = config.get("experiment_header", "show_header", default=None)
    if show_header is None:
        show_header = config.get("experiment_header", "enabled", default=None)
    if show_header is None:
        show_header = config.get("header", "show_header", default=True)

    has_student_info = bool(doc_model.name or doc_model.roll_number)
    layout_style = config.get("experiment_header", "layout_style", default="centered")

    if show_header:
        if has_student_info:
            top_margin_doc = margin_t + (26 if layout_style == "split_top" else 36)
        else:
            top_margin_doc = margin_t + 20
    else:
        if has_student_info:
            top_margin_doc = margin_t + 16
        else:
            top_margin_doc = margin_t


    doc = SimpleDocTemplate(
        output_path,
        pagesize=(page_w, page_h),
        leftMargin=margin_l,
        rightMargin=margin_r,
        topMargin=top_margin_doc,
        bottomMargin=margin_b
    )

    # Styles
    font_body = config.get_font("body")
    body_font_size = float(config.get("font_sizes", "body", default=11))
    line_spacing = float(config.get("paragraph", "line_spacing", default=1.25))

    body_style = ParagraphStyle(
        'DocBody',
        fontName=font_body,
        fontSize=body_font_size,
        leading=body_font_size * line_spacing,
        spaceAfter=float(config.get("paragraph", "spacing_after", default=6)),
        spaceBefore=float(config.get("paragraph", "spacing_before", default=0))
    )

    story = []
    first_exp = doc_model.experiments[0] if doc_model.experiments else None
    exp_num = first_exp.number if first_exp else None
    exp_type = first_exp.type if first_exp else None
    exp_date = first_exp.date if (first_exp and first_exp.date) else doc_model.date

    # Canvas callback for top experiment header and date line ABOVE rule
    def on_first_page(canv, document):
        if hasattr(canv, 'set_header_callback'):
            canv.set_header_callback(lambda c: draw_top_header_rule(c, exp_num, exp_type, exp_date, config, name=doc_model.name, roll_number=doc_model.roll_number, is_later_page=False))
        else:
            draw_top_header_rule(canv, exp_num, exp_type, exp_date, config, name=doc_model.name, roll_number=doc_model.roll_number, is_later_page=False)

    def on_later_pages(canv, document):
        if hasattr(canv, 'set_header_callback'):
            canv.set_header_callback(lambda c: draw_top_header_rule(c, exp_num, exp_type, exp_date, config, name=doc_model.name, roll_number=doc_model.roll_number, is_later_page=True))
        else:
            draw_top_header_rule(canv, exp_num, exp_type, exp_date, config, name=doc_model.name, roll_number=doc_model.roll_number, is_later_page=True)

    numbering_style_table = config.get("table", "numbering_style", default="sequential")
    numbering_style_figure = config.get("figure", "numbering_style", default="sequential")

    seq_tbl_counter = 1
    seq_fig_counter = 1

    for exp_idx, exp in enumerate(doc_model.experiments):
        for sec_idx, sec in enumerate(exp.sections):

            if numbering_style_table == "section_based":
                sec_tbl_counter = 1
            if numbering_style_figure == "section_based":
                sec_fig_counter = 1

            # Handle blank section, page break, or blank_page / new_page options
            if sec.type in ("blank", "blank_page", "empty", "empty_page", "raw_page"):
                if len(story) > 0:
                    story.append(PageBreak())
                if sec.no_header:
                    story.append(SuppressHeaderFlowable())
                story.append(Spacer(1, 1))
                story.append(PageBreak())
                continue
            elif sec.type in ("page_break", "pagebreak"):
                if len(story) > 0:
                    story.append(PageBreak())
                continue

            if getattr(sec, "blank_page", False) and len(story) > 0:
                story.append(Spacer(1, 1))
                story.append(PageBreak())
            elif sec.new_page and len(story) > 0:
                story.append(PageBreak())

            # Section Heading
            sec_heading = SectionHeadingFlowable(sec.number, sec.title, config)

            # Render Section Content
            if sec.type == "text":
                story.append(sec_heading)
                story.append(Spacer(1, 8))
                for para_text in sec.paragraphs:
                    p_flowable = create_paragraph(para_text, body_style, font_size=body_font_size)
                    story.append(p_flowable)
                story.append(Spacer(1, 4))

            elif sec.type == "table":
                story.append(sec_heading)
                story.append(Spacer(1, 8))
                for tbl in sec.tables:
                    tbl_idx = sec_tbl_counter if numbering_style_table == "section_based" else seq_tbl_counter
                    t_flowables = create_table_flowable(tbl, config, section_num=sec.number, table_index=tbl_idx)
                    story.extend(t_flowables)
                    if numbering_style_table == "section_based":
                        sec_tbl_counter += 1
                    else:
                        seq_tbl_counter += 1
                story.append(Spacer(1, 4))

            elif sec.type == "image":
                for sub_idx, sub in enumerate(sec.subsections):
                    # If this is not the first subsection, force a page break
                    if sub_idx > 0:
                        story.append(PageBreak())

                    fig_idx = sec_fig_counter if numbering_style_figure == "section_based" else seq_fig_counter
                    img_flowable = ImagePageFlowable(
                        subsection=sub,
                        section=sec,
                        image_map=sec.images,
                        config=config,
                        figure_counter_start=fig_idx
                    )

                    if sub_idx == 0 and sec_heading and sec_heading.has_heading:
                        story.append(sec_heading)
                        story.append(Spacer(1, 8))

                    story.append(img_flowable)

                    # Count how many images were placed in this subsection to increment figure counter
                    placed_count = _count_layout_images(sub.layout)
                    if numbering_style_figure == "section_based":
                        sec_fig_counter += placed_count
                    else:
                        seq_fig_counter += placed_count

                story.append(Spacer(1, 4))

            elif sec.type == "code":
                story.append(sec_heading)
                story.append(Spacer(1, 8))
                code_flowables = create_code_flowable(sec, config)
                story.extend(code_flowables)

    doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages, canvasmaker=LabCanvas)
    return output_path


def _count_layout_images(node):
    if not node:
        return 0
    if node.node_type in ("ref", "freebox"):
        return 1
    total = 0
    for child in node.children:
        total += _count_layout_images(child)
    return total


def build_manifest(manifest_path="main.json", config_path=None, name=None, roll_number=None):
    """
    Reads manifest file, validates it, and runs generation jobs.
    Returns list of job result tuples: (input_path, output_path, success_bool, error_message)
    """
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

    with open(manifest_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in manifest file {manifest_path}: {e}")

    jobs = data.get("jobs")
    if not isinstance(jobs, list):
        raise ValueError(f"Manifest file {manifest_path} must contain a 'jobs' array.")

    manifest_dir = os.path.dirname(os.path.abspath(manifest_path))

    results = []
    for job in jobs:
        if not isinstance(job, dict) or "input" not in job or "output" not in job:
            results.append(("<invalid_job>", "<invalid_job>", False, "Job missing 'input' or 'output' field."))
            continue

        raw_in = job["input"]
        raw_out = job["output"]

        # Resolve paths relative to manifest directory if relative
        in_path = raw_in if os.path.isabs(raw_in) else os.path.normpath(os.path.join(manifest_dir, raw_in))
        out_path = raw_out if os.path.isabs(raw_out) else os.path.normpath(os.path.join(manifest_dir, raw_out))

        job_config_path = config_path
        if not job_config_path:
            local_cfg = os.path.join(manifest_dir, "config.json")
            if os.path.exists(local_cfg):
                job_config_path = local_cfg
        elif not os.path.isabs(job_config_path):
            job_config_path = os.path.normpath(os.path.join(manifest_dir, job_config_path))

        try:
            doc_model = load_document(in_path)
            if name is not None:
                doc_model.name = name
            if roll_number is not None:
                doc_model.roll_number = roll_number
            config = load_config(config_path=job_config_path, template_name=doc_model.template_name)
            generate_document_pdf(doc_model, out_path, config=config, name=name, roll_number=roll_number)
            results.append((raw_in, raw_out, True, None))
        except Exception as e:
            results.append((raw_in, raw_out, False, str(e)))

    return results

