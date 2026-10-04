#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["wn>=1.1"]
# ///
"""Compute every figure the paper cites, and write them to facts.json.

One command, one file, so that any number in the paper can be checked against the
data without re-deriving it by hand. Run it after changing anything.

    uv run facts.py --data-directory .wn_data --english oewn:2025+ \\
        --concepticon ../cldf2wn/data/concepticon-ili.tsv \\
        --cldf ../wold/cldf:WhiteHmong:WOLD
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import sys
import warnings
import xml.etree.ElementTree as ET
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent))
# ruff: noqa: E402, I001 -- the sys.path line above has to run before these
import wn
from wn.morphy import Morphy

import conflicts
import hmong2lmf as m


#: First column of each header row in a file that holds several tables one after
#: another, as KinDiv's `extra-concepts.tsv` / `extra-relations.tsv` formats do.
TABLE_HEADERS = ("Subdomain", "Language")


def tables_of(path: Path) -> list[list[dict[str, str]]]:
    """Read a TSV that holds several tables in sequence, each with its own header.

    `kindiv-proposals.tsv` carries the concepts, then the hypernym relations, then
    the words, in KinDiv's own paste-in formats. Reading it as one table gave the
    later tables' rows the first table's column names, so a row of words counted
    as a proposed concept.
    """
    tables: list[list[dict[str, str]]] = []
    header: list[str] = []
    for line in path.read_text(encoding="utf8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        fields = line.split("\t")
        if fields[0] in TABLE_HEADERS:
            header = fields
            tables.append([])
            continue
        if not header:
            raise SystemExit(f"{path}: data before any header row")
        tables[-1].append(dict(zip(header, fields, strict=False)))
    return tables


def rows_of(path: Path) -> list[dict[str, str]]:
    """Read a TSV, ignoring `#` comments and blank lines.

    Blank lines have to go as well as comments: a file whose comment block is
    followed by an empty line would otherwise hand that empty line to DictReader
    as the header, and every column would come back under the key "".
    """
    lines = [line for line in path.open(encoding="utf8")
             if line.strip() and not line.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ontology", type=Path, default=Path("hmong_ontology.xml"))
    parser.add_argument("--pristine", type=Path,
                        help="the ontology before our additions, for growth figures")
    parser.add_argument("--data-directory", type=Path, default=m.DATA_DIR,
                        help=f"wn data directory (default: {m.DATA_DIR})")
    parser.add_argument("--pin-file", type=Path, default=m.PIN_FILE,
                        help="the wordnet releases to use, from load_pivots.py")
    parser.add_argument("--english", default="oewn:2025+",
                        help="must be the lexicon the converter links against, or "
                             "the figures do not describe the released build")
    parser.add_argument("--stopwords", type=Path, metavar="FILE",
                        default=Path("stopwords_classifiers.txt"))
    parser.add_argument("--concepticon", type=Path, required=True)
    parser.add_argument("--cili", type=Path, default=Path("../cygnet/bin/cili.tsv"),
                        help="a CILI release, to tell an invalid ILI from one this "
                             "English release happens not to carry")
    parser.add_argument("--cldf", metavar="DIR:LANGUAGE:NAME")
    parser.add_argument("--dbnary", type=Path, default=Path("dbnary-hmong.tsv"))
    parser.add_argument("--pivots", type=Path, default=Path("dbnary-pivots.tsv"))
    parser.add_argument("--out", type=Path, default=Path("facts.json"))
    args = parser.parse_args()

    wn.config.data_directory = args.data_directory
    english = wn.Wordnet(lexicon=args.english)
    morphy = Morphy(english)
    gloss_map = m.read_concepticon(args.concepticon)
    id_map = m.read_concepticon_ids(args.concepticon)
    facts: dict[str, object] = {}

    # ---- the sources ----------------------------------------------------
    # the tables live beside this script, not beside whatever directory it is run
    # from, so that the figures do not depend on the caller's working directory
    here = Path(__file__).resolve().parent
    classifiers = rows_of(here / "classifiers.tsv")
    class_nouns = rows_of(here / "class_nouns.tsv")
    underspec = rows_of(here / "underspecified.tsv")
    kinship = rows_of(here / "kinship.tsv")
    kindiv = rows_of(here / "kinship-kindiv.tsv")
    kindiv_proposals = tables_of(here / "kindiv-proposals.tsv")
    dbnary = list(csv.DictReader(args.dbnary.open(encoding="utf8"), delimiter="\t"))
    pivots = list(csv.DictReader(args.pivots.open(encoding="utf8"), delimiter="\t"))

    facts["classifiers"] = {
        "rows": len(classifiers),
        "wh": sum(1 for r in classifiers if r["DIALECT"] == "WH"),
        "gm": sum(1 for r in classifiers if r["DIALECT"] == "GM"),
        "bisang_only": sum(1 for r in classifiers
                           if "B:" in r["SOURCE"] and "W:" not in r["SOURCE"]),
        "white_only": sum(1 for r in classifiers
                          if "W:" in r["SOURCE"] and "B:" not in r["SOURCE"]),
        "both": sum(1 for r in classifiers
                    if "W:" in r["SOURCE"] and "B:" in r["SOURCE"]),
        "stopword_only": sum(1 for r in classifiers
                             if "W:" not in r["SOURCE"] and "B:" not in r["SOURCE"]),
        "with_examples": sum(1 for r in classifiers if r["EXAMPLES"]),
        "variants": sum(1 for r in classifiers
                        if r["DISPOSITION"].startswith("variant")),
        "omitted": sum(1 for r in classifiers if r["DISPOSITION"] == "omit"),
        "added": sum(1 for r in classifiers if not r["DISPOSITION"]),
        "by_class": dict(collections.Counter(r["CLASS"] for r in classifiers)),
    }
    facts["class_nouns"] = {
        "heads": len({r["CLASS_NOUN"] for r in class_nouns if r["CLASS_NOUN"]}),
        "members": sum(1 for r in class_nouns if r["MEMBER"]),
    }
    facts["underspecified"] = {"rows": len(underspec),
                               "nouns": len({r["NOUN"] for r in underspec})}
    facts["kinship"] = {
        "senses": len(kinship),
        "with_gm": sum(1 for r in kinship if r["GM"]),
        # ILI_STATUS is the measured outcome of looking each gloss up: `lemma` or
        # `lemma-inflected` found one, `propose` and `propose-hypernym` did not
        "ili_status": dict(collections.Counter(r["ILI_STATUS"] for r in kinship)),
        "no_english_lemma": sum(1 for r in kinship
                                if r["ILI_STATUS"].startswith("propose")),
        "kindiv_mapped": len(kindiv),
        "kindiv_exact": sum(1 for r in kindiv if r["RELATION"] == "exact"),
        "kindiv_proposed": sum(1 for r in kindiv if r["RELATION"] == "proposed"),
    }
    facts["dbnary"] = {
        "sense_anchored": len(dbnary),
        "mww": sum(1 for r in dbnary if r["ISO"] == "mww"),
        "hnj": sum(1 for r in dbnary if r["ISO"] == "hnj"),
    }
    # the same key `read_dbnary_pivots` groups on: a form plus the English sense it
    # translates. Dropping ENGLISH merged groups the linker keeps apart
    by_group = collections.defaultdict(set)
    for r in pivots:
        by_group[(r["FORM"], r["ENGLISH"], r["DEFINITION"])].add(r["PIVOT_ISO"])
    facts["pivots"] = {
        "rows": len(pivots),
        "languages": len({r["PIVOT_ISO"] for r in pivots}),
        "groups": len(by_group),
        "median_languages_per_group": sorted(len(v) for v in by_group.values())[
            len(by_group) // 2] if by_group else 0,
    }

    # ---- the ontology ---------------------------------------------------
    def shape(path: Path) -> dict[str, int]:
        word_set = ET.parse(path).getroot().find("word_set")
        return {
            "lemmas": len(word_set),
            "senses": sum(len(x.findall("sense")) for x in word_set),
            "gm": sum(1 for x in word_set if x.findtext("dialect") == "GM"),
        }
    facts["ontology"] = {"after": shape(args.ontology)}
    if args.pristine and args.pristine.exists():
        facts["ontology"]["before"] = shape(args.pristine)
        before, after = facts["ontology"]["before"], facts["ontology"]["after"]
        facts["ontology"]["lemma_growth_pct"] = round(
            100 * (after["lemmas"] - before["lemmas"]) / before["lemmas"], 1)

    # ---- the methods, one configuration at a time -----------------------
    def run(concepticon=False, cldf=False, pivot=False, dbnary_route=False):
        senses, _, entries = m.read_ontology(args.ontology, "WH")
        tri_keys: set[tuple[str, str, str]] = set()
        if cldf and args.cldf:
            directory, language, name = args.cldf.split(":")[:3]
            extra = m.read_cldf(Path(directory), language, name)
            m.merge_into_entries(entries, extra)
            senses.extend(extra)
        if pivot:
            opened, absent = m.open_pivots(args.pivots, args.pin_file)
            if absent:
                raise SystemExit(
                    f"{args.pivots}: {len(absent)} pivot wordnets are not loaded "
                    f"({' '.join(absent)}). Triangulation counts languages, so the "
                    f"figures would depend on an incomplete installation. Load them "
                    f"with load_pivots.py.")
            extra, review = m.read_dbnary_pivots(args.pivots, "WH", opened)
            tri_keys = {(s.form, s.glosses[0], s.definition) for s in extra}
            m.merge_into_entries(entries, extra)
            senses.extend(extra)
            facts.setdefault("triangulation", {})["undecided"] = len(review)
        if dbnary_route:
            extra = m.read_dbnary(args.dbnary, english, "WH", already=tri_keys)
            m.merge_into_entries(entries, extra)
            senses.extend(extra)
        m.link_senses(senses, english, True, True, morphy,
                      gloss_map if concepticon else None,
                      id_map if concepticon else None)
        m.record_ili_pos(senses, english)
        m.dedupe_senses(entries)
        senses = [s for e in entries for s in e.senses]
        linkable = [s for s in senses if not s.is_classifier]
        linked = [s for s in linkable if s.ili]
        return {
            "linkable": len(linkable),
            "linked": len(linked),
            "pct": round(100 * len(linked) / max(len(linkable), 1), 1),
            "ilis": len({s.ili for s in linked}),
            "methods": dict(collections.Counter(s.method for s in linkable)),
            "senses": senses,
        }

    stages = {
        "english_only": run(),
        "plus_concepticon": run(concepticon=True),
        "plus_wordlist": run(concepticon=True, cldf=True),
        "plus_triangulation": run(concepticon=True, cldf=True, pivot=True),
        "everything": run(concepticon=True, cldf=True, pivot=True, dbnary_route=True),
    }
    full = stages["everything"]["senses"]
    for key, value in stages.items():
        value.pop("senses", None)
        facts.setdefault("coverage", {})[key] = value

    # ---- per-source contribution ---------------------------------------
    ours = {s.ili for s in full if s.ili and not s.source}
    contrib = {}
    for name in sorted({s.source for s in full if s.source}):
        theirs = {s.ili for s in full if s.ili and s.source == name}
        contrib[name] = {"ilis": len(theirs), "new": len(theirs - ours)}
    facts["contribution"] = {"ontology_ilis": len(ours), "by_source": contrib}

    # ---- do Concepticon and triangulation agree? ------------------------
    # Where both reach the same word and concept, a disagreement means one of them
    # is wrong, which is a direct probe of the CLDF-to-wordnet mapping. The
    # comparison lives in conflicts.py, which also writes the review sheet, so the
    # figure here and the sheet a speaker annotates can never drift apart.
    both, _ = conflicts.compare(args.ontology, english, args.concepticon,
                                args.pivots, dialect="WH", cldf=args.cldf,
                                pin_file=args.pin_file)
    agree = {k: v for k, v in both.items() if v[0] == v[1]}
    facts["concepticon_vs_triangulation"] = {
        "both_reached": len(both),
        "agree": len(agree),
        "pct": round(100 * len(agree) / max(len(both), 1), 1),
        "disagreements": [
            {"form": k[0], "gloss": k[1], "concepticon": v[0], "triangulated": v[1]}
            for k, v in both.items() if k not in agree],
    }

    # ---- the source tables, as the paper's inventory counts them ---------
    # the stopword list is one form per line, with `#` section headings
    stopwords = [line.strip() for line
                 in args.stopwords.read_text(encoding="utf8").splitlines()
                 if line.strip() and not line.startswith("#")]
    facts["sources"] = {
        "stopword_forms": len(set(stopwords)),
        "bisang_classifiers": sum(1 for r in classifiers if "B:" in r["SOURCE"]),
        "white_classifiers": sum(1 for r in classifiers if "W:" in r["SOURCE"]),
        # as read from the wordlist, and as many as survive deduplication
        "wold_senses_read": len(m.read_cldf(
            Path(args.cldf.split(":")[0]), args.cldf.split(":")[1],
            args.cldf.split(":")[2])) if args.cldf else 0,
        "wold_forms": sum(1 for s in full if s.source == "WOLD"),
        # the file holds two tables: concepts in KinDiv's extra-concepts.tsv
        # format, then the relations and words that go with them
        "kindiv_proposal_concepts": len(kindiv_proposals[0]),
        "kindiv_proposal_relations": len(kindiv_proposals[1]),
        "kindiv_proposal_words": len(kindiv_proposals[2]),
    }

    # ---- what the additions brought that the ontology did not have -------
    pristine_forms: set[str] = set()
    if args.pristine and args.pristine.exists():
        root = ET.parse(args.pristine).getroot().find("word_set")
        pristine_forms = {m.normalise_form(x.findtext("form") or "") for x in root}
    if pristine_forms:
        members = {m.normalise_form(r["MEMBER"]) for r in class_nouns if r["MEMBER"]}
        facts["class_nouns"]["new"] = len(members - pristine_forms)
        added = {m.normalise_form(r["FORM"]) for r in classifiers
                 if not r["DISPOSITION"]}
        facts["classifiers"]["already_lemmas"] = len(added & pristine_forms)

    # ---- the classifier relations the markup implies ----------------------
    senses_all, _, entries_all = m.read_ontology(args.ontology, "WH")
    synset_of = {id(s): f"s{i}" for i, s in enumerate(senses_all)}
    rels = m.synset_relations(entries_all, synset_of, "concept")
    flat = [(src, rel, tgt) for src, rs in rels.items() for rel, tgt, _ in rs]
    facts["relations"] = {
        "classifier_synsets": sum(1 for s in senses_all if s.is_classifier),
        "exemplifies": sum(1 for _, rel, _ in flat if rel == "exemplifies"),
        "classifies": sum(1 for _, rel, _ in flat if rel == "classifies"),
        "classified_by": sum(1 for _, rel, _ in flat if rel == "classified_by"),
        "total": len(flat),
    }

    # ---- the inherited Concepticon mapping -------------------------------
    cc_rows = list(csv.DictReader(args.concepticon.open(encoding="utf8"),
                                  delimiter="\t"))
    exact = [r for r in cc_rows if r.get("RELATION") == "ss" and r.get("ILI")]
    absent = [r for r in exact if not english.synsets(ili=r["ILI"])]
    facts["concepticon"] = {
        "rows": len(cc_rows),
        "exact": len(exact),
        # a deliberately inexact link names its synset in NEAR_ILI, not ILI
        "inexact": sum(1 for r in cc_rows if r.get("RELATION") in {"ui", "iu"}),
        "unresolved": sum(1 for r in cc_rows if not r.get("RELATION")),
        "exact_absent_from_english": len(absent),
        "exact_absent_pct": round(100 * len(absent) / max(len(exact), 1), 1),
    }

    # Absent from one English release is not the same as invalid. CILI is the
    # authority on which ILIs exist, so each absence is classified: a current CILI
    # concept this English release does not lexicalise, a superseded one, or an
    # identifier CILI does not know. Where English carries the same *definition*
    # under a different ILI, that is recorded too: it is the sharpest form of the
    # problem, the concept still being there under another number.
    cili = m.read_cili(args.cili) if args.cili.exists() else {}
    by_definition: dict[str, str] = {}
    if cili:
        for synset in english.synsets():
            for definition in synset.definitions():
                by_definition.setdefault(definition.strip().lower(), str(synset.ili))
    detail = []
    for row in sorted(absent, key=lambda r: r["ILI"]):
        status, superseded, definition = cili.get(row["ILI"], ("", "", ""))
        detail.append({
            "ili": row["ILI"],
            "gloss": row.get("CONCEPTICON_GLOSS", ""),
            "in_cili": bool(cili) and row["ILI"] in cili,
            "cili_status": status,
            "superseded_by": superseded,
            "cili_definition": definition,
            # the same concept, by its definition, under a different ILI here
            "same_definition_as": by_definition.get(definition.strip().lower(), ""),
        })
    facts["concepticon"]["exact_absent_detail"] = detail
    facts["concepticon"]["exact_absent_but_current_in_cili"] = sum(
        1 for d in detail if d["in_cili"] and d["cili_status"] == "1"
        and not d["superseded_by"])
    facts["concepticon"]["exact_absent_concept_renumbered"] = sum(
        1 for d in detail if d["same_definition_as"])

    # ---- what the supersense filter is worth -----------------------------
    # the same run with and without category filtering: how many senses link only
    # because the ontology's category narrowed the candidates
    # both runs read the ontology fresh and are compared before deduplication,
    # which merges glosses and would make the two sides' keys disagree
    def linked_by_gloss(category_filter: bool) -> dict[tuple[str, str], str | None]:
        senses, _, _ = m.read_ontology(args.ontology, dialect="WH")
        m.link_senses(senses, english, True, category_filter, morphy,
                      gloss_map, id_map)
        return {(x.form, "; ".join(x.glosses)): x.ili
                for x in senses if not x.is_classifier}
    filtered, unfiltered = linked_by_gloss(True), linked_by_gloss(False)
    facts["supersense"] = {
        "senses_rescued": sum(1 for k, ili in filtered.items()
                              if ili and not unfiltered.get(k)),
        "senses_lost": sum(1 for k, ili in filtered.items()
                           if not ili and unfiltered.get(k)),
    }

    # ---- the review queue, stage by stage --------------------------------
    unlinked = [s for s in full if not s.ili and not s.is_classifier]
    ambiguous = [s for s in unlinked if s.method.startswith("ambiguous")]
    one_gloss = [s for s in ambiguous if len(s.glosses) == 1]
    nomatch = [s for s in unlinked if s.method.startswith("nomatch")]
    facts["queue"] = {
        "open": len(unlinked),
        "stage1_ambiguous": len(ambiguous),
        "stage1_single_gloss": len(one_gloss),
        "stage1_binary": sum(1 for s in one_gloss if len(s.candidates) == 2),
        "stage2_triangulation_splits": facts.get("triangulation", {}).get(
            "undecided", 0),
        "stage4_no_english_lemma": len(nomatch),
        "stage4_multiword": sum(1 for s in nomatch
                                if any(" " in g for g in s.glosses)),
    }
    # what a speaker is actually handed: the three annotation sheets
    sheets = {
        "conflicts": here / "review-conflicts-WH.tsv",
        "triangulation_splits": here / "review-triangulation-WH.tsv",
        "wiktionary_declined": here / "review-wiktionary-WH.tsv",
    }
    rows_in_sheets = {name: max(len(path.read_text(encoding="utf8").splitlines()) - 1, 0)
                      for name, path in sheets.items() if path.exists()}
    facts["queue"]["review_sheets"] = rows_in_sheets
    facts["queue"]["review_rows"] = sum(rows_in_sheets.values())

    linked_now = sum(1 for s in full if s.ili and not s.is_classifier)
    linkable_now = sum(1 for s in full if not s.is_classifier)
    facts["queue"]["coverage_after_stage1_pct"] = round(
        100 * (linked_now + facts["queue"]["stage1_binary"]) / max(linkable_now, 1), 1)

    # ---- Green Mong ------------------------------------------------------
    # the GM lexicon is built separately, because WH and GM are separate ISO 639-3
    # languages. WOLD's doculect is White Hmong, so it contributes nothing here
    gm_senses, _, gm_entries = m.read_ontology(args.ontology, dialect="GM")
    opened, _ = m.open_pivots(args.pivots, args.pin_file)
    gm_extra, _ = m.read_dbnary_pivots(args.pivots, "GM", opened)
    m.merge_into_entries(gm_entries, gm_extra)
    gm_senses.extend(gm_extra)
    m.link_senses(gm_senses, english, True, True, morphy, gloss_map, id_map)
    m.record_ili_pos(gm_senses, english)
    m.dedupe_senses(gm_entries)
    gm_all = [x for e in gm_entries for x in e.senses]
    gm_linkable = [x for x in gm_all if not x.is_classifier]
    facts["gm"] = {
        "lemmas": len({e.form for e in gm_entries}),
        "ontology_lemmas": len({e.form for e in gm_entries if not e.sources}),
        "senses": len(gm_all),
        "linkable": len(gm_linkable),
        "linked": sum(1 for x in gm_linkable if x.ili),
        "concepts": len({x.ili for x in gm_linkable if x.ili}),
    }

    # ---- the settings these figures were computed under ------------------
    facts["settings"] = {
        "english": args.english,
        "ontology": str(args.ontology),
        "concepticon": str(args.concepticon),
        "cldf": args.cldf or "",
        "morphy": True,
        "category_filter": True,
        "stative_adjective": True,
        # the exact releases, not only which languages: a wordnet at another
        # release has different words in different synsets and can move a vote
        "pivot_lexicons": sorted(
            f"{name}:{lexicon.lexicons()[0].version}"
            for name, lexicon in m.open_pivots(args.pivots, args.pin_file)[0].items()),
        "pin_file": str(args.pin_file),
    }

    # ---- confidence tiers ------------------------------------------------
    CERTAIN = {"concepticon-id", "concepticon", "intersection", "intersection+category"}
    tiers = collections.Counter()
    for s in full:
        if s.is_classifier:
            tiers["classifier (no ILI by design)"] += 1
        elif s.method.startswith("triangulated"):
            support = int(s.method.rsplit("-", 1)[-1])
            tiers["triangulated, 4+ languages" if support >= 4
                  else "triangulated, 2-3 languages"] += 1
        elif s.method in CERTAIN:
            tiers["concept-set or gloss intersection"] += 1
        elif s.ili:
            tiers["single gloss, monosemous"] += 1
        else:
            tiers["unlinked"] += 1
    facts["tiers"] = dict(tiers)
    facts["tiers"]["linked, stronger evidence"] = (
        tiers["concept-set or gloss intersection"]
        + tiers["triangulated, 4+ languages"] + tiers["triangulated, 2-3 languages"])
    # the triangulation route's own sense count, before deduplication merges any of
    # them into a sense another route also reached
    facts["triangulation"]["senses"] = len(m.read_dbnary_pivots(
        args.pivots, "WH", m.open_pivots(args.pivots, args.pin_file)[0])[0])
    # the category hierarchy as received, not after the categories we added for the
    # extracted material
    if args.pristine and args.pristine.exists():
        facts["sources"]["ontology_categories"] = len(
            m.read_ontology(args.pristine, dialect="WH")[1])
    facts["sources"]["ontology_categories_now"] = len(
        m.read_ontology(args.ontology, dialect="WH")[1])

    args.out.write_text(json.dumps(facts, indent=2, ensure_ascii=False,
                                   sort_keys=True) + "\n", encoding="utf8")
    print(f"wrote {args.out}")
    for key in ("ontology", "coverage", "contribution",
                "concepticon_vs_triangulation", "tiers"):
        print(f"\n{key}:")
        print("  " + json.dumps(facts[key], ensure_ascii=False)[:900])
    return 0


if __name__ == "__main__":
    sys.exit(main())
