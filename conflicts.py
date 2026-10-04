#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["wn>=1.1"]
# ///
"""Write the senses where two independent linking routes disagree.

A sense that only one route reaches has nothing to check it against. A sense two
routes reach is different: if they disagree, one of them is wrong, and which one
is a question a speaker can answer in a few seconds given both English
definitions. That makes this the highest-yield page of the review queue, and it is
the only error signal the pipeline has that does not need a speaker to go first.

The sheet has one row per disagreement, both candidate ILIs with their English
lemmas and definitions, and an empty VERDICT column. `ADJUDICATION` and `BY` hold
a provisional reading and who made it, so that a judgement by someone who does not
speak the language is never mistaken for a speaker's.

    uv run conflicts.py --data-directory .wn_data \\
        --concepticon ../cldf2wn/data/concepticon-ili.tsv \\
        --cldf ../wold/cldf:WhiteHmong:WOLD
"""

from __future__ import annotations

import argparse
import csv
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent))
# ruff: noqa: E402 -- the sys.path line above has to run before these
import wn
from wn.morphy import Morphy

import hmong2lmf as m

FIELDS = [
    "VERDICT", "FORM", "DIALECT", "GLOSS",
    "CONCEPTICON_ILI", "CONCEPTICON_LEMMAS", "CONCEPTICON_DEFINITION",
    "TRIANGULATED_ILI", "TRIANGULATED_LEMMAS", "TRIANGULATED_DEFINITION",
    "SUPPORT", "ADJUDICATION", "BY",
]


def describe(english: wn.Wordnet, ili: str) -> tuple[str, str]:
    """English lemmas and first definition for an ILI, for a human to read."""
    found = english.synsets(ili=ili)
    if not found:
        return "", "(no synset in this English WordNet release)"
    synset = found[0]
    lemmas = ", ".join(w.lemma() for w in synset.words())
    return lemmas, (synset.definitions() or [""])[0]


def answers(senses: list[m.OntSense], prefix: str) -> dict[tuple[str, str], str]:
    """The ILI each route chose, keyed by Hmong form and normalised English gloss.

    The gloss has to be part of the key. `cua` is 'wind' in the ontology and 'air'
    in Wiktionary, `hli` is 'month' and 'moon': keying on the form alone compares
    two different senses and manufactures a disagreement.
    """
    found: dict[tuple[str, str], str] = {}
    for sense in senses:
        if sense.ili and sense.method.startswith(prefix):
            for gloss in sense.glosses:
                found.setdefault((sense.form, m.normalise_gloss(gloss).lower()),
                                 str(sense.ili))
    return found


def compare(
    ontology: Path, english: wn.Wordnet, concepticon: Path, pivots: Path,
    dialect: str = "WH", cldf: str | None = None, pin_file: Path | None = None,
) -> tuple[dict[tuple[str, str], tuple[str, str]], dict[tuple[str, str], str]]:
    """Run the Concepticon and triangulation routes separately and line them up.

    Returns every (form, gloss) both routes reached, with the two ILIs, and the
    triangulation support note for each. The two have to run in separate
    configurations because in the pipeline triangulation takes precedence, so no
    one sense ever carries both answers.
    """
    morphy = Morphy(english)
    gloss_map = m.read_concepticon(concepticon)
    id_map = m.read_concepticon_ids(concepticon)

    def run(pivot: bool) -> list[m.OntSense]:
        senses, _, entries = m.read_ontology(ontology, dialect=dialect)
        if cldf:
            directory, language, name = cldf.split(":")[:3]
            extra = m.read_cldf(Path(directory), language, name)
            m.merge_into_entries(entries, extra)
            senses.extend(extra)
        if pivot:
            opened, absent = m.open_pivots(pivots, pin_file)
            if absent:
                raise SystemExit(f"{pivots}: pivot wordnets not loaded: "
                                 f"{' '.join(absent)}")
            extra, _ = m.read_dbnary_pivots(pivots, dialect, opened)
            m.merge_into_entries(entries, extra)
            senses.extend(extra)
        m.link_senses(senses, english, True, True, morphy, gloss_map, id_map)
        m.record_ili_pos(senses, english)
        # deliberately before `dedupe_senses`. Where both routes reach the same
        # ILI, deduplication merges the two senses into one and labels it with the
        # stronger method, so reading the routes afterwards sees the disagreements
        # and almost none of the agreements --- which is how a comparison between
        # them comes out looking far worse than it is
        return senses

    without = run(pivot=False)
    with_pivots = run(pivot=True)
    by_concepticon = answers(without, "concepticon")
    by_triangulation = answers(with_pivots, "triangulated")
    support = {k: (s.note or "").replace("triangulated: ", "")
               for s in with_pivots if s.ili
               for k in answers([s], "triangulated")}
    both = {key: (by_concepticon[key], by_triangulation[key])
            for key in sorted(set(by_concepticon) & set(by_triangulation))}
    return both, support


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ontology", type=Path, default=Path("hmong_ontology.xml"))
    parser.add_argument("--data-directory", type=Path, default=m.DATA_DIR,
                        help=f"wn data directory (default: {m.DATA_DIR})")
    parser.add_argument("--pin-file", type=Path, default=m.PIN_FILE,
                        help="the wordnet releases to use, from load_pivots.py")
    parser.add_argument("--english", default="oewn:2025+")
    parser.add_argument("--concepticon", type=Path, required=True)
    parser.add_argument("--cldf", metavar="DIR:LANGUAGE:NAME")
    parser.add_argument("--pivots", type=Path, default=Path("dbnary-pivots.tsv"))
    parser.add_argument("--dialect", default="WH", choices=["WH", "GM"])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--adjudications", type=Path,
                        help="a TSV of FORM, GLOSS, ADJUDICATION, BY to fold in, so "
                             "that a reading already made is not asked for twice")
    args = parser.parse_args()
    out = args.out or Path(f"review-conflicts-{args.dialect}.tsv")

    wn.config.data_directory = args.data_directory
    english = wn.Wordnet(lexicon=args.english)
    both, support = compare(args.ontology, english, args.concepticon, args.pivots,
                            dialect=args.dialect, cldf=args.cldf,
                            pin_file=args.pin_file)

    prior: dict[tuple[str, str], dict[str, str]] = {}
    if args.adjudications and args.adjudications.exists():
        for row in csv.DictReader(args.adjudications.open(encoding="utf8"),
                                  delimiter="\t"):
            prior[(row["FORM"], row["GLOSS"])] = row

    rows = []
    for key, (concept_ili, tri_ili) in both.items():
        if concept_ili == tri_ili:
            continue
        cl, cd = describe(english, concept_ili)
        tl, td = describe(english, tri_ili)
        said = prior.get(key, {})
        rows.append({
            "VERDICT": "", "FORM": key[0], "DIALECT": args.dialect, "GLOSS": key[1],
            "CONCEPTICON_ILI": concept_ili, "CONCEPTICON_LEMMAS": cl,
            "CONCEPTICON_DEFINITION": cd,
            "TRIANGULATED_ILI": tri_ili, "TRIANGULATED_LEMMAS": tl,
            "TRIANGULATED_DEFINITION": td,
            "SUPPORT": support.get(key, ""),
            "ADJUDICATION": said.get("ADJUDICATION", ""),
            "BY": said.get("BY", ""),
        })

    with out.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t",
                                lineterminator="\n", quoting=csv.QUOTE_NONE,
                                escapechar="\\")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {out}: {len(rows)} conflicts out of {len(both)} senses both "
          f"routes reached ({len(both) - len(rows)} agreed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
