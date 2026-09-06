import os
import re
import hashlib
import io
import xml.sax.saxutils as saxutils
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from reportlab.platypus import Paragraph, Image as RLImage, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor

# Cache directory for math images
CACHE_DIR = os.path.join(os.getcwd(), "output", ".cache_math")
os.makedirs(CACHE_DIR, exist_ok=True)

_MATH_CACHE = {}

def render_latex_to_file(latex_str, font_size=11, text_color="black"):
    """
    Renders a LaTeX math expression to a transparent PNG image file.
    Returns (img_path, width_pt, height_pt).
    """
    cache_key = (latex_str, font_size, text_color)
    if cache_key in _MATH_CACHE:
        return _MATH_CACHE[cache_key]

    # Normalize latex expression for matplotlib mathtext
    tex = latex_str.strip()
    if not tex.startswith("$"):
        tex = f"${tex}$"

    # Compute a unique filename hash
    hash_str = hashlib.md5(f"{tex}_{font_size}_{text_color}".encode('utf-8')).hexdigest()
    img_filename = f"math_{hash_str}.png"
    img_path = os.path.join(CACHE_DIR, img_filename)

    if not os.path.exists(img_path):
        try:
            fig = plt.figure()
            t = fig.text(0, 0, tex, fontsize=font_size, color=text_color)
            fig.canvas.draw()
            bbox = t.get_window_extent(fig.canvas.get_renderer())
            w_in, h_in = bbox.width / fig.dpi, bbox.height / fig.dpi
            fig.set_size_inches(w_in, h_in)

            # Save transparent high-DPI image
            plt.savefig(img_path, format='png', dpi=300, bbox_inches='tight', pad_inches=0.01, transparent=True)
            plt.close(fig)

            # Re-read dimensions from saved figure bounding box
            w_pt = max(6.0, w_in * 72.0)
            h_pt = max(6.0, h_in * 72.0)

            _MATH_CACHE[cache_key] = (img_path, w_pt, h_pt)
            return img_path, w_pt, h_pt
        except Exception as e:
            # Fallback to plain text if matplotlib fails on invalid TeX
            plt.close('all')
            print(f"WARNING: Could not render math expression '{latex_str}': {e}")
            return None, 0, 0
    else:
        # Load from disk
        from PIL import Image as PILImage
        with PILImage.open(img_path) as im:
            w_px, h_px = im.size
            # 300 dpi -> points (72 pt / 300 dpi)
            w_pt = (w_px / 300.0) * 72.0
            h_pt = (h_px / 300.0) * 72.0
        _MATH_CACHE[cache_key] = (img_path, w_pt, h_pt)
        return img_path, w_pt, h_pt


def process_text_with_latex(text_str, font_size=11, text_color="black"):
    """
    Parses a string for LaTeX expressions ($ ... $) and returns HTML formatted text
    with embedded <img> tags for ReportLab Paragraphs.
    """
    if not text_str:
        return ""

    # Check if text is entirely a single math equation
    trimmed = text_str.strip()
    if trimmed.startswith("$") and trimmed.endswith("$") and trimmed.count("$") == 2:
        img_path, w_pt, h_pt = render_latex_to_file(trimmed, font_size=font_size, text_color=text_color)
        if img_path:
            return f'<img src="{img_path}" width="{w_pt:.2f}" height="{h_pt:.2f}" valign="middle"/>'

    # Split text into math ($...$) and non-math segments
    pattern = r'(\$.*?\$)'
    parts = re.split(pattern, text_str)

    res_parts = []
    for part in parts:
        if not part:
            continue
        if part.startswith("$") and part.endswith("$") and len(part) > 2:
            img_path, w_pt, h_pt = render_latex_to_file(part, font_size=font_size, text_color=text_color)
            if img_path:
                res_parts.append(f'<img src="{img_path}" width="{w_pt:.2f}" height="{h_pt:.2f}" valign="middle"/>')
            else:
                res_parts.append(saxutils.escape(part))
        else:
            # Escape plain text for ReportLab XML parser
            res_parts.append(saxutils.escape(part))

    return "".join(res_parts)


def create_paragraph(text_str, style, font_size=11):
    """
    Creates a ReportLab Paragraph flowable from text_str, rendering any LaTeX expressions inside.
    """
    html_text = process_text_with_latex(text_str, font_size=font_size)
    return Paragraph(html_text, style)
