"""Pytest configuration and shared fixtures for Tree_Visualizer."""
from __future__ import annotations

import os
import sys
import pytest


# Ensure Windows CI runner finds tcl and tk libraries correctly
if sys.platform.startswith("win"):
    base_prefix = getattr(sys, "base_prefix", sys.prefix)
    tcl_root = os.path.join(base_prefix, "tcl")
    if os.path.isdir(tcl_root):
        for item in os.listdir(tcl_root):
            full = os.path.join(tcl_root, item)
            if os.path.isdir(full):
                if item.startswith("tcl") and "TCL_LIBRARY" not in os.environ:
                    os.environ["TCL_LIBRARY"] = full
                elif item.startswith("tk") and "TK_LIBRARY" not in os.environ:
                    os.environ["TK_LIBRARY"] = full


def has_display() -> bool:
    """Check if a graphical display environment is available for Tkinter GUI tests."""
    if sys.platform.startswith("win"):
        # On Windows, a GUI session is typically available unless running as headless service
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            root.destroy()
            return True
        except Exception:
            return False
    else:
        # On Linux / macOS, verify DISPLAY or WAYLAND_DISPLAY
        if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
            return False
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            root.destroy()
            return True
        except Exception:
            return False


requires_display = pytest.mark.skipif(
    not has_display(),
    reason="Graphical display not available (headless environment)."
)
