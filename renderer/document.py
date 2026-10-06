import os
import json
import csv

class ImageObject:
    def __init__(self, id, path, title="", rotation=0, doc_dir="."):
        self.id = str(id)
        self.raw_path = str(path) if path else ""
        self.title = str(title) if title else ""
        self.rotation = int(rotation) % 360
        self.doc_dir = os.path.abspath(doc_dir)

    @property
    def resolved_path(self):
        # Use unified path resolution utility
        from .utils import resolve_path
        return resolve_path(self.raw_path, self.doc_dir)


class TableObject:
    def __init__(self, number, title, element_type, elements, csv_path=None, doc_dir=".", delimiter=","):
        self.number = number
        self.title = title
        self.element_type = element_type.lower() if isinstance(element_type, str) else ""
        self.elements = elements or []
        self.csv_path = csv_path
        self.doc_dir = doc_dir
        self.delimiter = delimiter or ","
        self.csv_matrix = None

        if self.csv_path:
            self.load_csv()

    def load_csv(self):
        # Resolve CSV path using utils
        from .utils import resolve_path
        abs_path = resolve_path(self.csv_path, self.doc_dir)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f'ERROR: CSV file not found "{abs_path}" in {self.doc_dir}')

        matrix = []
        try:
            with open(abs_path, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f, delimiter=self.delimiter)
                for row in reader:
                    matrix.append([cell.strip() for cell in row])
        except Exception as e:
            raise ValueError(f'ERROR: Failed to read CSV file "{abs_path}": {e}')

        self.csv_matrix = matrix

    def validate(self):
        if self.element_type and self.element_type not in ("row", "column"):
            raise ValueError(f'ERROR: Table {self.number} contains invalid or mixed "row" and "column" elements.')

        for idx, elem in enumerate(self.elements):
            if isinstance(elem, dict):
                e_type = elem.get("element_type")
                if e_type and self.element_type and e_type.lower() != self.element_type:
                    raise ValueError(f'ERROR: Table {self.number} contains mixed "row" and "column" elements.')



import re

class LayoutNode:
    def __init__(self, data):
        if isinstance(data, (str, int, float)):
            self.node_type = "ref"
            self.image_id = str(data)
            self.children = []
        elif isinstance(data, dict):
            raw_type = str(data.get("type", "row")).lower()

            grid_match = re.match(r"^(\d+)x(\d+)$", raw_type)
            if raw_type == "grid" or grid_match or ("rows" in data and "cols" in data):
                self.node_type = "column"
                self.image_id = None

                if grid_match:
                    rows_cnt = int(grid_match.group(1))
                    cols_cnt = int(grid_match.group(2))
                else:
                    rows_cnt = int(data.get("rows", 1))
                    cols_cnt = int(data.get("cols", 1))

                raw_elements = data.get("elements", [])
                row_nodes = []
                for r in range(rows_cnt):
                    start_idx = r * cols_cnt
                    end_idx = min(start_idx + cols_cnt, len(raw_elements))
                    row_elems = raw_elements[start_idx:end_idx]
                    if row_elems:
                        row_dict = {
                            "type": "row",
                            "elements": row_elems
                        }
                        row_nodes.append(LayoutNode(row_dict))
                self.children = row_nodes

            elif raw_type == "freebox":
                self.node_type = "freebox"
                raw_img = data.get("image")
                if isinstance(raw_img, dict):
                    self.image_id = str(raw_img.get("id") or raw_img.get("path"))
                else:
                    self.image_id = str(raw_img) if raw_img is not None else ""
                self.position = data.get("position", {"x": 0, "y": 0})
                self.size = data.get("size", {"width": 100, "height": 100})
                self.children = []
            else:
                self.node_type = raw_type
                self.image_id = None
                self.children = [LayoutNode(c) for c in data.get("elements", [])]
        else:
            raise ValueError(f"Invalid layout node specification: {data}")


class ImageSubsection:
    def __init__(self, title, layout_data):
        self.title = title
        self.layout = LayoutNode(layout_data) if layout_data else None


from .graph import GraphObject


