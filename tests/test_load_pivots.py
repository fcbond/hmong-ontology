"""Tests for load_pivots.py: reading pinned releases from a Cygnet-format TOML."""

import subprocess
import sys
from pathlib import Path

import load_pivots


def test_release_names_give_lexicon_and_version(tmp_path: Path) -> None:
    toml = tmp_path / "pivots.toml"
    toml.write_text(
        'en = ["https://en-word.net/static/english-wordnet-2025-plus.xml.gz"]\n'
        'fr = ["https://example.org/v2.0/omw-fr-2.0.tar.xz"]\n'
        'cmn = ["https://example.org/v1.1/cow-1.1.tar.xz"]\n'
        'ja = ["https://example.org/v2.1/wnja-2.1.tar.xz"]\n'
        'id = ["https://example.org/v1.4/wnb-id-1.4.tar.xz"]\n'
        'xx = ["https://example.org/some-page.html"]\n',
        encoding="utf8")
    assert load_pivots.pinned_lexicons(toml) == {
        "oewn": "2025+", "omw-fr": "2.0", "cow": "1.1", "wnja": "2.1", "wnb-id": "1.4"}


def test_every_pivot_is_pinned() -> None:
    pinned = load_pivots.pinned_lexicons(load_pivots.WORDNETS_TOML)
    assert [name for name in load_pivots.PIVOTS if name not in pinned] == []


if __name__ == "__main__":
    sys.exit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-q"]))
