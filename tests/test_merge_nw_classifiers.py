"""Tests for merge_nw_classifiers.py, which folds Nathan White's list into ours."""

import subprocess
import sys

import merge_nw_classifiers as m


def ours(*rows: tuple[str, str, str]) -> list[dict[str, str]]:
    """Rows of classifiers.tsv from (form, dialect, source) triples."""
    out = []
    for form, dialect, source in rows:
        row = dict.fromkeys(m.FIELDS, "")
        row.update(FORM=form, DIALECT=dialect, SOURCE=source)
        out.append(row)
    return out


def nw(form: str, dialect: str, gloss: str, category: str, citation: str = "",
       note: str = "") -> dict[str, str]:
    return {"FORM": form, "DIALECT": dialect, "GLOSS": gloss, "CATEGORY": category,
            "CITATION": citation, "NOTE": note}


def test_source_keys() -> None:
    assert m.source_keys("White 2019:224,226;White 2021:302,354") == [
        "W19:224,226", "W:302,354"]
    assert m.source_keys("") == ["NW:p.c."]


def test_sandhi_bases_follow_the_tone_rule() -> None:
    assert m.sandhi_bases("leeg") == ["leej", "lees", "leem"]
    assert m.sandhi_bases("xyoos") == ["xyoo"]
    assert m.sandhi_bases("qho") == ["qhov"]
    assert m.sandhi_bases("kab") == []


def test_existing_row_gains_only_the_new_citation() -> None:
    table = ours(("cov", "WH", "B:24; W:354"), ("cov", "GM", "W:354"))
    added, _ = m.merge(table, [nw("cov", "CO", "cl:pa", "non-singular",
                                  "White 2019:224;White 2021:302,354")])
    assert added == []
    assert [row["SOURCE"] for row in table] == ["B:24; W:354; W19:224", "W:354; W19:224"]


def test_common_form_becomes_a_row_per_dialect_and_a_sandhi_form_a_variant() -> None:
    table = ours(("xyoo", "WH", "W:345"), ("xyoo", "GM", "W:345"))
    added, _ = m.merge(table, [
        nw("xyoo", "CO", "cl:year", "mensural:time", "White 2021:345"),
        nw("xyoos", "CO", "cl:year", "mensural:time", "White 2021:137", "sandhi form"),
    ])
    assert [(r["FORM"], r["DIALECT"], r["DISPOSITION"]) for r in added] == [
        ("xyoos", "WH", "variant-of:xyoo"), ("xyoos", "GM", "variant-of:xyoo")]
    assert added[0]["CLASS"] == "mensural"


def test_sandhi_form_needs_a_base_with_the_same_gloss() -> None:
    table = ours(("kauj", "WH", "W:340"))
    added, log = m.merge(table, [
        nw("kauj", "WH", "cl:spool", "mensural", "White 2021:340"),
        nw("kaug", "WH", "vcl:bite", "verbal action", "White 2021:538", "sandhi form"),
    ])
    assert added == []
    assert any(line.startswith("SKIP   kaug") for line in log)


def test_green_mong_spelling_is_not_made_white_hmong() -> None:
    added, _ = m.merge([], [nw("dlus", "CO", "mw:span", "measure word",
                                "White 2021:367")])
    assert [(r["FORM"], r["DIALECT"]) for r in added] == [("dlus", "GM")]
    assert added[0]["DEFINITION"] == "a measure word glossed 'span' by White"


if __name__ == "__main__":
    sys.exit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-q"]))