class Section:
    def __init__(self, data, doc_dir=".", global_images=None):
        raw_type = data.get("type")
        if not raw_type and any(k in data for k in ("x", "x_col", "x_column", "y", "y_col", "y_column", "graph_type", "chart_type")):
            self.type = "graph"
        elif not raw_type and any(k in data for k in ("csv", "csv_file")):
            self.type = "table"
        elif not raw_type and any(k in data for k in ("file", "code_file", "source", "code")):
            self.type = "code"
        elif raw_type and raw_type.lower() in ("side_by_side_table", "table_group"):
            self.type = "table"
        else:
            self.type = (raw_type or "text").lower()

        self.table_layout = data.get("layout")
        self.side_by_side = (
            bool(data.get("side_by_side")) or
            (self.table_layout == "side_by_side") or
            (isinstance(self.table_layout, dict) and self.table_layout.get("type") == "side_by_side") or
            (raw_type is not None and str(raw_type).lower() in ("side_by_side_table", "table_group"))
        )

        self.number = data.get("number", "")
        self.title = data.get("title", "")
        self.new_page = bool(data.get("new_page", False))
        self.blank_page = bool(data.get("blank_page") or data.get("blank") or self.type in ("blank", "blank_page", "empty", "empty_page", "raw_page"))
        self.no_header = bool(
            data.get("no_header") or
            data.get("empty") or
            data.get("clear") or
            data.get("raw") or
            (data.get("show_header") is False) or
            self.type in ("empty", "empty_page", "raw_page")
        )
        self.doc_dir = doc_dir

        # Code attributes
        self.code_text = ""
        self.code_path = None
        self.language = data.get("language") or data.get("lang") or ""
        self.show_line_numbers = data.get("show_line_numbers", data.get("line_numbers", True))

        if self.type == "code":
            code_file_rel = (
                data.get("file") or
                data.get("path") or
                data.get("code_file") or
                data.get("source")
            )
            if code_file_rel:
                self.code_path = code_file_rel
                if not os.path.isabs(code_file_rel):
                    abs_path = os.path.normpath(os.path.join(doc_dir, code_file_rel))
                else:
                    abs_path = code_file_rel

                if not os.path.exists(abs_path):
                    raise FileNotFoundError(f'ERROR: Code file not found "{abs_path}" in {doc_dir}')

                try:
                    with open(abs_path, "r", encoding="utf-8") as f:
                        self.code_text = f.read()
                except Exception as e:
                    raise ValueError(f'ERROR: Failed to read code file "{abs_path}": {e}')
            else:
                raw_code = data.get("code", data.get("text", ""))
                if isinstance(raw_code, list):
                    self.code_text = "\n".join(str(line) for line in raw_code)
                else:
                    self.code_text = str(raw_code)

        # Text attributes
        raw_text = data.get("text", "")
        if isinstance(raw_text, str):
            self.paragraphs = [raw_text] if raw_text else []
        elif isinstance(raw_text, list):
            self.paragraphs = [str(p) for p in raw_text]
        else:
            self.paragraphs = []

        # Table attributes
        self.tables = []
        self.table_items = []
        if self.type == "table":
            if "tables" in data:
                for t_data in data["tables"]:
                    if isinstance(t_data, dict) and ("tables" in t_data or t_data.get("side_by_side") or t_data.get("layout") == "side_by_side"):
                        group_tables = []
                        for sub_t in t_data.get("tables", []):
                            csv_p = sub_t.get("csv") or sub_t.get("csv_file") or sub_t.get("file") or sub_t.get("path")
                            delim = sub_t.get("delimiter") or sub_t.get("sep") or ","
                            tbl = TableObject(
                                sub_t.get("number", self.number),
                                sub_t.get("title", self.title),
                                sub_t.get("element_type"),
                                sub_t.get("elements"),
                                csv_path=csv_p,
                                doc_dir=doc_dir,
                                delimiter=delim
                            )
                            tbl.validate()
                            group_tables.append(tbl)
                            self.tables.append(tbl)
                        self.table_items.append({
                            "side_by_side": True,
                            "tables": group_tables,
                            "layout": t_data.get("layout")
                        })
                    else:
                        csv_p = t_data.get("csv") or t_data.get("csv_file") or t_data.get("file") or t_data.get("path")
                        delim = t_data.get("delimiter") or t_data.get("sep") or ","
                        tbl = TableObject(
                            t_data.get("number", self.number),
                            t_data.get("title", self.title),
                            t_data.get("element_type"),
                            t_data.get("elements"),
                            csv_path=csv_p,
                            doc_dir=doc_dir,
                            delimiter=delim
                        )
                        tbl.validate()
                        self.tables.append(tbl)
                        self.table_items.append(tbl)
            else:
                csv_p = data.get("csv") or data.get("csv_file") or (data.get("file") if "elements" not in data and "tables" not in data else None) or (data.get("path") if "elements" not in data and "tables" not in data else None)
                delim = data.get("delimiter") or data.get("sep") or ","
                tbl = TableObject(
                    data.get("number", self.number),
                    data.get("title", self.title),
                    data.get("element_type"),
                    data.get("elements"),
                    csv_path=csv_p,
                    doc_dir=doc_dir,
                    delimiter=delim
                )
                tbl.validate()
                self.tables.append(tbl)
                self.table_items.append(tbl)

        # Image attributes
        self.images = dict(global_images) if global_images else {}
        self.subsections = []

        if self.type == "image":
            raw_images = data.get("images", [])
            for img_d in raw_images:
                img_obj = ImageObject(
                    id=img_d.get("id"),
                    path=img_d.get("path"),
                    title=img_d.get("title", ""),
                    rotation=img_d.get("rotation", 0),
                    doc_dir=doc_dir
                )
                if img_obj.id in self.images and self.images[img_obj.id].raw_path != img_obj.raw_path:
                    raise ValueError(f'ERROR: Duplicate image ID "{img_obj.id}" in {doc_dir}')
                self.images[img_obj.id] = img_obj

            raw_subsections = data.get("subsections", [])
            for sub_d in raw_subsections:
                sub_title = sub_d.get("title", "")
                sub_layout = sub_d.get("layout")
                self.subsections.append(ImageSubsection(sub_title, sub_layout))

        # Graph attributes
        self.graphs = []
        if self.type in ("graph", "plot", "chart"):
            if "graphs" in data:
                for g_data in data["graphs"]:
                    g_obj = GraphObject(g_data, doc_dir=doc_dir, default_title=self.title, default_number=self.number)
                    g_obj.validate()
                    self.graphs.append(g_obj)
            elif "plots" in data:
                for g_data in data["plots"]:
                    g_obj = GraphObject(g_data, doc_dir=doc_dir, default_title=self.title, default_number=self.number)
                    g_obj.validate()
                    self.graphs.append(g_obj)
            else:
                g_obj = GraphObject(data, doc_dir=doc_dir, default_title=self.title, default_number=self.number)
                g_obj.validate()
                self.graphs.append(g_obj)


