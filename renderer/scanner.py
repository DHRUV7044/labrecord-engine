import os
import json
import re

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".bmp", ".webp", ".tiff"}

def sanitize_id(filename):
    """
    Converts a filename into a clean, valid image ID string.
    e.g. 'CMOS Schematic (v2).png' -> 'cmos_schematic_v2'
    """
    name_without_ext = os.path.splitext(filename)[0]
    clean_name = re.sub(r'[^a-zA-Z0-9_]+', '_', name_without_ext).strip('_').lower()
    return clean_name if clean_name else "image"


def format_title(filename, counter_idx=1):
    """
    Generates a concise, short title for an image file.
    If the filename is a short clean name (<= 15 chars), formats it cleanly.
    Otherwise, returns a simple sequential number string '1', '2', '3', etc.
    """
    name_without_ext = os.path.splitext(filename)[0]
    words = re.sub(r'[^a-zA-Z0-9]+', ' ', name_without_ext).split()
    formatted = ' '.join(word.capitalize() for word in words) if words else name_without_ext
    if len(formatted) <= 15 and formatted:
        return formatted
    return str(counter_idx)


def scan_images(image_dir=".", record_json_path="record.json", recursive=False, use_abs=False, force=False):
    """
    Scans image_dir for image files and registers them in record_json_path.
    Returns (added_list, skipped_list).
    """
    abs_image_dir = os.path.abspath(image_dir)
    if not os.path.exists(abs_image_dir):
        raise FileNotFoundError(f"Image directory to scan does not exist: {image_dir}")

    abs_record_path = os.path.abspath(record_json_path)
    record_dir = os.path.dirname(abs_record_path)

    # Find image files
    found_files = []
    if recursive:
        for root, _, files in os.walk(abs_image_dir):
            for file in sorted(files):
                ext = os.path.splitext(file)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    found_files.append(os.path.join(root, file))
    else:
        for file in sorted(os.listdir(abs_image_dir)):
            full_p = os.path.join(abs_image_dir, file)
            if os.path.isfile(full_p):
                ext = os.path.splitext(file)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    found_files.append(full_p)

    if not found_files:
        print(f"No matching images found in '{image_dir}'.")
        return [], []

    # Load existing record.json or create structure
    if os.path.exists(abs_record_path):
        with open(abs_record_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {
            "document": {"title": "LAB RECORD", "date": ""},
            "images": [],
            "experiments": []
        }

    if "images" not in data or not isinstance(data["images"], list):
        data["images"] = []

    existing_ids = {img["id"]: img for img in data["images"] if isinstance(img, dict) and "id" in img}
    existing_paths = {img.get("path"): img for img in data["images"] if isinstance(img, dict) and "path" in img}

    added = []
    skipped = []

    for scan_idx, img_file in enumerate(found_files, start=1):
        filename = os.path.basename(img_file)
        base_id = sanitize_id(filename)

        # Path resolution
        if use_abs:
            img_path_str = os.path.abspath(img_file)
        else:
            try:
                img_path_str = os.path.relpath(img_file, record_dir)
            except ValueError:
                img_path_str = os.path.abspath(img_file)

        # Check if path already in registry
        if img_path_str in existing_paths and not force:
            skipped.append((existing_paths[img_path_str]["id"], img_path_str, "Path already registered"))
            continue

        # Handle ID collisions
        final_id = base_id
        counter = 2
        while final_id in existing_ids and not force:
            final_id = f"{base_id}_{counter}"
            counter += 1

        img_entry = {
            "id": final_id,
            "path": img_path_str,
            "title": format_title(filename, counter_idx=scan_idx)
        }

        if final_id in existing_ids and force:
            # Overwrite existing entry
            data["images"] = [img if img.get("id") != final_id else img_entry for img in data["images"]]
        else:
            data["images"].append(img_entry)

        existing_ids[final_id] = img_entry
        existing_paths[img_path_str] = img_entry
        added.append((final_id, img_path_str))

    # Save updated record.json
    with open(abs_record_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return added, skipped
