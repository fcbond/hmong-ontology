#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Add numeral classifiers, class nouns and dialect tags to the Hmong ontology.

Every change is idempotent, so the script can be re-run after the TSV files are
edited by hand.

1. **Dialect tags.** No Green Mong form appears as a lemma or a variant in the
   ontology as it stands, so every existing lemma is White Hmong and gets
   `<dialect>WH</dialect>`. This is the first half of the repository's own TODO
   ("Label forms as White Hmong where distinct and add Green Mong forms"); the
   second half arrives with the GM rows of `classifiers.tsv`.

2. **Classifiers**, from `classifiers.tsv`. Classifiers sit outside the noun and
   verb hierarchy: they are non-referential, so Morgado da Costa and Bond (2016)
   give them the part of speech `x` and link them to the concept `classifier` by
   `exemplifies` rather than by hypernymy. The category hierarchy added here
   mirrors that -- one `classifier` node with the five classes of Bond and Paik
   (2000) beneath it. Where the classifier's form is already a lemma, the
   classifier reading is added as a further `<sense>` of that lemma rather than
   as a homograph, which is both better lexicography and a record of the
   grammaticalisation Bisang traces: `taus` is 'axe' and also 'the width of one
   fist', `thoob` is 'bucket' and also 'one bucketful'.

3. **Class nouns**, from `class_nouns.tsv`, added under `--class-nouns`. A class
   noun is referential -- it is part of the noun phrase -- so its members are
   ordinary nouns, and they slot into the ontology's existing convention for
   compounds: an underscored form with a `<headword>`, as in the `yas_taw`
   'ankle' already present. The classifier a compound takes is recorded with
   `classified_by`, the converse of `classifies`.

    uv run add_classifiers.py                  # classifiers only
    uv run add_classifiers.py --class-nouns    # classifiers and class nouns
    uv run add_classifiers.py --check          # report, write nothing
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

CLASSES = {
    "sortal": "classify the kind of the noun phrase they quantify",
    "event": "quantify events",
    "mensural": "measure an amount of some property",
    "group": "refer to a collection of members",
    "taxonomic": "force a generic-kind reading",
}

#: "thoob (bucket)" -> ("thoob", "bucket")
EXAMPLE = re.compile(r"^\s*(.+?)\s*\(([^)]*)\)\s*$")

#: the ontology writes multi-word forms with underscores, e.g. yas_taw 'ankle'
def normalise(form: str) -> str:
    """Ontology spelling of a form the TSV files write with spaces."""
    return form.strip().replace(" ", "_")


