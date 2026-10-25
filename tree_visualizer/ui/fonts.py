"""Cross-platform font loader and typography manager.

Loads the custom cursive font 'Rouge Script' for definition cards:
- On Windows: Uses GDI AddFontResourceExW with FR_PRIVATE (process-local).
- On non-Windows: Uses tkextrafont if installed; otherwise falls back to a serif italic
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
_ROUGE_SCRIPT_LOADED: bool = False
_ROUGE_SCRIPT_FAMILY: str = "Rouge Script"
_FALLBACK_SERIF_FAMILY: str = "Georgia" if sys.platform == "win32" else "Times New Roman"

FR_PRIVATE = 0x10


def get_assets_font_path() -> str:
    """Return the absolute path to RougeScript-Regular.ttf."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "assets", "fonts", "RougeScript-Regular.ttf")


def load_custom_fonts() -> bool:
    """Load Rouge Script into the process font table.

    Returns True if Rouge Script was successfully loaded or is available, False if fallback.
    """
    global _ROUGE_SCRIPT_LOADED
    if _ROUGE_SCRIPT_LOADED:
        return True

    font_path = get_assets_font_path()
    if not os.path.exists(font_path):
        logger.warning(
            "Rouge Script font file not found at '%s'. Falling back to '%s'.",
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
                _ROUGE_SCRIPT_LOADED = True
                logger.info("Successfully loaded Rouge Script via GDI AddFontResourceExW.")
                return True
            else:
                logger.warning(
                    "AddFontResourceExW returned 0 fonts added. Falling back to '%s'.",
                    _FALLBACK_SERIF_FAMILY,
                )
        except Exception as e:
            logger.warning("Failed to load Rouge Script font on Windows: %s", e)
    else:
        # Non-Windows platform: attempt tkextrafont
        try:
            import tkextrafont  # type: ignore
            # tkextrafont loaded lazily if Tk root is initialized
            _ROUGE_SCRIPT_LOADED = True
            logger.info("Rouge Script will be loaded via tkextrafont.")
            return True
        except ImportError:
            logger.warning(
                "tkextrafont is not installed on this non-Windows platform. "
                "Rouge Script cannot be loaded natively; falling back to serif italic '%s'.",
                _FALLBACK_SERIF_FAMILY,
            )
        except Exception as e:
            logger.warning("Failed to register font with tkextrafont: %s", e)

    return False


def get_definition_font_family() -> str:
    """Return font family name for empty canvas definition card."""
    load_custom_fonts()
    if _ROUGE_SCRIPT_LOADED:
        return _ROUGE_SCRIPT_FAMILY
    return _FALLBACK_SERIF_FAMILY


def get_definition_title_font(size: int = 28) -> Tuple[str, int, str]:
    """Return font tuple for definition card title."""
    family = get_definition_font_family()
    weight = "normal" if family == _ROUGE_SCRIPT_FAMILY else "bold italic"
    return (family, size, weight)


def get_definition_body_font(size: int = 16) -> Tuple[str, int, str]:
    """Return font tuple for definition card narrative body."""
    family = get_definition_font_family()
    weight = "normal" if family == _ROUGE_SCRIPT_FAMILY else "italic"
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