class Experiment:
    def __init__(self, data, doc_dir=".", global_images=None):
        self.number = data.get("number")  # Optional: None if omitted
        self.type = data.get("type")  # Optional: None if omitted
        self.title = data.get("title", "")
        self.date = data.get("date", "")
        self.sections = []
        for s_data in data.get("sections", []):
            self.sections.append(Section(s_data, doc_dir=doc_dir, global_images=global_images))


class DocumentModel:
    def __init__(self, data, doc_path="."):
        self.doc_path = os.path.abspath(doc_path)
        self.doc_dir = os.path.dirname(self.doc_path)

        self.template_name = data.get("template")

        doc_info = data.get("document", {})
        self.title = doc_info.get("title", "VLSI Engineering Lab Record")
        self.date = doc_info.get("date", "13/08/2026")

        # Extract student info (Name & Roll Number)
        student_info = doc_info.get("student", {}) if isinstance(doc_info.get("student"), dict) else {}
        root_student_info = data.get("student", {}) if isinstance(data.get("student"), dict) else {}

        self.name = str(
            doc_info.get("name") or 
            doc_info.get("student_name") or 
            doc_info.get("author") or 
            student_info.get("name") or 
            root_student_info.get("name") or 
            data.get("name") or 
            data.get("student_name") or 
            ""
        ).strip()

        self.roll_number = str(
            doc_info.get("roll_number") or 
            doc_info.get("roll_no") or 
            doc_info.get("roll") or 
            student_info.get("roll_number") or 
            student_info.get("roll_no") or 
            student_info.get("roll") or 
            root_student_info.get("roll_number") or 
            root_student_info.get("roll_no") or 
            root_student_info.get("roll") or 
            data.get("roll_number") or 
            data.get("roll_no") or 
            data.get("roll") or 
            ""
        ).strip()

        # Top-level Global Image Registry
        self.images = {}
        raw_global_images = data.get("images", [])
        for img_d in raw_global_images:
            if not isinstance(img_d, dict) or "id" not in img_d:
                continue
            img_obj = ImageObject(
                id=img_d.get("id"),
                path=img_d.get("path"),
                title=img_d.get("title", ""),
                rotation=img_d.get("rotation", 0),
                doc_dir=self.doc_dir
            )
            if img_obj.id in self.images:
                raise ValueError(f'ERROR: Duplicate image ID "{img_obj.id}" in {self.doc_path}')
            self.images[img_obj.id] = img_obj

        self.experiments = []
        raw_exps = data.get("experiments", [])
        if not raw_exps and "experiment" in data:
            raw_exps = [data["experiment"]]

        for exp_d in raw_exps:
            self.experiments.append(Experiment(exp_d, doc_dir=self.doc_dir, global_images=self.images))

        self.validate()

    def validate(self):
        # Validate image references exist and check file existence when image is referenced
        for exp in self.experiments:
            for sec in exp.sections:
                if sec.type == "image":
                    for sub in sec.subsections:
                        self._validate_layout_references(sub.layout, sec.images)

    def _validate_layout_references(self, node, image_map):
        if not node:
            return
        if node.node_type == "ref" or node.node_type == "freebox":
            ref_id = node.image_id
            if ref_id not in image_map:
                raise KeyError(f'ERROR: Image reference "{ref_id}" was not found in the image registry in {self.doc_path}.')
            img_obj = image_map[ref_id]
            resolved = img_obj.resolved_path
            if resolved and not os.path.exists(resolved):
                print(f"WARNING: Image file not found for ID '{ref_id}': {resolved}")
        for child in node.children:
            self._validate_layout_references(child, image_map)


def load_document(doc_path):
    if not os.path.exists(doc_path):
        raise FileNotFoundError(f"Input document file not found: {doc_path}")

    with open(doc_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in document file {doc_path}: {e}")

    return DocumentModel(data, doc_path=doc_path)
