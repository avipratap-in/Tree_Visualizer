"""Pytest configuration and shared fixtures for Tree_Visualizer."""
from __future__ import annotations

import os
import sys
import pytest


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
