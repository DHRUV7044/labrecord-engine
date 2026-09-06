import os
import io
from PIL import Image as PILImage
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Flowable

from .layout import Rect, compute_recursive_image_layout, convert_freebox_coords, MM

def load_and_prepare_image(image_path, rotation=0):
    """
    Opens image file with Pillow, rotates if needed (0, 90, 180, 270),
    and returns (ReportLab ImageReader, effective_width_px, effective_height_px).
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"ERROR: Image file not found: {image_path}")

    img = PILImage.open(image_path)
    rotation = rotation % 360

    if rotation != 0:
        # Pillow rotate counter-clockwise for positive degrees
        img = img.rotate(-rotation, expand=True)

    buf = io.BytesIO()
    # Save as PNG to preserve format/quality
    img.save(buf, format="PNG")
    buf.seek(0)

    reader = ImageReader(buf)
    w_px, h_px = img.size
    return reader, float(w_px), float(h_px)


class ImagePageFlowable(Flowable):
    """
    A ReportLab Flowable representing exactly ONE PDF page of images for an ImageSubsection.
    Prioritizes maximum page utilization, aspect-ratio preservation, and margin/gap constraints.
    """
    def __init__(self, subsection, section, image_map, config, figure_counter_start=1):
        super().__init__()
        self.subsection = subsection
        self.section = section
        self.image_map = image_map
        self.config = config
        self.figure_counter_start = figure_counter_start

        # Page dimension allocation initialized to printable defaults, adjusted in wrap()
        self.width = config.printable_width
        self.height = config.printable_height

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        self.height = availHeight
        return self.width, self.height

    def draw(self):
        canv = self.canv
        config = self.config

        # Printable bounds in canvas space
        printable_rect = Rect(0, 0, self.width, self.height)

        layout = self.subsection.layout
        if not layout:
            return

        fig_num = self.figure_counter_start
        gap = float(config.get("image", "default_gap", default=5)) * MM
        caption_size = float(config.get("image", "caption_font_size", default=10))
        caption_spacing = float(config.get("image", "caption_spacing", default=4))
        caption_height_pt = caption_size * 1.3 + caption_spacing

        if layout.node_type == "freebox":
            img_obj = self.image_map.get(layout.image_id)
            if not img_obj:
                print(f"WARNING: Image ID '{layout.image_id}' not found in image map.")
                return

            # Freebox top-left mm conversion relative to printable area
            fb_rect = convert_freebox_coords(layout.position, layout.size, printable_rect, config)
            self._draw_single_image(canv, img_obj, fb_rect, fig_num, caption_height_pt, caption_spacing)

        else:
            # Recursive aspect-ratio aware layout (row/column)
            placements = compute_recursive_image_layout(layout, printable_rect, gap, self.image_map)

            for img_obj, box in placements:
                self._draw_single_image(canv, img_obj, box, fig_num, caption_height_pt, caption_spacing)
                fig_num += 1

    def _draw_single_image(self, canv, img_obj, box, fig_num, caption_height_pt, caption_spacing):
        try:
            reader, eff_w, eff_h = load_and_prepare_image(img_obj.resolved_path, img_obj.rotation)
        except Exception as e:
            print(f"ERROR loading image {img_obj.raw_path}: {e}")
            return

        numbering_style = self.config.get("figure", "numbering_style", default="sequential")
        number_format = self.config.get("figure", "number_format", default="Figure {figure_num}: {title}")

        sec_str = str(self.section.number) if (self.section and self.section.number) else ""
        fig_num_str = str(fig_num)
        title_text = img_obj.title

        if numbering_style == "section_based":
            if title_text:
                try:
                    caption_text = number_format.format(section_num=sec_str, figure_num=fig_num_str, title=title_text)
                except KeyError:
                    caption_text = f"Figure {sec_str}.{fig_num_str}: {title_text}"
            else:
                base_fmt = number_format.split(":")[0]
                try:
                    caption_text = base_fmt.format(section_num=sec_str, figure_num=fig_num_str)
                except KeyError:
                    caption_text = f"Figure {sec_str}.{fig_num_str}"
        else:
            if title_text:
                try:
                    caption_text = number_format.format(figure_num=fig_num_str, title=title_text)
                except KeyError:
                    caption_text = f"Figure {fig_num_str}: {title_text}"
            else:
                base_fmt = number_format.split(":")[0]
                try:
                    caption_text = base_fmt.format(figure_num=fig_num_str)
                except KeyError:
                    caption_text = f"Figure {fig_num_str}"


        # Reserve caption height at bottom of box
        avail_img_h = max(10.0, box.height - caption_height_pt)
        avail_img_w = max(10.0, box.width)

        scale_x = avail_img_w / eff_w
        scale_y = avail_img_h / eff_h
        scale = min(scale_x, scale_y)

        final_w = eff_w * scale
        final_h = eff_h * scale

        # Center image within available image space
        img_x = box.x + (avail_img_w - final_w) / 2.0
        img_y = box.y + caption_height_pt + (avail_img_h - final_h) / 2.0

        canv.saveState()
        canv.drawImage(
            reader,
            img_x,
            img_y,
            width=final_w,
            height=final_h,
            preserveAspectRatio=True,
            mask="auto"
        )

        # Draw caption centered below image
        caption_font = self.config.get_font("caption")
        caption_size = float(self.config.get("image", "caption_font_size", default=10))

        canv.setFont(caption_font, caption_size)
        caption_y = box.y + caption_spacing
        caption_x = box.x + box.width / 2.0

        canv.drawCentredString(caption_x, caption_y, caption_text)
        canv.restoreState()
