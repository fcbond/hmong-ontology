"""Tests for facts_tex.py, which turns facts.json into LaTeX macros."""

from __future__ import annotations

import facts_tex as ft


def test_macro_key_replaces_unsafe_characters() -> None:
    assert ft.macro_key("tiers.linked, stronger evidence") == "tiers.linked-stronger-evidence"
    assert ft.macro_key("coverage.everything.linked") == "coverage.everything.linked"


def test_format_value_separates_thousands_only_for_integers() -> None:
    assert ft.format_value(1747) == "1,747"
    assert ft.format_value(64.6) == "64.6"


def test_render_defines_every_numeric_leaf() -> None:
    text = ft.render({"a": {"b": 1747, "c": "x", "d": True}, "pct": 64.6})
    assert r"\csname fact@a.b\endcsname{1,747}" in text
    assert r"\csname fact@pct\endcsname{64.6}" in text
    assert "fact@a.c" not in text and "fact@a.d" not in text
