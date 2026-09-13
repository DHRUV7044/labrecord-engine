#!/usr/bin/env python3
import os
import sys
import shutil
from pathlib import Path

# Add project root to sys.path if running within repository
PACKAGE_ROOT = Path(__file__).resolve().parent
if (PACKAGE_ROOT / "renderer").exists():
    sys.path.insert(0, str(PACKAGE_ROOT))

REQUIRED_FILES = {"main.json", "config.json", "record.json"}

def batch_generate(start_dir=".", name=None, roll_number=None, output_dir=None, overwrite=False):
    start_dir = Path(start_dir).resolve()

    if output_dir:
        folder_name = output_dir
    elif name or roll_number:
        parts = []
        if name:
            parts.append(str(name).strip().lower().replace(" ", "_"))
        if roll_number:
            parts.append(str(roll_number).strip().lower().replace(" ", "_"))
        folder_name = "_".join(parts)
    else:
        folder_name = "all_pdfs"

    all_pdfs_dir = start_dir / folder_name
    if overwrite and all_pdfs_dir.exists():
        shutil.rmtree(all_pdfs_dir, ignore_errors=True)
    all_pdfs_dir.mkdir(exist_ok=True)

    print("========================================")
    print("LabRecord Engine — Batch PDF Generator")
    print("========================================")
    print(f"Scanning directory : {start_dir}")
    print(f"Output directory   : {all_pdfs_dir}")
    if name or roll_number:
        print(f"Override Name      : {name or '(none)'}")
        print(f"Override Roll No   : {roll_number or '(none)'}")
    print()

    project_dirs = []
    for root, dirs, files in os.walk(start_dir):
        root_path = Path(root)

        # Skip output folder and .git folders
        if folder_name in root_path.parts or "all_pdfs" in root_path.parts or ".git" in root_path.parts:
            continue

        if REQUIRED_FILES.issubset(set(files)):
            project_dirs.append(root_path)

    if not project_dirs:
        print("No directories containing all 3 JSON files (main.json, config.json, record.json) were found.")
        return

    print(f"Found {len(project_dirs)} project(s):")
    for p in project_dirs:
        rel_p = p.relative_to(start_dir)
        display_name = rel_p.as_posix() if str(rel_p) != "." else "current directory"
        print(f"  - {display_name}")
    print()

    copied_count = 0

    try:
        from renderer.cli import find_manifest
        from renderer.pdf import build_manifest
    except ImportError:
        find_manifest = None
        build_manifest = None

    for p in project_dirs:
        rel_p = p.relative_to(start_dir)
        display_name = rel_p.as_posix() if str(rel_p) != "." else "current directory"
        print(f"Building project in: {display_name}...")

        generated_pdfs = []

        if build_manifest and find_manifest:
            try:
                manifest_path = find_manifest(str(p))
                generated_pdfs = build_manifest(manifest_path, name=name, roll_number=roll_number)
            except Exception as e:
                print(f"  [-] ERROR building project in {display_name}: {e}")
                continue
        else:
            # Fallback to subprocess labfile generate
            import subprocess
            cmd = ["labfile", "generate", str(p)]
            if name:
                cmd.extend(["--name", name])
            if roll_number:
                cmd.extend(["--roll-number", roll_number])
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                print(f"  [-] ERROR generating PDF in {display_name}:\n{res.stderr}")
                continue
            
            output_folder = p / "output"
            if output_folder.exists():
                generated_pdfs = [str(f) for f in output_folder.glob("*.pdf")]

        for res in generated_pdfs:
            if isinstance(res, tuple):
                if len(res) >= 3 and res[2]:  # success
                    pdf_path_str = res[1]
                else:
                    continue
            else:
                pdf_path_str = str(res)

            pdf_file = Path(pdf_path_str) if os.path.isabs(pdf_path_str) else (p / pdf_path_str)
            if pdf_file.exists():
                folder_prefix = rel_p.as_posix().replace("/", "_").replace("\\", "_")
                if folder_prefix and folder_prefix != ".":
                    target_name = f"{pdf_file.stem}_{folder_prefix}{pdf_file.suffix}"
                else:
                    target_name = pdf_file.name

                target_path = all_pdfs_dir / target_name
                shutil.copy2(pdf_file, target_path)
                print(f"  [+] Copied: {pdf_file.name} -> {folder_name}/{target_name}")
                copied_count += 1

    print()
    print("========================================")
    print(f"Successfully generated and collected {copied_count} PDF(s) into: {all_pdfs_dir}")
    print("========================================")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="LabRecord Engine — Batch PDF Generator")
    parser.add_argument("directory", nargs="?", default=".", help="Root directory to scan for project folders")
    parser.add_argument("-n", "--name", default=None, help="Override student name for all generated PDFs")
    parser.add_argument("-r", "--roll-number", "--roll", dest="roll_number", default=None, help="Override student roll number")
    parser.add_argument("-o", "--overwrite", "--force", action="store_true", dest="overwrite", help="Overwrite existing output directory")
    parser.add_argument("--output-dir", "--out", dest="output_dir", default=None, help="Custom output folder name")
    args = parser.parse_args()
    batch_generate(
        start_dir=args.directory,
        name=args.name,
        roll_number=args.roll_number,
        output_dir=args.output_dir,
        overwrite=args.overwrite
    )
