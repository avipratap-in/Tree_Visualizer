"""Cross-platform font loader and typography manager.

Loads the custom font 'Special Elite' for definition cards:
- On Windows: Uses GDI AddFontResourceExW with FR_PRIVATE (process-local).
- On non-Windows: Uses tkextrafont if installed; otherwise falls back to a typewriter/monospace
  font with a logged warning.

Other application text uses Segoe UI on Windows or platform sans-serif defaults.
"""
from __future__ import annotations

import logging
import os
import sys
from typing import Any, Optional, Tuple

logger = logging.getLogger(__name__)

# Track loaded font availability
_SPECIAL_ELITE_LOADED: bool = False
_SPECIAL_ELITE_FAMILY: str = "Special Elite"
_FALLBACK_SERIF_FAMILY: str = "Courier New" if sys.platform == "win32" else "monospace"

FR_PRIVATE = 0x10


def get_assets_font_path(filename: str = "SpecialElite-Regular.ttf") -> str:
    """Return the absolute path to custom font file."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        for rel in [
            os.path.join("tree_visualizer", "assets", "fonts", filename),
            os.path.join("assets", "fonts", filename),
        ]:
            candidate = os.path.join(sys._MEIPASS, rel)
            if os.path.exists(candidate):
                return candidate

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "assets", "fonts", filename)


def load_custom_fonts() -> bool:
    """Load Special Elite font into the process font table.

    Returns True if Special Elite was successfully loaded or is available, False if fallback.
    """
    global _SPECIAL_ELITE_LOADED
    if _SPECIAL_ELITE_LOADED:
        return True

    font_path = get_assets_font_path("SpecialElite-Regular.ttf")
    if not os.path.exists(font_path):
        logger.warning(
            "Special Elite font file not found at '%s'. Falling back to '%s'.",
            font_path,
            _FALLBACK_SERIF_FAMILY,
        )
        return False

    if sys.platform == "win32":
        try:
            import ctypes
            num_added = ctypes.windll.gdi32.AddFontResourceExW(
                os.path.abspath(font_path),
                FR_PRIVATE,
                0,
            )
            if num_added > 0:
                _SPECIAL_ELITE_LOADED = True
                logger.info("Successfully loaded Special Elite via GDI AddFontResourceExW.")
                return True
            else:
                logger.warning(
                    "AddFontResourceExW returned 0 fonts added. Falling back to '%s'.",
                    _FALLBACK_SERIF_FAMILY,
                )
        except Exception as e:
            logger.warning("Failed to load Special Elite font on Windows: %s", e)
    else:
        # Non-Windows platform: attempt tkextrafont
        try:
            import tkextrafont  # type: ignore
            # tkextrafont loaded lazily if Tk root is initialized
            _SPECIAL_ELITE_LOADED = True
            logger.info("Special Elite will be loaded via tkextrafont.")
            return True
        except ImportError:
            logger.warning(
                "tkextrafont is not installed on this non-Windows platform. "
                "Special Elite cannot be loaded natively; falling back to serif '%s'.",
                _FALLBACK_SERIF_FAMILY,
            )
        except Exception as e:
            logger.warning("Failed to register font with tkextrafont: %s", e)

    return False


def get_definition_font_family() -> str:
    """Return font family name for empty canvas definition card."""
    load_custom_fonts()
    if _SPECIAL_ELITE_LOADED:
        return _SPECIAL_ELITE_FAMILY
    return _FALLBACK_SERIF_FAMILY


def get_definition_title_font(size: int = 34) -> Tuple[str, int, str]:
    """Return font tuple for definition card title (default size increased 20% to 34)."""
    family = get_definition_font_family()
    weight = "normal"
    return (family, size, weight)


def get_definition_body_font(size: int = 20) -> Tuple[str, int, str]:
    """Return font tuple for definition card narrative body (default size increased 20% to 20)."""
    family = get_definition_font_family()
    weight = "normal"
    return (family, size, weight)


def get_ui_font(size: int = 10, bold: bool = False, italic: bool = False) -> Tuple[str, int, str]:
    """Return standard application UI font tuple (Segoe UI or system sans-serif)."""
    if sys.platform == "win32":
        family = "Segoe UI"
    elif sys.platform == "darwin":
        family = "SF Pro Text"
    else:
        family = "DejaVu Sans"

    modifiers = []
    if bold:
        modifiers.append("bold")
    if italic:
        modifiers.append("italic")
    style_str = " ".join(modifiers) if modifiers else "normal"
    return (family, size, style_str)


def get_code_font(size: int = 10, bold: bool = False) -> Tuple[str, int, str]:
    """Return monospaced font tuple for pseudocode and values."""
    if sys.platform == "win32":
        family = "Consolas"
    elif sys.platform == "darwin":
        family = "Menlo"
    else:
        family = "DejaVu Sans Mono"

    return (family, size, "bold" if bold else "normal")
