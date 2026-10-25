"""Persistent application settings stored in the user's home folder.

Tolerates missing files, unreadable directories, and corrupted JSON
by falling back safely to canonical defaults.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass
class Settings:
    """Persistent user preferences and UI configuration."""

    theme: str = "dark"  # "dark" | "light"
    bt_label_type: str = "numbers"  # "numbers" | "letters"
    build_label_type: str = "letters"  # "letters" | "numbers"
    sidebar_collapsed: bool = False
    window_width: int = 1200
    window_height: int = 800

    @classmethod
    def get_settings_path(cls) -> str:
        """Return the absolute path to the settings JSON file in user home directory."""
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, ".tree_visualizer", "settings.json")

    @classmethod
    def load(cls, filepath: Optional[str] = None) -> Settings:
        """Load settings from JSON file.

        Tolerates missing files, corrupt JSON, or malformed data by returning defaults.
        """
        path = filepath if filepath is not None else cls.get_settings_path()
        if not os.path.exists(path):
            return cls()

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                return cls()

            # Extract fields with safe defaults
            theme = data.get("theme", "dark")
            if theme not in ("dark", "light"):
                theme = "dark"

            bt_label_type = data.get("bt_label_type", "numbers")
            if bt_label_type not in ("numbers", "letters"):
                bt_label_type = "numbers"

            build_label_type = data.get("build_label_type", "letters")
            if build_label_type not in ("letters", "numbers"):
                build_label_type = "letters"

            sidebar_collapsed = bool(data.get("sidebar_collapsed", False))

            try:
                window_width = int(data.get("window_width", 1200))
                window_height = int(data.get("window_height", 800))
                window_width = max(900, min(window_width, 3840))
                window_height = max(600, min(window_height, 2160))
            except (ValueError, TypeError):
                window_width = 1200
                window_height = 800

            return cls(
                theme=theme,
                bt_label_type=bt_label_type,
                build_label_type=build_label_type,
                sidebar_collapsed=sidebar_collapsed,
                window_width=window_width,
                window_height=window_height,
            )

        except Exception:
            # Tolerates any JSON decode error, permission error, or OS error
            return cls()

    def save(self, filepath: Optional[str] = None) -> bool:
        """Save current settings to JSON file.

        Returns True on success, False if file could not be written.
        """
        path = filepath if filepath is not None else self.get_settings_path()
        try:
            folder = os.path.dirname(path)
            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, indent=2)
            return True
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return asdict(self)
