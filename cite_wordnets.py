#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["wn>=1.1"]
# ///
"""Write the citation, licence and version of every wordnet this work uses.

A wordnet used as a pivot is a source, and its authors should be credited for it.
Each WN-LMF lexicon carries the citation its authors want, so the list is
generated from the loaded lexicons rather than typed: that way it cannot drift
from what was actually queried, and nothing is attributed to anyone on our
recollection of it.

Writes a LaTeX table for the paper's appendix, and the same thing as TSV.

    uv run cite_wordnets.py --latex ../paper-hmong/wordnets.tex
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent))
# ruff: noqa: E402 -- the sys.path line above has to run before these
import wn

import hmong2lmf as m

FIELDS = ["LEXICON", "VERSION", "LANGUAGE", "LABEL", "BIBKEY", "LICENSE", "URL",
          "CITATION"]

#: Two lexicons we use declare no citation of their own. Supplying one by hand is
#: a judgement, so it is here rather than hidden in the output: Open English
#: WordNet's is its release paper, and the Slovak wordnet is credited through the
#: Open Multilingual Wordnet collection that distributes it, which is the most we
#: can say without inventing an attribution.
FALLBACK_CITATIONS = {
    "oewn": "John P. McCrae, Alexandre Rademaker, Francis Bond, Ewa Rudnicka and "
            "Christiane Fellbaum. 2019. English WordNet 2019 - An Open-Source "
            "WordNet for English. In Proceedings of the 10th Global WordNet "
            "Conference, pages 245-252. [no citation declared in the lexicon]",
    "omw-sk": "Distributed in the Open Multilingual Wordnet; the lexicon declares "
              "no citation of its own. [attribution supplied by us]",
}

#: The BibTeX keys the paper cites each wordnet by, in the paper's wordnets.bib.
#: They are the keys of the papers the lexicon's own citation names, taken from
#: the wordnet's citation.bib in omw-data where it has one. Greek's has none and
#: Open English WordNet's is in curated-wordnets; Slovak, which names nothing, is
#: credited through the Open Multilingual Wordnet that distributes it.
BIBKEYS = {
    "omw-arb": "Black:Elkateb:Rodriguez:Alkhalifa:Vossen:Pease:Bertran:Fellbaum:2006,"
               "Abouenour:Bouzoubaa:Rosso:2013",
    "omw-bg": "Simov:Osenova:2010",
    "omw-ca": "Gonzalez-Agirre:Laparra:Rigau:2012",
    "omw-cmn": "Wang:Bond:2013",
    "omw-da": "Pedersen:2009",
    "omw-el": "Stamou:Nenadic:Christodoulakis:2004",
    "oewn": "mccrae-etal-2019-english",
    "omw-es": "Gonzalez-Agirre:Laparra:Rigau:2012",
    "omw-eu": "Pociello:Agirre:Aldezabal:2011",
    "omw-fi": "Linden:Carlson:2010",
    "omw-fr": "Sagot:Fiser:2008",
    "omw-gl": "Gonzalez-Agirre:Laparra:Rigau:2012",
    "omw-he": "Ordan:Wintner:2007",
    "omw-hr": "Oliver:Sojat:Srebacic:2015",
    "omw-id": "Noor:Sapuan:Bond:2011",
    "omw-is": "Sigmundsson:1985",
    "omw-it": "Pianta:Bentivogli:Girardi:2002",
    "omw-ja": "Isahara:Bond:Uchimoto:Utiyama:Kanzaki:2008",
    "omw-lt": "Garabik:Pileckyte:2013",
    "omw-nb": "Fjeld:Nygaard:2009",
    "omw-nl": "Postma:Miltenburg:Segers:Schoen:Vossen:2016",
    "omw-nn": "Fjeld:Nygaard:2009",
    "omw-pl": "Piasecki:Szpakowicz:Broda:2009",
    "omw-ro": "Tufis:Ion:Bozianu:Ceausu:Stefanescu:2008",
    "omw-sk": "bond-etal-2023-documenting",
    "omw-sq": "Ruci:2008",
    "omw-sv": "Borin:Forsberg:Lonngren:2013",
    "omw-th": "Thoongsup:Charoenporn:Robkop:Sinthurahat:Mokarat:"
              "Sornlertlamvanich:Isahara:2009",
    "omw-zsm": "Noor:Sapuan:Bond:2011",
}

#: TeX's reserved characters, so a citation that contains one does not break the
#: build or silently render as something else
TEX_ESCAPES = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


#: Lightweight markup the citations are written in. They are not consistent about
#: it -- some are Markdown, some reStructuredText, some neither, and several are
#: both in one string -- so it is stripped rather than interpreted. Printing
#: somebody's citation as plain text is accurate; guessing which asterisk was
#: meant as emphasis is how a credit gets distorted.
RST_LINK = re.compile(r"`([^`<]*?)\s*<[^>]*>`_+")
#: Also the braces BibTeX uses to protect capitalisation, which several citations
#: were evidently pasted out of a .bib file still carrying
MARKUP = re.compile(r"[*`{}]+")


def tex(text: str) -> str:
    """Escape a string for LaTeX, with its lightweight markup removed."""
    text = RST_LINK.sub(r"\1", text)
    text = MARKUP.sub("", text)
    return "".join(TEX_ESCAPES.get(character, character)
                   for character in " ".join(text.split()))


def rows_for(pinned: dict[str, str]) -> list[dict[str, str]]:
    """One row per pinned lexicon, in language order."""
    rows = []
    for lexicon in wn.lexicons():
        # match the version too, not only the id: two releases of one wordnet can
        # be installed side by side, and only the pinned one was queried
        if pinned and pinned.get(lexicon.id) != lexicon.version:
            continue
        rows.append({
            # a wordnet without an entry in BIBKEYS is left uncited rather than
            # cited by a key no .bib defines
            "BIBKEY": BIBKEYS.get(lexicon.id, ""),
            "LEXICON": lexicon.id,
            "VERSION": lexicon.version,
            "LANGUAGE": lexicon.language,
            "LABEL": lexicon.label or "",
            "LICENSE": lexicon.license or "",
            "URL": lexicon.url or "",
            "CITATION": " ".join(
                (lexicon.citation or FALLBACK_CITATIONS.get(lexicon.id, "")).split()),
        })
    return sorted(rows, key=lambda row: (row["LANGUAGE"], row["LEXICON"]))


def write_latex(path: Path, rows: list[dict[str, str]]) -> None:
    """A longtable of the wordnets, for an appendix.

    An appendix, because this is 26 citations and the paper has eight pages: in
    ACL style the appendices follow the references and do not count against the
    limit, so crediting every source costs the argument no space.
    """
    lines = [
        "% Generated by cite_wordnets.py from the loaded lexicons. Do not edit.",
        r"\begin{longtable}{@{}p{0.26\linewidth}p{0.70\linewidth}@{}}",
        r"\toprule",
        r"Wordnet & Cited as its own metadata asks \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"Wordnet & Cited as its own metadata asks \\",
        r"\midrule",
        r"\endhead",
    ]
    for row in rows:
        name = tex(row["LABEL"] or row["LEXICON"])
        detail = (f"{tex(row['LEXICON'])}:{tex(row['VERSION'])}, "
                  f"{tex(row['LANGUAGE'])}")
        citation = tex(row["CITATION"]) or r"\textit{no citation in the lexicon}"
        cite = f" \\citep{{{row['BIBKEY']}}}" if row["BIBKEY"] else ""
        lines.append(f"{name}{cite} & {citation} \\\\")
        lines.append(f"\\quad\\textit{{{detail}}} & \\\\[2pt]")
    lines += [r"\bottomrule", r"\end{longtable}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-directory", type=Path, default=m.DATA_DIR)
    parser.add_argument("--pin-file", type=Path, default=m.PIN_FILE,
                        help="restrict the list to these lexicons and versions")
    parser.add_argument("--out", type=Path, default=Path("wordnets-cited.tsv"))
    parser.add_argument("--latex", type=Path,
                        help="also write a LaTeX longtable here")
    args = parser.parse_args()

    wn.config.data_directory = args.data_directory
    pinned = m.read_pin_file(args.pin_file)
    rows = rows_for(pinned)
    if not rows:
        raise SystemExit(f"{args.data_directory}: no pinned lexicons are loaded. "
                         f"Run load_pivots.py first.")

    with args.out.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t",
                                lineterminator="\n", quoting=csv.QUOTE_NONE,
                                escapechar="\\")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {args.out}: {len(rows)} wordnets")
    missing = [row["LEXICON"] for row in rows if not row["CITATION"]]
    if missing:
        print(f"  no citation in the lexicon metadata for: {' '.join(missing)}")
    uncited = [row["LEXICON"] for row in rows if not row["BIBKEY"]]
    if uncited:
        print(f"  no BibTeX key in BIBKEYS for: {' '.join(uncited)}")
    if args.latex:
        write_latex(args.latex, rows)
        print(f"wrote {args.latex}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
