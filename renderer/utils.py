# renderer/utils.py
"""Utility functions for the LabRecord engine.

This module contains helper functions that were previously scattered across
`renderer/document.py` and other files. They are extracted here to avoid
circular imports and to provide a stable public API for backward‑compatible
use.
"""
import os
import re
from typing import Any, Dict, Optional

def resolve_path(raw_path: str, doc_dir: str) -> str:
    """Return an absolute path for *raw_path* relative to *doc_dir*.

    The resolution strategy mirrors the historic behaviour of ``ImageObject``
    and ``TableObject``:
    1. If *raw_path* is already absolute, return it.
    2. Resolve relative to *doc_dir* and return the normalized path.
    3. As a fallback, return the normalized *raw_path* (which may be a
       relative path to the current working directory).
    """
    if not raw_path:
        return ""
    if os.path.isabs(raw_path):
        return raw_path
    primary = os.path.normpath(os.path.join(doc_dir, raw_path))
    if os.path.exists(primary):
        return primary
    return os.path.normpath(raw_path)

def clean_latex_math(text: str) -> str:
    """Sanitise LaTeX math for Matplotlib's mathtext parser.

    Matplotlib does not understand ``\text{}`` but accepts ``\mathrm{}``.
    This helper replaces common unsupported commands with equivalents that
    render correctly.
    """
    cleaned = re.sub(r"\\\\text\{([^}]*)\}", r"\\\\mathrm{\1}", text)
    return cleaned

def merge_styles(base: Dict[str, Any], overrides: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge two style dictionaries, giving precedence to *overrides*.

    The function performs a shallow merge – nested dictionaries are not deep‑
    merged because the existing configuration format treats nested keys as
    independent style groups.
    """
    if not overrides:
        return dict(base)
    merged = dict(base)
    merged.update(overrides)
    return merged
