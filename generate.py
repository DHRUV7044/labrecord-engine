#!/usr/bin/env python3
import sys
import os

from renderer.pdf import build_manifest

def main():
    manifest_file = "main.json"
    if len(sys.argv) > 1:
        manifest_file = sys.argv[1]

    print("========================================")
    print("LabRecord Engine")
    print("========================================")
    print()

    if not os.path.exists(manifest_file):
        print(f"ERROR: Manifest file '{manifest_file}' not found.")
        sys.exit(1)

    try:
        results = build_manifest(manifest_file)
    except Exception as e:
        print(f"FATAL ERROR: Failed to execute manifest '{manifest_file}': {e}")
        sys.exit(1)

    total_jobs = len(results)
    success_count = 0

    for idx, (in_path, out_path, success, err_msg) in enumerate(results, start=1):
        print(f"[{idx}/{total_jobs}] {in_path}")
        print(f"      -> {out_path}")
        if success:
            print("      SUCCESS")
            success_count += 1
        else:
            print(f"      FAILED: {err_msg}")
        print()

    print("========================================")
    print(f"{success_count}/{total_jobs} PDFs generated successfully")
    print("========================================")

    if success_count < total_jobs:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
