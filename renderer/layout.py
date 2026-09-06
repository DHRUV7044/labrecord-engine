import os
from PIL import Image as PILImage

MM = 72.0 / 25.4

class Rect:
    def __init__(self, x, y, width, height):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)

    def __repr__(self):
        return f"Rect(x={self.x:.2f}, y={self.y:.2f}, w={self.width:.2f}, h={self.height:.2f})"


def get_effective_image_dimensions(img_obj):
    """
    Returns effective (width, height) of an image after applying rotation (0, 90, 180, 270).
    """
    if not img_obj or not os.path.exists(img_obj.resolved_path):
        return 100.0, 100.0

    try:
        with PILImage.open(img_obj.resolved_path) as im:
            orig_w, orig_h = im.size
            rotation = int(img_obj.rotation) % 360
            if rotation in (90, 270):
                return float(orig_h), float(orig_w)
            return float(orig_w), float(orig_h)
    except Exception:
        return 100.0, 100.0


def compute_node_aspect_ratio(node, image_map):
    """
    Recursively computes the effective intrinsic aspect ratio (width / height)
    of a layout node tree.
    """
    if not node:
        return 1.0

    if node.node_type in ("ref", "freebox"):
        img_obj = image_map.get(node.image_id)
        eff_w, eff_h = get_effective_image_dimensions(img_obj)
        return eff_w / eff_h if eff_h > 0 else 1.0

    elif node.node_type == "row":
        children = node.children
        if not children:
            return 1.0
        # In a row, children share height, so aspect ratios add up
        total_aspect = sum(compute_node_aspect_ratio(c, image_map) for c in children)
        return total_aspect if total_aspect > 0 else 1.0

    elif node.node_type == "column":
        children = node.children
        if not children:
            return 1.0
        # In a column, children share width, so inverse aspect ratios add up
        inv_aspect_sum = sum(1.0 / max(0.01, compute_node_aspect_ratio(c, image_map)) for c in children)
        return 1.0 / inv_aspect_sum if inv_aspect_sum > 0 else 1.0

    return 1.0


def compute_recursive_image_layout(node, container_rect, gap, image_map):
    """
    Recursively computes optimal image placement bounding boxes inside container_rect
    by distributing space proportional to child aspect ratios.
    Returns a list of tuples: (image_object, rect)
    """
    if not node:
        return []

    if node.node_type == "ref":
        img_obj = image_map.get(node.image_id)
        if img_obj:
            return [(img_obj, container_rect)]
        return []

    if node.node_type == "row":
        children = node.children
        n = len(children)
        if n == 0:
            return []

        avail_w = container_rect.width - (n - 1) * gap
        if avail_w < 0:
            avail_w = max(0.0, container_rect.width)

        aspects = [compute_node_aspect_ratio(c, image_map) for c in children]
        total_aspect = sum(aspects)

        results = []
        curr_x = container_rect.x

        for i, child in enumerate(children):
            if total_aspect > 0:
                child_w = avail_w * (aspects[i] / total_aspect)
            else:
                child_w = avail_w / n

            c_rect = Rect(curr_x, container_rect.y, child_w, container_rect.height)
            results.extend(compute_recursive_image_layout(child, c_rect, gap, image_map))
            curr_x += child_w + gap

        return results

    elif node.node_type == "column":
        children = node.children
        m = len(children)
        if m == 0:
            return []

        avail_h = container_rect.height - (m - 1) * gap
        if avail_h < 0:
            avail_h = max(0.0, container_rect.height)

        inv_aspects = [1.0 / max(0.01, compute_node_aspect_ratio(c, image_map)) for c in children]
        total_inv_aspect = sum(inv_aspects)

        results = []
        # Top-to-bottom layout
        curr_top_y = container_rect.y + container_rect.height

        for j, child in enumerate(children):
            if total_inv_aspect > 0:
                child_h = avail_h * (inv_aspects[j] / total_inv_aspect)
            else:
                child_h = avail_h / m

            cy = curr_top_y - child_h
            c_rect = Rect(container_rect.x, cy, container_rect.width, child_h)
            results.extend(compute_recursive_image_layout(child, c_rect, gap, image_map))
            curr_top_y -= (child_h + gap)

        return results

    return []


def convert_freebox_coords(pos_mm, size_mm, printable_area_rect, config):
    """
    Converts top-left relative millimetre coordinates (x, y) and size (w, h)
    to ReportLab bottom-left point coordinates inside printable_area_rect.
    """
    x_mm = float(pos_mm.get("x", 0))
    y_mm = float(pos_mm.get("y", 0))
    w_mm = float(size_mm.get("width", 100))
    h_mm = float(size_mm.get("height", 100))

    w_pt = w_mm * MM
    h_pt = h_mm * MM

    # Printable area top y in ReportLab
    top_y = printable_area_rect.y + printable_area_rect.height

    x_pt = printable_area_rect.x + x_mm * MM
    y_pt = top_y - (y_mm * MM) - h_pt

    # Bounds validation check
    printable_w_mm = printable_area_rect.width / MM
    printable_h_mm = printable_area_rect.height / MM

    if (x_mm + w_mm) > (printable_w_mm + 0.1) or (y_mm + h_mm) > (printable_h_mm + 0.1) or x_mm < -0.1 or y_mm < -0.1:
        print(f"WARNING: Freebox box at ({x_mm}mm, {y_mm}mm, size {w_mm}x{h_mm}mm) exceeds allowed image-page bounds ({printable_w_mm:.1f}x{printable_h_mm:.1f}mm).")

    return Rect(x_pt, y_pt, w_pt, h_pt)
