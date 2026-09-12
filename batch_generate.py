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

def batch_generate(start_dir="."):
    start_dir = Path(start_dir).resolve()
    all_pdfs_dir = start_dir / "all_pdfs"
    all_pdfs_dir.mkdir(exist_ok=True)

    print("========================================")
    print("LabRecord Engine — Batch PDF Generator")
    print("========================================")
    print(f"Scanning directory : {start_dir}")
    print(f"Output directory   : {all_pdfs_dir}")
    print()

    project_dirs = []
    for root, dirs, files in os.walk(start_dir):
        root_path = Path(root)

        # Skip all_pdfs and .git folders
        if "all_pdfs" in root_path.parts or ".git" in root_path.parts:
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
                generated_pdfs = build_manifest(manifest_path)
            except Exception as e:
                print(f"  [-] ERROR building project in {display_name}: {e}")
                continue
        else:
            # Fallback to subprocess labfile generate
            import subprocess
            cmd = ["labfile", "generate", str(p)]
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
                print(f"  [+] Copied: {pdf_file.name} -> all_pdfs/{target_name}")
                copied_count += 1

    print()
    print("========================================")
    print(f"Successfully generated and collected {copied_count} PDF(s) into: {all_pdfs_dir}")
    print("========================================")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    batch_generate(target)
