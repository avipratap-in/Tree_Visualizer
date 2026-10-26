"""Cross-platform font loader and typography manager.

Loads custom bundled fonts for definition cards:
- Heading: 'Cinzel Decorative' Bold (700)
- Body: 'Agbalumo' Regular (400)
- Hint: 'Agbalumo' Regular (400)

Loading mechanism:
- On Windows: Uses GDI AddFontResourceExW with FR_PRIVATE (process-local).
- On non-Windows: Uses tkextrafont if installed; otherwise falls back to Georgia/serif
  with a single logged warning.

Other application text uses Segoe UI on Windows or platform sans-serif defaults.
"""
from __future__ import annotations

import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Named Constants: Font Families, Weights, and Baseline Scaled Sizes (+20%)
# ---------------------------------------------------------------------------
FONT_FAMILY_HEADING: str = "Cinzel Decorative"
FONT_FAMILY_BODY: str = "Agbalumo"
FONT_FAMILY_HINT: str = "Agbalumo"
FONT_FAMILY_FALLBACK: str = "Georgia"

FONT_WEIGHT_HEADING: str = "bold"
FONT_WEIGHT_BODY: str = "normal"
FONT_WEIGHT_HINT: str = "normal"

# Default baseline font sizes (increased 20% from v1.0.0 baselines 28, 17, 10)
FONT_SIZE_HEADING: int = 34  # round(28 * 1.2) = 34
FONT_SIZE_BODY: int = 20     # round(17 * 1.2) = 20
FONT_SIZE_HINT: int = 12     # round(10 * 1.2) = 12

# Minimum clamped font sizes
MIN_FONT_SIZE_HEADING: int = 12
MIN_FONT_SIZE_BODY: int = 10
MIN_FONT_SIZE_HINT: int = 10

FR_PRIVATE = 0x10

# Tracking loaded font availability
_CUSTOM_FONTS_LOADED: bool = False
_FALLBACK_WARNED: bool = False
_BUNDLED_FONT_FILES = [
    "Agbalumo-Regular.ttf",
    "CinzelDecorative-Regular.ttf",
    "CinzelDecorative-Bold.ttf",
]


def get_assets_font_path(filename: str) -> str:
    """Return the absolute path to a bundled custom font file."""
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
    """Load bundled custom fonts into the process font table.

    Returns True if custom fonts were successfully registered, False if fallback.
    """
    global _CUSTOM_FONTS_LOADED, _FALLBACK_WARNED
    if _CUSTOM_FONTS_LOADED:
        return True

    loaded_all = True

    if sys.platform == "win32":
        try:
            import ctypes
            for filename in _BUNDLED_FONT_FILES:
                font_path = get_assets_font_path(filename)
                if not os.path.exists(font_path):
                    loaded_all = False
                    continue
                num_added = ctypes.windll.gdi32.AddFontResourceExW(
                    os.path.abspath(font_path),
                    FR_PRIVATE,
                    0,
                )
                if num_added <= 0:
                    loaded_all = False
            if loaded_all:
                _CUSTOM_FONTS_LOADED = True
                logger.info("Successfully registered Agbalumo and Cinzel Decorative via GDI AddFontResourceExW.")
                return True
        except Exception as e:
            loaded_all = False
            logger.warning("Failed to register Windows GDI fonts: %s", e)
    else:
        # Non-Windows platform: attempt registration via tkextrafont
        try:
            import tkextrafont  # type: ignore
            for filename in _BUNDLED_FONT_FILES:
                font_path = get_assets_font_path(filename)
                if os.path.exists(font_path):
                    try:
                        tkextrafont.Font(file=font_path)
                    except Exception:
                        pass
            _CUSTOM_FONTS_LOADED = True
            logger.info("Registered custom fonts via tkextrafont.")
            return True
        except ImportError:
            loaded_all = False
        except Exception as e:
            loaded_all = False
            logger.warning("Failed to register font with tkextrafont: %s", e)

    if not _CUSTOM_FONTS_LOADED and not _FALLBACK_WARNED:
        logger.warning(
            "Custom fonts ('Agbalumo', 'Cinzel Decorative') could not be loaded; "
            "falling back to '%s'.",
            FONT_FAMILY_FALLBACK,
        )
        _FALLBACK_WARNED = True

    return _CUSTOM_FONTS_LOADED


def get_definition_font_family(role: str = "body") -> str:
    """Return active font family name for empty canvas definition card."""
    load_custom_fonts()
    if _CUSTOM_FONTS_LOADED:
        if role == "heading" or role == "title":
            return FONT_FAMILY_HEADING
        return FONT_FAMILY_BODY
    return FONT_FAMILY_FALLBACK


def get_definition_title_font(size: int = FONT_SIZE_HEADING) -> Tuple[str, int, str]:
    """Return font tuple for definition card heading (Cinzel Decorative Bold)."""
    return get_definition_heading_font(size)


def get_definition_heading_font(size: int = FONT_SIZE_HEADING) -> Tuple[str, int, str]:
    """Return font tuple for definition card heading (Cinzel Decorative Bold)."""
    family = get_definition_font_family("heading")
    weight = FONT_WEIGHT_HEADING
    return (family, size, weight)


def get_definition_body_font(size: int = FONT_SIZE_BODY) -> Tuple[str, int, str]:
    """Return font tuple for definition card narrative body (Agbalumo Regular)."""
    family = get_definition_font_family("body")
    weight = FONT_WEIGHT_BODY
    return (family, size, weight)


def get_definition_hint_font(size: int = FONT_SIZE_HINT) -> Tuple[str, int, str]:
    """Return font tuple for definition card hint line (Agbalumo Regular)."""
    family = get_definition_font_family("hint")
    weight = FONT_WEIGHT_HINT
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
