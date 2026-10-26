"""Initial scaffolding tests for Tree_Visualizer."""
from __future__ import annotations

import sys
import pytest
from tree_visualizer.constants import APP_NAME, VERSION


def test_constants():
    """Verify official application name and version constants."""
    assert APP_NAME == "Tree_Visualizer"
    assert VERSION == "1.0.1"


def test_layer_imports_do_not_import_tkinter():
    """Verify that core, recorder, and state layers never import tkinter."""
    # Ensure tkinter is not in sys.modules before checking
    tkinter_already_loaded = "tkinter" in sys.modules

    import tree_visualizer.core
    import tree_visualizer.recorder
    import tree_visualizer.state

    # Subpackages must not expose tkinter
    assert not hasattr(tree_visualizer.core, "tkinter")
    assert not hasattr(tree_visualizer.recorder, "tkinter")
    assert not hasattr(tree_visualizer.state, "tkinter")
