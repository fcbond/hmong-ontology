#!/usr/bin/env python3
"""Merge Nathan White's own classifier inventory into data/classifiers.tsv.

`data/classifiers-nw.tsv` is the classifier list Nathan White wrote by hand from
his own work (classifiers_sources.tsv in github.com/nathanmwhite/hmong-ontology),
one row per form with a gloss, his category and the pages that describe it in
White (2019) and White (2021). It adds forms neither our extraction of his thesis
nor Bisang has, tone-sandhi forms, and the citations to his 2019 chapter.

The merge is additive and can be rerun as his list grows. For each of his rows:

- `CO` (common to both varieties) becomes one row per dialect, as elsewhere in
  classifiers.tsv, except that a form spelt dl- is Green Mong only.
- A form and dialect already in classifiers.tsv gains his citations in SOURCE,
  and his category where WHITE_CATEGORY is empty. Nothing already there changes.
- A new form becomes a new row: CLASS by the mapping below, a DEFINITION built
  from his gloss, his citations, and his note (a borrowing, say).
- A sandhi form becomes `variant-of:<base>`, where the base is the form of the
  same gloss and dialect that the tone-melody rule (White 2021, Sec. 2.3.1:
  -j, -s, -m -> -g; -v -> bare; bare -> -s) turns into it, or the form his
  note names ("variant of fwj"). A sandhi form whose
  base cannot be found is reported and not added.

Citations become SOURCE keys: `W:<pages>` for White (2021), `W19:<pages>` for
White (2019), and `NW:p.c.` for a row he gives without a citation.

Usage:
    uv run scripts/merge_nw_classifiers.py --check   # report, write nothing
    uv run scripts/merge_nw_classifiers.py
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

#: his categories -> (WHITE_CATEGORY as classifiers.tsv spells it, CLASS)
CATEGORIES = {
    "sortal": ("sortal", "sortal"),
    "subordinate sortal": ("subordinate_sortal", "sortal"),
    "locational": ("locational", "sortal"),
    "possessed": ("possessed", "sortal"),
    "mensural": ("mensural", "mensural"),
    "mensural:time": ("time", "mensural"),
    "mensural:container": ("container", "mensural"),
    "measure word": ("measure_word", "mensural"),
    "mensural:collective": ("collective", "group"),
    "non-singular": ("non_singular", "group"),
    "mensural:kind": ("kind", "taxonomic"),
    "verbal action": ("verbal_action", "event"),
}

#: how a definition names each of his categories
CATEGORY_PHRASE = {
    "sortal": "a sortal classifier",
    "subordinate_sortal": "a subordinate sortal classifier",
    "locational": "a locational classifier",
    "possessed": "a possessed classifier",
    "mensural": "a mensural classifier",
    "time": "a mensural classifier of time",
    "container": "a container classifier",
    "measure_word": "a measure word",
    "collective": "a collective classifier",
    "non_singular": "a non-singular classifier",
    "kind": "a kind classifier",
    "verbal_action": "a verbal action classifier",
}

FIELDS = ["FORM", "DIALECT", "CLASS", "WHITE_CATEGORY", "BISANG_CATEGORY",
          "FUNCTION", "DEFINITION", "EXAMPLES", "SOURCE", "NOTE", "DISPOSITION"]

#: RPA tone letters: a syllable ending in none of them has the mid tone
TONE_LETTERS = "bjvsgmd"


def read_nw(path: Path) -> list[dict[str, str]]:
    """His rows, skipping comments and the header row."""
    rows = []
    for line in path.read_text(encoding="utf8").splitlines():
        if not line.strip() or line.startswith("#") or line.startswith("FORM\t"):
            continue
        cells = [cell.strip() for cell in line.split("\t")] + [""] * 6
        form, dialect, gloss, category, citation, note = cells[:6]
        rows.append({"FORM": form, "DIALECT": dialect, "GLOSS": gloss,
                     "CATEGORY": category, "CITATION": citation, "NOTE": note})
    return rows


def source_keys(citation: str) -> list[str]:
    """`White 2019:224,226;White 2021:302` -> ["W19:224,226", "W:302"]."""
    keys = []
    for part in filter(None, (p.strip() for p in citation.split(";"))):
        match = re.fullmatch(r"White (\d{4}):\s*(.+)", part)
        if not match:
            raise ValueError(f"unrecognised citation {part!r}")
        year, pages = match.groups()
        key = "W:" if year == "2021" else f"W{year[2:]}:"
        keys.append(key + pages.replace(" ", ""))
    return keys or ["NW:p.c."]


#: sandhi forms whose base is a noun rather than a classifier in his list, so the
#: tone rule finds nothing; such a form is added as a row of its own, with the base
#: in its note. kaug occurs only after ib 'one' and ob 'two', where sandhi applies,
#: and an unsandhied form would need a numeral above five
NOUN_BASES = {
    ("kaug", "WH"): ("base probably kaus 'tusk' (Green Mong kaug), to be confirmed "
                     "with a speaker (N. White p.c. 2026-10-25); Heimbach (1979, "
                     "App. 1) gives kaus 'fang' and tom ib kaug 'bitten once'"),
}


def sandhi_bases(form: str) -> list[str]:
    """The forms the tone-melody rule could have turned into `form`."""
    head, last = form[:-1], form[-1]
    if last == "g":
        return [head + letter for letter in "jsm"]
    if last == "s":
        return [head]
    if last not in TONE_LETTERS:
        return [form + "v"]
    return []


def definition(gloss: str, white_category: str) -> str:
    """One clause from his gloss.

    `cl:spoon` becomes "a container classifier glossed 'spoon' by White".
    """
    meaning = re.sub(r"^(cl|mw|vcl):", "", gloss).replace(".", " ").replace(",", ", ")
    return f"{CATEGORY_PHRASE[white_category]} glossed '{meaning}' by White"


def merge(ours: list[dict[str, str]], theirs: list[dict[str, str]]
          ) -> tuple[list[dict[str, str]], list[str]]:
    """Fold his rows into ours. Returns the new rows and a log of what changed."""
    index = {(row["FORM"], row["DIALECT"]): row for row in ours}
    expanded = []
    for row in theirs:
        both = ("WH", "GM")
        if row["FORM"].startswith("dl"):
            # dl- is Green Mong spelling only (White Hmong d-), so a common form
            # written dl- cannot be a White Hmong row
            both = ("GM",)
        for dialect in (both if row["DIALECT"] == "CO" else (row["DIALECT"],)):
            expanded.append({**row, "DIALECT": dialect})
    glosses = {(row["FORM"], row["DIALECT"]): row["GLOSS"] for row in expanded}
    log: list[str] = []
    added: list[dict[str, str]] = []
    for row in expanded:
        key = (row["FORM"], row["DIALECT"])
        keys = source_keys(row["CITATION"])
        white_category, klass = CATEGORIES[row["CATEGORY"]]
        existing = index.get(key)
        if existing is not None:
            sources = [s.strip() for s in existing["SOURCE"].split(";") if s.strip()]
            new = [k for k in keys if k not in sources
                   and not (k.startswith("W:") and any(s.startswith("W:") for s in sources))
                   and not (k == "NW:p.c." and "NW:p.c." in sources)]
            if new:
                existing["SOURCE"] = "; ".join(sources + new)
                log.append(f"cite   {key[0]} ({key[1]}): + {'; '.join(new)}")
            if not existing["WHITE_CATEGORY"]:
                existing["WHITE_CATEGORY"] = white_category
                log.append(f"class  {key[0]} ({key[1]}): {white_category}")
            continue
        disposition = ""
        note = row["NOTE"]
        if key in NOUN_BASES:
            note = f"{note}; {NOUN_BASES[key]}"
        elif "sandhi" in note or note.startswith("variant of"):
            named = re.match(r"variant of (\S+)", note)
            candidates = [named.group(1)] if named else sandhi_bases(row["FORM"])
            # the base must be his form for the same meaning: kaug 'bite' is not
            # an alternant of kauj 'spool', though the tone rule allows it
            bases = (candidates if named else
                     [b for b in candidates
                      if glosses.get((b, row["DIALECT"])) == row["GLOSS"]])
            if "standalone" not in note:
                if len(bases) != 1:
                    why = ("not found" if not bases
                           else "ambiguous: " + ", ".join(bases))
                    log.append(f"SKIP   {key[0]} ({key[1]}): sandhi form, base {why}")
                    continue
                disposition = f"variant-of:{bases[0]}"
                note = (f"tone-melody alternant of {bases[0]}"
                        + (f"; {row['NOTE']}" if row["NOTE"] != "sandhi form" else ""))
        new_row = dict.fromkeys(FIELDS, "")
        new_row.update({
            "FORM": row["FORM"], "DIALECT": row["DIALECT"], "CLASS": klass,
            "WHITE_CATEGORY": white_category, "FUNCTION": "classifier",
            "DEFINITION": definition(row["GLOSS"], white_category),
            "SOURCE": "; ".join(keys), "NOTE": note, "DISPOSITION": disposition,
        })
        index[key] = new_row
        added.append(new_row)
        log.append(f"add    {key[0]} ({key[1]}): {klass}"
                   + (f", {disposition}" if disposition else ""))
    return added, log


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--nw", type=Path, default=Path("data/classifiers-nw.tsv"))
    parser.add_argument("--table", type=Path, default=Path("data/classifiers.tsv"))
    parser.add_argument("--check", action="store_true", help="report, write nothing")
    args = parser.parse_args()

    text = args.table.read_text(encoding="utf8")
    header = [line for line in text.splitlines() if line.startswith("#")]
    body = [line for line in text.splitlines() if not line.startswith("#")]
    ours = list(csv.DictReader(body, delimiter="\t", quoting=csv.QUOTE_NONE))
    added, log = merge(ours, read_nw(args.nw))
    print("\n".join(log))
    print(f"\n{len(added)} rows added, "
          f"{sum(1 for line in log if line.startswith(('cite', 'class')))} rows updated, "
          f"{sum(1 for line in log if line.startswith('SKIP'))} skipped", file=sys.stderr)
    if args.check:
        print("--check: nothing written", file=sys.stderr)
        return 0
    lines = [*header, "\t".join(FIELDS)]
    lines += ["\t".join(row[field] or "" for field in FIELDS) for row in ours + added]
    args.table.write_text("\n".join(lines) + "\n", encoding="utf8")
    print(f"wrote {args.table}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
