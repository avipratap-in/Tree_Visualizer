"""Unit tests for Settings persistence and fault tolerance."""
from __future__ import annotations

import json
import os
import tempfile
import pytest
from tree_visualizer.state.settings import Settings


def test_settings_defaults():
    s = Settings()
    assert s.theme == "dark"
    assert s.bt_label_type == "numbers"
    assert s.build_label_type == "letters"
    assert s.sidebar_collapsed is False
    assert s.window_width == 1200
    assert s.window_height == 800


def test_settings_save_and_load(tmp_path):
    filepath = str(tmp_path / "settings.json")
    s1 = Settings(
        theme="light",
        bt_label_type="letters",
        build_label_type="numbers",
        sidebar_collapsed=True,
        window_width=1400,
        window_height=900,
    )
    assert s1.save(filepath) is True

    s2 = Settings.load(filepath)
    assert s2.theme == "light"
    assert s2.bt_label_type == "letters"
    assert s2.build_label_type == "numbers"
    assert s2.sidebar_collapsed is True
    assert s2.window_width == 1400
    assert s2.window_height == 900


def test_settings_missing_file():
    s = Settings.load("/path/to/non_existent_settings_file.json")
    assert s.theme == "dark"
    assert s.window_width == 1200


def test_settings_corrupted_file(tmp_path):
    filepath = str(tmp_path / "corrupt_settings.json")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("{this is invalid json!@@#$$%}")

    # Must tolerate corruption without crashing and return defaults
    s = Settings.load(filepath)
    assert s.theme == "dark"
    assert s.bt_label_type == "numbers"


def test_settings_invalid_values_sanitization(tmp_path):
    filepath = str(tmp_path / "bad_values.json")
    bad_data = {
        "theme": "neon-glow-invalid",
        "bt_label_type": "emojis",
        "build_label_type": "hieroglyphs",
        "sidebar_collapsed": "not_a_bool",
        "window_width": "invalid_number",
        "window_height": -999,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(bad_data, f)

    s = Settings.load(filepath)
    # Must fallback to sanitized canonical defaults
    assert s.theme == "dark"
    assert s.bt_label_type == "numbers"
    assert s.build_label_type == "letters"
    assert s.window_width == 1200
    assert s.window_height >= 600
