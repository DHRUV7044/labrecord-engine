import argparse
import sys
import os

from .pdf import build_manifest
from .templates import init_project
from .scanner import scan_images

VERSION = "1.0.0"

def find_manifest(path_arg=None):
    """
    Locates main.json build manifest file using project discovery rules:
    1. Explicit manifest/project path argument.
    2. main.json in current working directory.
    3. main.json in parent directories.
    4. Otherwise raises FileNotFoundError.
    """
    if path_arg:
        abs_p = os.path.abspath(path_arg)
        if os.path.isfile(abs_p):
            return abs_p
        elif os.path.isdir(abs_p):
            manifest_in_dir = os.path.join(abs_p, "main.json")
            if os.path.exists(manifest_in_dir):
                return manifest_in_dir
            else:
                raise FileNotFoundError(f"Could not locate 'main.json' inside directory: {abs_p}")
        else:
            raise FileNotFoundError(f"Specified project path does not exist: {path_arg}")

    # 2. Search current directory
    cwd = os.getcwd()
    manifest_cwd = os.path.join(cwd, "main.json")
    if os.path.exists(manifest_cwd):
        return manifest_cwd

    # 3. Search parent directories
    curr = cwd
    while True:
        parent = os.path.dirname(curr)
        if parent == curr:  # Reached filesystem root
            break
        manifest_parent = os.path.join(parent, "main.json")
        if os.path.exists(manifest_parent):
            return manifest_parent
        curr = parent

    # 4. Error if not found
    raise FileNotFoundError(
        "Could not locate 'main.json' in current directory or parent directories.\n"
        "Run 'labfile init' to initialize a project, or specify a manifest path:\n"
        "    labfile generate /path/to/main.json"
    )


from .template_loader import list_available_templates

def handle_templates(args):
    templates = list_available_templates()
    print("Available templates:")
    for t in templates:
        print(f"  {t}")


def handle_init(args):
    try:
        init_project(
            target_dir=args.directory,
            template_name=args.template,
            make_image_dir=args.makeimagedir,
            force=args.force
        )

        if args.scan:
            scan_dir = args.scan if isinstance(args.scan, str) else args.directory
            rec_path = os.path.join(args.directory, "record.json")
            added, skipped = scan_images(image_dir=scan_dir, record_json_path=rec_path)
            print(f"Scanned '{scan_dir}': registered {len(added)} new image(s) in record.json.")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


def handle_generate(args):
    print("========================================")
    print("LabRecord Engine")
    print("========================================")
    print()

    try:
        manifest_path = find_manifest(args.path)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print(f"Using manifest: {manifest_path}")
    print()

    try:
        results = build_manifest(manifest_path)
    except Exception as e:
        print(f"FATAL ERROR: Failed to process manifest '{manifest_path}': {e}")
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
    print(f"{success_count}/{total_jobs} jobs completed successfully")
    print("========================================")

    if success_count < total_jobs:
        sys.exit(1)
    else:
        sys.exit(0)


def handle_scan(args):
    print("========================================")
    print("LabRecord Engine — Image Scanner")
    print("========================================")
    print()

    try:
        added, skipped = scan_images(
            image_dir=args.directory,
            record_json_path=args.record,
            recursive=args.recursive,
            use_abs=args.abs,
            force=args.force
        )

        print(f"Scanned directory : {args.directory}")
        print(f"Target document   : {args.record}")
        print()

        if added:
            print(f"Added {len(added)} image(s) to image registry in {args.record}:")
            for img_id, img_path in added:
                print(f"  [+] ID: {img_id:20s} -> {img_path}")
            print()

        if skipped:
            print(f"Skipped {len(skipped)} image(s) (already registered or duplicate):")
            for img_id, img_path, reason in skipped:
                print(f"  [-] ID: {img_id:20s} -> {img_path} ({reason})")
            print()

        print(f"Updated {args.record} successfully.")

    except Exception as e:
        print(f"ERROR: Image scanning failed: {e}")
        sys.exit(1)


class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print(f"ERROR: {message}\n")
        self.print_help()
        sys.exit(2)


def main():
    parser = CustomArgumentParser(
        prog="labfile",
        description="LabRecord Engine — PDF Typesetting & Build CLI",
        epilog="Use 'labfile <command> --help' for detailed command options."
    )
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {VERSION}")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize a LabRecord project",
        description="Creates basic project files (main.json, config.json, record.json, output/)."
    )
    init_parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory where project files should be created (default: current directory)"
    )
    init_parser.add_argument(
        "-t", "--template",
        default="default",
        help="Template to use for initialization (default: 'default')"
    )
    init_parser.add_argument(
        "-makeimagedir", "--makeimagedir",
        action="store_true",
        help="Optionally create an images/ directory for convenience"
    )
    init_parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force overwrite of existing project template files"
    )
    init_parser.add_argument(
        "--scan",
        nargs="?",
        const=".",
        default=None,
        help="Scan directory for images during initialization and add them to record.json"
    )

    # generate command
    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate PDFs from main.json",
        description="Locates main.json, processes build jobs, and generates clean A4 PDFs."
    )
    generate_parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Optional path to main.json manifest file or project directory"
    )

    # scan command
    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan directory for images and add them to document JSON",
        description="Scans a directory for image files (.png, .jpg, .svg, etc.) and registers them in record.json."
    )
    scan_parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to scan for image files (default: current directory)"
    )
    scan_parser.add_argument(
        "-r", "--record",
        default="record.json",
        help="Target document JSON file to update (default: 'record.json')"
    )
    scan_parser.add_argument(
        "--recursive",
        action="store_true",
        help="Scan directory recursively"
    )
    scan_parser.add_argument(
        "--abs",
        action="store_true",
        help="Store absolute paths instead of relative paths"
    )
    scan_parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Overwrite existing image entries with matching IDs"
    )

    # templates command
    templates_parser = subparsers.add_parser(
        "templates",
        help="List available document templates",
        description="Lists all installed/available document templates."
    )

    args = parser.parse_args()

    if args.command == "init":
        handle_init(args)
    elif args.command == "generate":
        handle_generate(args)
    elif args.command == "scan":
        handle_scan(args)
    elif args.command == "templates":
        handle_templates(args)
    else:
        parser.print_help()
        sys.exit(0)



if __name__ == "__main__":
    main()