def read_tsv(path: Path) -> list[dict[str, str]]:
    """Rows of a TSV, ignoring the leading comment block."""
    with path.open(encoding="utf8") as handle:
        lines = [line for line in handle if not line.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t"))


def parse_examples(field: str) -> list[tuple[str, str]]:
    """Split an EXAMPLES cell into (Hmong noun, English gloss) pairs."""
    pairs = []
    for chunk in field.split(";"):
        match = EXAMPLE.match(chunk)
        if match:
            pairs.append((normalise(match.group(1)), match.group(2).strip()))
    return pairs


def indent(element: ET.Element, level: int = 0) -> None:
    """Pretty-print in the style the existing file uses: tabs, one node per line."""
    pad = "\n" + "\t" * level
    if len(element):
        if not (element.text or "").strip():
            element.text = pad + "\t"
        for child in element:
            indent(child, level + 1)
        if not (element[-1].tail or "").strip():
            element[-1].tail = pad
    if level and not (element.tail or "").strip():
        element.tail = pad


def add_categories(root: ET.Element, extra: list[tuple[str, str, str]]) -> int:
    """Add the classifier node, the five classes beneath it, and any extras."""
    category_set = root.find("category_set")
    present = {c.findtext("term") for c in category_set.findall("category")}
    wanted = [("classifier", "", "non-referential; linked by exemplifies, not hypernymy")]
    wanted += [(f"{name}_classifier", "classifier", why) for name, why in CLASSES.items()]
    wanted += extra
    added = 0
    for term, parent, comment in wanted:
        if term in present:
            continue
        node = ET.SubElement(category_set, "category")
        ET.SubElement(node, "term").text = term
        if parent:
            ET.SubElement(node, "superordinate").text = parent
        if comment:
            ET.SubElement(node, "comment").text = comment
        present.add(term)
        added += 1
    return added


def tag_dialects(root: ET.Element, value: str = "WH") -> int:
    """Give every lemma that lacks one a dialect tag."""
    tagged = 0
    for lemma in root.find("word_set"):
        if lemma.find("dialect") is not None:
            continue
        node = ET.Element("dialect")
        node.text = value
        # keep it next to the form, before the senses
        lemma.insert(1, node)
        tagged += 1
    return tagged


def index_lemmas(root: ET.Element) -> dict[tuple[str, str], ET.Element]:
    """(form, dialect) -> lemma, for deciding between a new sense and a new lemma."""
    index = {}
    for lemma in root.find("word_set"):
        key = (lemma.findtext("form") or "", lemma.findtext("dialect") or "")
        index.setdefault(key, lemma)
    return index


def new_lemma(word_set: ET.Element, form: str, dialect: str,
              headword: str = "") -> ET.Element:
    lemma = ET.SubElement(word_set, "lemma")
    ET.SubElement(lemma, "form").text = form
    ET.SubElement(lemma, "dialect").text = dialect
    if headword:
        ET.SubElement(lemma, "headword").text = headword
    return lemma


#: Note fragments this script derives from a table row. On a re-run they are
#: regenerated and must replace the old ones rather than being appended beside
#: them, or a row whose wording changes leaves both versions in the note.
DERIVED_NOTE_KEYS = ("attestation", "White's category", "Bisang's category")


def split_note(note: str) -> list[str]:
    """A note's `key: value` fragments, keeping values that contain a semicolon.

    `attestation: B:35; W:334, 337` is one fragment, not two. A piece starts a new
    fragment only if it opens with one of the keys this script writes, or carries
    no colon at all and so is free text; anything else continues the piece before
    it. Testing for "something, then a colon" is not enough, because `W:334, 337`
    is a page reference that looks exactly like a key.
    """
    fragments: list[str] = []
    for piece in note.split(";"):
        piece = piece.strip()
        if not piece:
            continue
        starts = (any(piece.startswith(f"{key}:") for key in DERIVED_NOTE_KEYS)
                  or ":" not in piece)
        if fragments and not starts:
            fragments[-1] += f"; {piece}"
        else:
            fragments.append(piece)
    return fragments


def merge_note(existing: str, derived: list[str]) -> str:
    """Replace the derived fragments of a note, keeping anything hand-written.

    Fragments whose key is one this script generates are dropped and the current
    ones put back in order; anything else -- a remark somebody added by hand -- is
    kept as it was.
    """
    kept = [f for f in split_note(existing)
            if not any(f.startswith(f"{key}:") for key in DERIVED_NOTE_KEYS)]
    return "; ".join(dict.fromkeys(derived + kept))


def category_note(row: dict[str, str]) -> list[str]:
    """Each source's own category for this form, White's first.

    White is the base analysis, so his category is the one `CLASS` follows and the
    one a reader should see first; Bisang's comes next where he treats the form,
    and preserves distinctions White collapses -- measures, intrinsic quantifiers,
    collectives and kinds all being one mensural category for White.
    """
    note = []
    if row.get("WHITE_CATEGORY"):
        note.append(f"White's category: {row['WHITE_CATEGORY']}")
    if row.get("BISANG_CATEGORY"):
        note.append(f"Bisang's category: {row['BISANG_CATEGORY']}")
    return note


def find_sense(lemma: ET.Element, category: str) -> ET.Element | None:
    """The lemma's sense in `category`, if it already has one."""
    for sense in lemma.findall("sense"):
        if (sense.findtext("category") or "") == category:
            return sense
    return None


def fill_sense(sense: ET.Element, row: dict[str, str], category: str) -> int:
    """Add to an existing sense whatever this row carries and it does not.

    The script is a merge, so running it again after a row gains a definition, a
    function or an example has to fold that in. Testing only the category and
    skipping the row made a partly enriched sense look finished, which meant a
    corrected table never reached the ontology. Returns the number of children
    added.
    """
    added = 0
    if row["DEFINITION"] and sense.find("meaning") is None:
        node = ET.Element("meaning")
        node.text = row["DEFINITION"]
        sense.insert(0, node)
        added += 1
    if sense.find("category") is None:
        ET.SubElement(sense, "category").text = category
        added += 1
    present = {(f.text or "").strip() for f in sense.findall("function")}
    for function in row["FUNCTION"].split(";"):
        if function.strip() and function.strip() not in present:
            ET.SubElement(sense, "function").text = function.strip()
            added += 1
    pairs = {(c.get("form", ""), c.text or "") for c in sense.findall("classifies")}
    for noun, gloss in parse_examples(row["EXAMPLES"]):
        if (noun, gloss) in pairs:
            continue
        node = ET.SubElement(sense, "classifies")
        node.set("form", noun)
        node.text = gloss
        added += 1
    note = [f"attestation: {row['SOURCE']}"] if row["SOURCE"] else []
    note += category_note(row)
    if note:
        existing = sense.find("note")
        if existing is None:
            ET.SubElement(sense, "note").text = "; ".join(note)
            added += 1
        else:
            wanted = merge_note(existing.text or "", note)
            if wanted != (existing.text or "").strip():
                existing.text = wanted
                added += 1
    return added


def add_variant(lemma: ET.Element, form: str) -> bool:
    """Record `form` as a variant of `lemma`, if it is not already one."""
    if any((v.text or "") == form for v in lemma.findall("variant")):
        return False
    node = ET.Element("variant")
    node.text = form
    # variants sit after the form and the dialect, before the senses
    at = 1 + (1 if lemma.find("dialect") is not None else 0) + len(lemma.findall("variant"))
    lemma.insert(at, node)
    return True


def add_classifiers(
    root: ET.Element, rows: list[dict[str, str]]
) -> tuple[int, int, int, int, int]:
    """Add a classifier sense per row.

    A row's DISPOSITION may divert it. `omit` means the stopword list has the form
    but no source supports it as a classifier, so nothing is added.
    `variant-of:<form>` means White shows it to be a tone-melody alternant of that
    form rather than a classifier of its own, so it becomes a `<variant>` of that
    lemma. Where the sense is already there, `fill_sense` adds whatever the row has
    that it does not. Returns (new lemmas, new senses, enriched, variants, omitted).
    """
    word_set = root.find("word_set")
    index = index_lemmas(root)
    lemmas = senses = enriched = variants = omitted = 0

    # variants are applied after the senses, so the base lemma exists by then
    deferred: list[tuple[str, str, str]] = []

    for row in rows:
        form, dialect = normalise(row["FORM"]), row["DIALECT"]
        disposition = row.get("DISPOSITION", "")
        if disposition == "omit":
            omitted += 1
            continue
        if disposition.startswith("variant-of:"):
            deferred.append((form, dialect, normalise(disposition.split(":", 1)[1])))
            continue
        category = f"{row['CLASS']}_classifier"
        lemma = index.get((form, dialect))
        existing = find_sense(lemma, category) if lemma is not None else None
        if existing is not None:
            if fill_sense(existing, row, category):
                enriched += 1
            continue
        if lemma is None:
            lemma = new_lemma(word_set, form, dialect)
            index[(form, dialect)] = lemma
            lemmas += 1
        sense = ET.SubElement(lemma, "sense")
        if row["DEFINITION"]:
            ET.SubElement(sense, "meaning").text = row["DEFINITION"]
        ET.SubElement(sense, "category").text = category
        for function in row["FUNCTION"].split(";"):
            if function.strip():
                ET.SubElement(sense, "function").text = function.strip()
        for noun, gloss in parse_examples(row["EXAMPLES"]):
            node = ET.SubElement(sense, "classifies")
            node.set("form", noun)
            node.text = gloss
        note = [f"attestation: {row['SOURCE']}"] if row["SOURCE"] else []
        note += category_note(row)
        if note:
            ET.SubElement(sense, "note").text = "; ".join(note)
        senses += 1

    index = index_lemmas(root)
    for form, dialect, base in deferred:
        lemma = index.get((base, dialect))
        if lemma is None:
            print(f"warning: {form!r} is a variant of {base!r}, which is not a lemma "
                  f"for dialect {dialect}; skipped", file=sys.stderr)
            continue
        if add_variant(lemma, form):
            variants += 1
    return lemmas, senses, enriched, variants, omitted


def add_class_nouns(root: ET.Element, rows: list[dict[str, str]]) -> tuple[int, int, int]:
    """Add class-noun members and mark the class nouns. Returns (lemmas, marked, skipped)."""
    word_set = root.find("word_set")
    index = index_lemmas(root)
    lemmas = marked = skipped = 0

    #: the row that describes a class noun itself carries no member
    itself = {normalise(r["CLASS_NOUN"]): r for r in rows
              if r["CLASS_NOUN"] and not r["MEMBER"]}
    for name in sorted({normalise(r["CLASS_NOUN"]) for r in rows if r["CLASS_NOUN"]}):
        lemma = index.get((name, "WH"))
        own = itself.get(name)
        if lemma is None:
            if own is None:
                print(f"warning: no row describes the class noun {name!r}, skipped",
                      file=sys.stderr)
                continue
            lemma = new_lemma(word_set, name, "WH")
            index[(name, "WH")] = lemma
            sense = ET.SubElement(lemma, "sense")
            ET.SubElement(sense, "meaning").text = own["CLASS_NOUN_GLOSS"]
            if own["CATEGORY"]:
                ET.SubElement(sense, "category").text = own["CATEGORY"]
            ET.SubElement(sense, "function").text = "class_noun"
            ET.SubElement(sense, "note").text = f"attestation: {own['SOURCE']}"
            lemmas += 1
            continue
        first = lemma.find("sense")
        if first is None or any((f.text or "") == "class_noun"
                                for f in lemma.iter("function")):
            continue
        # <function> follows <category> in the senses this script writes
        first.append(ET.Element("function"))
        list(first)[-1].text = "class_noun"
        marked += 1

    for row in rows:
        if not row["MEMBER"]:
            continue
        form = normalise(row["MEMBER"])
        lemma = index.get((form, "WH"))
        if lemma is not None:
            skipped += 1
            continue
        lemma = new_lemma(word_set, form, "WH", normalise(row["CLASS_NOUN"]))
        index[(form, "WH")] = lemma
        sense = ET.SubElement(lemma, "sense")
        ET.SubElement(sense, "meaning").text = row["GLOSS"]
        if row["CATEGORY"]:
            ET.SubElement(sense, "category").text = row["CATEGORY"]
        if row["CLASSIFIER"]:
            node = ET.SubElement(sense, "classified_by")
            node.set("form", normalise(row["CLASSIFIER"]))
        ET.SubElement(sense, "note").text = f"attestation: {row['SOURCE']}"
        lemmas += 1
    return lemmas, marked, skipped


def add_underspecified(root: ET.Element, rows: list[dict[str, str]]) -> tuple[int, int]:
    """Add the classifier-plus-underspecified-noun compounds of White's Tables 39-41.

    These are the one case where a classifier does not agree with a noun but decides
    what the phrase denotes, so each row is a distinct sense: `phau ntawv` is a book
    and `tsab ntawv` a letter, from the same noun. Each becomes a compound lemma with
    the noun as its `<headword>` and the classifier as `<classified_by>`.

    Returns (compounds added, already present).
    """
    word_set = root.find("word_set")
    index = index_lemmas(root)
    added = present = 0
    for row in rows:
        form = normalise(row["COMPOUND"])
        if (form, "WH") in index:
            present += 1
            continue
        lemma = new_lemma(word_set, form, "WH", normalise(row["NOUN"]))
        index[(form, "WH")] = lemma
        sense = ET.SubElement(lemma, "sense")
        ET.SubElement(sense, "meaning").text = row["GLOSS"]
        if row["CATEGORY"]:
            ET.SubElement(sense, "category").text = row["CATEGORY"]
        node = ET.SubElement(sense, "classified_by")
        node.set("form", normalise(row["CLASSIFIER"]))
        ET.SubElement(sense, "note").text = (
            f"classifier-specified sense of {row['NOUN']} "
            f"'{row['NOUN_GLOSS']}'; {row['VALUE']}; attestation: W:{row['PAGE']}")
        added += 1
    return added, present


def add_kinship(
    root: ET.Element, rows: list[dict[str, str]], kindiv: dict[tuple[str, str], dict[str, str]]
) -> tuple[int, int, int]:
    """Add the kinship terms of White's Table 29, both dialects.

    Kinship is where this lexicon most needs concepts rather than links: English
    does not lexicalise most of these distinctions, so English WordNet has no lemma
    for them. Where a term maps to a KinDiv concept the mapping is recorded on the
    sense, because a KinDiv kin-type code identifies the concept across languages
    even where the interlingual index does not reach.

    Returns (White Hmong lemmas, Green Mong lemmas, senses on existing lemmas).
    """
    word_set = root.find("word_set")
    index = index_lemmas(root)
    wh = gm = existing = 0
    for row in rows:
        for dialect, form in (("WH", row["WH"]), ("GM", row["GM"])):
            if not form:
                continue
            form = normalise(form)
            lemma = index.get((form, dialect))
            if lemma is None:
                lemma = new_lemma(word_set, form, dialect)
                index[(form, dialect)] = lemma
                if dialect == "WH":
                    wh += 1
                else:
                    gm += 1
            elif any((m.text or "") == row["GLOSS"]
                     for sense in lemma.findall("sense")
                     for m in sense.findall("meaning")):
                continue
            else:
                existing += 1
            sense = ET.SubElement(lemma, "sense")
            ET.SubElement(sense, "meaning").text = row["GLOSS"]
            ET.SubElement(sense, "category").text = (
                "affinal_relation" if row["RELATION"] == "affinal"
                else "consanguineal_relation" if row["RELATION"] == "consanguineal"
                else "family_relation")
            notes = [f"attestation: {row['SOURCE']}"]
            mapped = kindiv.get((row["WH"], row["GLOSS"]))
            if mapped:
                ET.SubElement(sense, "kindiv").set("concept", mapped["KINDIV"])
                notes.append(f"KinDiv {mapped['KINDIV']} "
                             f"({mapped['KINDIV_LABEL']}), {mapped['RELATION']}")
                if mapped["NOTE"]:
                    notes.append(mapped["NOTE"])
            ET.SubElement(sense, "note").text = "; ".join(notes)
    return wh, gm, existing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ontology", type=Path, default=Path("hmong_ontology.xml"))
    parser.add_argument("--classifiers", type=Path, default=Path("classifiers.tsv"))
    parser.add_argument("--class-noun-table", type=Path, default=Path("class_nouns.tsv"))
    parser.add_argument("--class-nouns", action="store_true",
                        help="also add the class nouns of Bisang's Appendix II")
    parser.add_argument("--underspecified", action="store_true",
                        help="also add the classifier-specified compounds of White's "
                             "Tables 39-41")
    parser.add_argument("--underspecified-table", type=Path,
                        default=Path("underspecified.tsv"))
    parser.add_argument("--kinship", action="store_true",
                        help="also add the kinship terms of White's Table 29")
    parser.add_argument("--kinship-table", type=Path, default=Path("kinship.tsv"))
    parser.add_argument("--kindiv-table", type=Path, default=Path("kinship-kindiv.tsv"))
    parser.add_argument("--check", action="store_true", help="report, write nothing")
    args = parser.parse_args()

    tree = ET.parse(args.ontology)
    root = tree.getroot()
    before = len(root.find("word_set"))

    class_noun_rows = read_tsv(args.class_noun_table) if args.class_nouns else []
    extra = [("direction", "", ""), ("time", "", ""),
             ("communication", "", ""), ("plant_part", "plant", "")] if class_noun_rows else []
    categories = add_categories(root, extra)
    dialects = tag_dialects(root)
    lemmas, senses, enriched, variants, omitted = add_classifiers(
        root, read_tsv(args.classifiers))

    print(f"categories added:        {categories}")
    print(f"lemmas tagged WH:        {dialects}")
    print(f"classifier senses added: {senses} "
          f"({lemmas} on new lemmas, {senses - lemmas} on lemmas already present, "
          f"{enriched} already present and enriched from the table)")
    print(f"variants added:          {variants} (tone-melody alternants)")
    print(f"rows omitted:            {omitted} (no source supports them as classifiers)")
    if class_noun_rows:
        cn_lemmas, cn_marked, cn_skipped = add_class_nouns(root, class_noun_rows)
        print(f"class-noun lemmas added: {cn_lemmas} "
              f"({cn_marked} class nouns marked, {cn_skipped} members already present)")
    if args.kinship:
        kindiv = {(r["WH"], r["GLOSS"]): r for r in read_tsv(args.kindiv_table)}
        k_wh, k_gm, k_existing = add_kinship(
            root, read_tsv(args.kinship_table), kindiv)
        print(f"kinship lemmas added:    {k_wh} White Hmong, {k_gm} Green Mong "
              f"({k_existing} senses on lemmas already present)")
        print(f"  of which mapped to a KinDiv concept: "
              f"{len(root.findall('.//kindiv'))}")
    if args.underspecified:
        u_added, u_present = add_underspecified(
            root, read_tsv(args.underspecified_table))
        print(f"underspecified compounds: {u_added} added ({u_present} already present)")
    print(f"lemmas: {before} -> {len(root.find('word_set'))}")

    if args.check:
        print("\n--check: nothing written")
        return 0

    indent(root)
    tree.write(args.ontology, encoding="UTF-8", xml_declaration=True)
    print(f"\nwrote {args.ontology}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
