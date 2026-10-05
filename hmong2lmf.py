#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["wn>=1.1"]
# ///
"""Convert the Hmong semantic ontology into WN-LMF XML.

Source: https://github.com/nathanmwhite/hmong-ontology (Nathan M. White, LCRC,
James Cook University), with the numeral classifiers and class nouns of Bisang
(1993) added: White Hmong and Green Mong lemmas with senses, English glosses and
a semantic category hierarchy.

Output: WN-LMF 1.4, loadable with the `wn` Python library and by Cygnet, with
senses linked to the Collaborative Interlingual Index where that can be done
safely.

The interesting part is how a sense earns an ILI. Glosses alone are ambiguous
("crab" is seven synsets in English WordNet), so the converter links only when
the evidence is unambiguous:

  intersection   the sense has 2+ English glosses whose candidate synsets
                 intersect in exactly one ILI. This is the sense-intersection
                 heuristic used for the Abui Wordnet.
  monosemous     the sense has one gloss, and that gloss has exactly one
                 synset for its part of speech.

Everything else is left unlinked and reported, because a wrong ILI is worse
than no ILI. Unlinked senses still become synsets, carrying their glosses as a
definition and their ontology category, so nothing is lost -- they are simply
candidates for manual linking or for new ILI proposals.

Classifiers are handled separately, because they are not referential and their
`<meaning>` is a definition rather than a gloss, so looking it up as an English
lemma would be meaningless. Following Morgado da Costa and Bond (2016) they take
the part of speech `x`, carry their definition as a Definition, and are attached
to the concept `classifier` by `exemplifies` rather than by hypernymy. Their
example nouns become `classifies` relations, with the converse `classified_by` on
the noun, at a confidence of 1.0 where the source's English gloss picks out one
sense of the noun and 0.5 where only the Hmong form matches. WN-LMF 1.4 has all
four of these relations as first-class types, so nothing here needs an extension.

Hmong stative verbs gloss as "be bright", "be prosperous" and correspond to
English adjectives, so for `verb.stative` senses the converter also tries the
gloss with "be " stripped against adjective synsets. Cross-part-of-speech
linking of this kind is normal in wordnets for languages with adjectival verbs.
Disable it with --no-stative-adjective to see what it contributes.

White Hmong (mww) and Green Mong (hnj) are separate ISO 639-3 languages, and
WN-LMF sets the language on the Lexicon, so one run produces one dialect. The
default is White Hmong, which is what the ontology is.

Usage:
    uv run hmong2lmf.py --ontology hmong_ontology.xml --output hmn.xml
    uv run hmong2lmf.py --ontology hmong_ontology.xml --output hnj.xml --dialect GM
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import KW_ONLY, dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

import wn
from wn.morphy import Morphy

DOCTYPE = (
    '<!DOCTYPE LexicalResource SYSTEM '
    '"http://globalwordnet.github.io/schemas/WN-LMF-1.4.dtd">'
)
NS = "https://globalwordnet.github.io/schemas/dc/"

# Categories whose members are verbs; everything else in the ontology is a noun,
# except the classifier categories, which are neither.
VERB_PREFIX = "verb."
CLASSIFIER_SUFFIX = "_classifier"

# The linguistic sense of "classifier" in English WordNet: oewn-06319426-n, which
# is 06308436-n in the Princeton WordNet 3.0 numbering Morgado da Costa and Bond
# (2016) cite. The ILI is the part that is stable across versions.
CLASSIFIER_ILI = "i69631"
CLASSIFIER_GLOSS = (
    "a word or morpheme used in some languages in certain contexts "
    "(such as counting) to indicate the semantic class to which the "
    "counted item belongs"
)

# Dialect tags the ontology uses, and the ISO 639-3 code each one is.
DIALECT_LANGUAGES = {"WH": "mww", "GM": "hnj"}

#: The project's own `wn` database and the wordnet releases triangulation is
#: pinned to, both relative to this file rather than to the caller's working
#: directory. `load_pivots.py` writes them; nothing here ever reads or writes the
#: user's `~/.wn_data`, because which releases are installed changes which ILI
#: triangulation picks and that must not depend on the machine.
DATA_DIR = Path(__file__).resolve().parent / ".wn_data"
PIN_FILE = Path(__file__).resolve().parent / "etc" / "pivots.lock"

# The ontology's noun categories are a Hmong-specific semantic classification, but
# they line up closely with Princeton WordNet's lexicographer files. Using them to
# filter candidate synsets is what makes linking possible at all: "crab" is seven
# synsets in English, but only two are noun.animal. Verb categories need no table --
# they already are lexicographer-file names.
# Nine categories are used in the data but never declared in <category_set>, and two
# of those are near-misses for a declared one. Normalising them here keeps a typo from
# silently costing a sense its part of speech: "be.contact" does not start with "verb.",
# so without this it would be treated as a noun.
CATEGORY_ALIASES: dict[str, str] = {
    "be.contact": "verb.contact",
    "verb.cognitive": "verb.cognition",
}

CATEGORY_LEXFILES: dict[str, tuple[str, ...]] = {
    "animal": ("noun.animal",),
    "wild_animal": ("noun.animal",),
    "domestic_animal": ("noun.animal",),
    "person": ("noun.person",),
    "social_role": ("noun.person",),
    "family_relation": ("noun.person",),
    "consanguineal_relation": ("noun.person",),
    "affinal_relation": ("noun.person",),
    "ethnicity": ("noun.person", "noun.group"),
    "plant": ("noun.plant", "noun.food"),
    "plant_part": ("noun.plant", "noun.food"),
    "object": ("noun.artifact", "noun.object", "noun.food"),
    "one_dimensional_object": ("noun.artifact", "noun.object"),
    "one_dimensional_nonrigid_object": ("noun.artifact", "noun.object"),
    "two_dimensional_object": ("noun.artifact", "noun.object"),
    "three_dimensional_object": ("noun.artifact", "noun.object", "noun.food"),
    "three_dimensional_space": ("noun.location", "noun.artifact"),
    "tool": ("noun.artifact",),
    "artifact": ("noun.artifact",),
    "substance": ("noun.substance", "noun.food"),
    "body": ("noun.body",),
    "one_dimensional_body_part": ("noun.body",),
    "one_dimensional_nonrigid_body_part": ("noun.body",),
    "two_dimensional_body_part": ("noun.body",),
    "three_dimensional_body_part": ("noun.body",),
    "paired_body_part": ("noun.body",),
    "illness": ("noun.state",),
    "symbol": ("noun.communication",),
    "communication": ("noun.communication",),
    "cognition": ("noun.cognition",),
    "feeling": ("noun.feeling",),
    "attribute": ("noun.attribute",),
    "shape": ("noun.shape", "noun.attribute"),
    "act": ("noun.act",),
    "event": ("noun.event",),
    "process": ("noun.process", "noun.event"),
    "state": ("noun.state",),
    "possession": ("noun.possession",),
    "place": ("noun.location",),
    "location": ("noun.location",),
    "time": ("noun.time",),
    # used in the data but absent from <category_set>
    "body_part": ("noun.body",),
    "food": ("noun.food",),
    "group": ("noun.group",),
    "paired_object": ("noun.artifact", "noun.object"),
    "phenomenon": ("noun.phenomenon",),
    # added with the class nouns of Bisang (1993) Appendix II
    "direction": ("noun.location", "noun.relation"),
    "abstraction": ("noun.attribute", "noun.state", "noun.cognition"),
}


@dataclass
class OntSense:
    """One sense of one ontology lemma."""

    lemma_index: int
    form: str
    glosses: list[str]
    category: str
    #: everything below is keyword-only: inserting a field must never silently
    #: shift a positional argument into the wrong slot
    _: KW_ONLY
    note: str | None = None
    dialect: str = "WH"
    #: set when the source states a part of speech rather than implying it by category
    pos_override: str = ""
    #: a Concepticon concept set id, where the source is already mapped to one
    concepticon: str = ""
    #: provenance, for dc:source on the entry
    source: str = ""
    #: a KinDiv kin-type code, where the sense is a kinship term mapped to one
    kindiv: str = ""
    #: the source's own definition, where it anchors the sense: Wiktionary numbers
    #: its senses privately, so the definition text is what distinguishes two
    #: translations of one English lemma
    definition: str = ""
    functions: list[str] = field(default_factory=list)
    #: (Hmong noun form, English gloss) pairs from <classifies>
    classifies: list[tuple[str, str]] = field(default_factory=list)
    #: classifier forms from <classified_by>
    classified_by: list[str] = field(default_factory=list)
    # filled in by linking
    ili: str | None = None
    method: str = "unprocessed"
    candidates: set[str] = field(default_factory=set)
    candidate_notes: dict[str, str] = field(default_factory=dict)

    @property
    def pos(self) -> str:
        if self.pos_override:
            return self.pos_override
        if self.category.endswith(CLASSIFIER_SUFFIX):
            return "x"
        return "v" if self.category.startswith(VERB_PREFIX) else "n"

    @property
    def is_classifier(self) -> bool:
        return self.category.endswith(CLASSIFIER_SUFFIX)


@dataclass
class Entry:
    """A (written form, part of speech, dialect) triple: one WN-LMF LexicalEntry."""

    form: str
    pos: str
    _: KW_ONLY
    dialect: str = "WH"
    senses: list[OntSense] = field(default_factory=list)
    variants: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    foreign: bool = False


def text_of(element: ET.Element | None) -> str | None:
    """Return stripped element text, or None."""
    if element is None or element.text is None:
        return None
    stripped = element.text.strip()
    return stripped or None


def normalise_form(form: str) -> str:
    """Ontology forms join syllables with '_'; RPA writes them with spaces."""
    return form.replace("_", " ").strip()


def normalise_gloss(gloss: str) -> str:
    """Glosses mix 'be developed' and 'be_developed'; unify for lookup."""
    gloss = unicodedata.normalize("NFC", gloss)
    gloss = gloss.replace("_", " ")
    return re.sub(r"\s+", " ", gloss).strip()


def read_ontology(
    path: Path, dialect: str = "WH"
) -> tuple[list[OntSense], dict[str, str], list[Entry]]:
    """Parse the ontology into senses, the category hierarchy, and merged entries.

    `dialect` is "WH", "GM" or "all"; anything but "all" keeps only the lemmas
    tagged with it, because WN-LMF sets the language on the Lexicon and the two
    dialects are separate ISO 639-3 languages.
    """
    root = ET.parse(path).getroot()

    hierarchy: dict[str, str] = {}
    category_set = root.find("category_set")
    if category_set is not None:
        for category in category_set.findall("category"):
            term = text_of(category.find("term"))
            if term:
                hierarchy[term] = text_of(category.find("superordinate")) or ""

    word_set = root.find("word_set")
    if word_set is None:
        raise SystemExit(f"{path}: no <word_set> element")

    senses: list[OntSense] = []
    # keyed by dialect as well as form and part of speech: WH and GM are separate
    # ISO 639-3 languages, so a homograph across them is two entries, not one
    entries: dict[tuple[str, str, str], Entry] = {}
    undescribed: set[tuple[str, str]] = set()

    for index, lemma in enumerate(word_set.findall("lemma")):
        raw_form = text_of(lemma.find("form"))
        if not raw_form:
            print(f"warning: lemma {index} has no <form>, skipped", file=sys.stderr)
            continue
        form = normalise_form(raw_form)
        lemma_dialect = text_of(lemma.find("dialect")) or "WH"
        if dialect != "all" and lemma_dialect != dialect:
            continue

        lemma_notes = [t for t in (text_of(n) for n in lemma.findall("note")) if t]
        headword = text_of(lemma.find("headword"))
        if headword:
            lemma_notes.append(f"headword: {normalise_form(headword)}")
        variants = [normalise_form(v)
                    for v in (text_of(x) for x in lemma.findall("variant")) if v]
        sources = [t for t in (text_of(s) for s in lemma.findall("source")) if t]
        # the ontology contains both 'foreign_word' and the typo 'foreign word'
        foreign = any(
            (text_of(s) or "").replace(" ", "_") == "foreign_word"
            for s in lemma.findall("status")
        )

        for sense_element in lemma.findall("sense"):
            category = text_of(sense_element.find("category"))
            if category:
                category = CATEGORY_ALIASES.get(category, category)
            if not category:
                print(f"warning: sense of {form!r} has no category, skipped", file=sys.stderr)
                continue
            glosses = [g for g in (text_of(m) for m in sense_element.findall("meaning")) if g]
            if not glosses and category.endswith(CLASSIFIER_SUFFIX):
                # a handful of classifiers are attested in the ontology's own
                # stopword list but not yet described by any source. Their class is
                # known, so say only that, and record that it is all we know rather
                # than dropping the form.
                glosses = [f"a {category.removesuffix(CLASSIFIER_SUFFIX)} classifier"]
                undescribed.add((form, category))
            if not glosses:
                print(f"warning: sense of {form!r} has no meaning, skipped", file=sys.stderr)
                continue
            sense_note = text_of(sense_element.find("note"))
            functions = [f for f in (text_of(x)
                         for x in sense_element.findall("function")) if f]
            classifies = [
                (normalise_form(x.get("form", "")), (x.text or "").strip())
                for x in sense_element.findall("classifies")
                if x.get("form")
            ]
            classified_by = [
                normalise_form(x.get("form", ""))
                for x in sense_element.findall("classified_by")
                if x.get("form")
            ]
            kindiv_element = sense_element.find("kindiv")
            kindiv = (kindiv_element.get("concept", "")
                      if kindiv_element is not None else "")
            sense = OntSense(index, form, glosses, category, note=sense_note,
                             dialect=lemma_dialect, functions=functions,
                             classifies=classifies, classified_by=classified_by,
                             kindiv=kindiv)
            senses.append(sense)

            key = (form, sense.pos, lemma_dialect)
            entry = entries.get(key)
            if entry is None:
                entry = entries[key] = Entry(form, sense.pos, dialect=lemma_dialect)
            entry.senses.append(sense)
            for variant in variants:
                if variant not in entry.variants:
                    entry.variants.append(variant)
            for source in sources:
                if source not in entry.sources:
                    entry.sources.append(source)
            for note in lemma_notes:
                if note not in entry.notes:
                    entry.notes.append(note)
            entry.foreign = entry.foreign or foreign

    if undescribed:
        print(f"note: {len(undescribed)} classifiers have a class but no definition; "
              "they carry their class as their definition", file=sys.stderr)
    return senses, hierarchy, list(entries.values())


#: DBnary reports the part of speech with lexinfo's names
DBNARY_POS = {"noun": "n", "verb": "v", "adjective": "a", "adverb": "r",
              "properNoun": "n"}

#: words that carry no weight when comparing two definitions
DEFINITION_STOP = frozenset(
    "a an the of to and or in on for with that which is are was be as by from any "
    "such other chiefly countable uncountable especially usually often more most "
    "one someone something etc used also who whom".split())


def definition_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", text.lower())
            if w not in DEFINITION_STOP and len(w) > 2}


def read_dbnary(
    path: Path, english: wn.Wordnet, dialect: str, source: str = "DBnary",
    threshold: float = 0.12, margin: float = 1.5,
    review: list[dict[str, str]] | None = None,
    already: set[tuple[str, str, str]] | None = None,
) -> list[OntSense]:
    """Senses from the sense-anchored Wiktionary translations in `dbnary-hmong.tsv`.

    Each row gives a Hmong form, an English lemma with its part of speech, and the
    Wiktionary definition of the particular English sense the translation was
    attached to. That last part is what makes the row worth having: an English lemma
    alone is ambiguous, but a lemma plus the sense it was filed under is not.

    Wiktionary's sense numbering is its own, so it cannot be mapped to WordNet's
    directly. We compare the two definitions instead, by Jaccard overlap of their
    content words, and accept a synset only when it is both above `threshold` and
    `margin` times better than the runner-up. That is a tuned heuristic and weaker
    evidence than the Concepticon route, which needs no threshold at all; the
    conservative settings mean most rows are declined rather than guessed.

    A declined row is not a dead end: the candidates are there, with their
    definitions, and a speaker could choose between them in seconds. Pass `review`
    to collect them, and `write_review` turns that into an annotation sheet.

    `already` holds the (form, English lemma, Wiktionary definition) triples
    triangulation has decided. Those are skipped, because triangulation is the
    better evidence and the two disagree about a quarter of the time: adding both
    would put a comparison of two glosses beside the agreement of a dozen
    lexicographers and let the format treat them as equals. The definition is part
    of the key because it is what anchors the sense: one Hmong form may translate
    `bank` under both the financial and the river-edge Wiktionary sense, and
    deciding one of those says nothing about the other.
    """
    already = already or set()
    senses: list[OntSense] = []
    with path.open(newline="", encoding="utf8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["DIALECT"] != dialect:
                continue
            pos = DBNARY_POS.get(row["POS"])
            if not pos:
                continue
            if (normalise_form(row["FORM"]), row["ENGLISH"],
                    row["DEFINITION"]) in already:
                continue
            candidates = [c for c in english.synsets(row["ENGLISH"], pos=pos) if c.ili]
            if not candidates:
                continue
            wanted = definition_words(row["DEFINITION"])
            scored = sorted(
                ((len(wanted & definition_words((c.definitions() or [""])[0]))
                  / max(len(wanted | definition_words((c.definitions() or [""])[0])), 1), c)
                 for c in candidates),
                key=lambda pair: -pair[0])
            best = scored[0]
            too_weak = best[0] < threshold
            too_close = len(scored) > 1 and best[0] <= scored[1][0] * margin
            if too_weak or too_close:
                if review is not None:
                    review.append({
                        "VERDICT": "",
                        "FORM": normalise_form(row["FORM"]),
                        "DIALECT": dialect,
                        "ENGLISH": row["ENGLISH"],
                        "POS": pos,
                        "WHY": "no candidate close enough" if too_weak
                               else "two candidates too close",
                        "WIKTIONARY_SENSE": row["DEFINITION"],
                        "CANDIDATES": " | ".join(
                            f"{c.ili}={(c.definitions() or [''])[0][:70]} [{score:.2f}]"
                            for score, c in scored[:5]),
                    })
                continue
            sense = OntSense(
                lemma_index=-1,
                form=normalise_form(row["FORM"]),
                glosses=[row["ENGLISH"]],
                category="",
                note=f"{source}: translation of {row['ENGLISH']} "
                     f"'{row['DEFINITION'][:60]}'",
                dialect=dialect,
                pos_override=pos,
                source=source,
                definition=row["DEFINITION"],
            )
            # the ILI is decided here, not by the gloss routes
            sense.ili, sense.method = str(best[1].ili), "dbnary-sense"
            senses.append(sense)
    return senses


def write_review(path: Path, rows: list[dict[str, str]]) -> None:
    """Write the declined Wiktionary candidates as an annotation sheet.

    One row per translation the definition comparison would not decide, with every
    candidate ILI and its English definition on the same line and an empty VERDICT
    column. Choosing between two or three glossed candidates is a few seconds' work
    for someone who knows the language, and it is work no heuristic should be doing
    on their behalf.
    """
    fields = list(rows[0]) if rows else [
        "VERDICT", "FORM", "DIALECT", "ENGLISH", "WHY", "WIKTIONARY_SENSE",
        "PIVOTS", "CANDIDATES"]
    # an empty queue still writes the file: leaving an earlier run's sheet in place
    # would make a stale annotation task look like the current one
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t",
                                lineterminator="\n", quoting=csv.QUOTE_NONE,
                                escapechar="\\")
        writer.writeheader()
        writer.writerows(rows)


def read_dbnary_pivots(
    path: Path, dialect: str, pivots: dict[str, wn.Wordnet],
    source: str = "triangulated", min_support: int = 2,
) -> tuple[list[OntSense], list[dict[str, str]]]:
    r"""Link Hmong senses by intersecting other languages' translations of the same
    English sense.

    This is the method of \citet{bond-etal-2008-japanese} and
    \citet{bond-foster-2013-omw}, applied to Wiktionary rather than to bilingual
    dictionaries. DBnary tells us which English *sense* a Hmong word translates;
    that sense is usually translated into a dozen other languages as well; each of
    those words has ILIs in its own wordnet; and the ILI that several of them agree
    on is the concept.

    What makes this better evidence than comparing two definitions is that it is not
    a proxy. A French lexicographer put `air` in a synset and a Finnish one put
    `ilma` in one, independently of each other and of Wiktionary. Agreement between
    them is evidence about the concept; overlap between two glosses is evidence
    about wording.

    `min_support` counts the languages backing the *winning* ILI, not the languages
    that produced any candidate at all. That distinction matters: counting the
    latter is a mistake we made in earlier work on this method, and fixing it moved
    precision from 85.4% to 90.7%.

    Returns the senses it could link, and a review row for every group it could not.
    """
    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    with path.open(newline="", encoding="utf8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["DIALECT"] != dialect:
                continue
            groups[(row["FORM"], row["ENGLISH"], row["DEFINITION"])].append(row)

    senses: list[OntSense] = []
    review: list[dict[str, str]] = []
    for (form, english, definition), rows in sorted(groups.items()):
        # languages backing each ILI, one vote per language however many of its
        # words point there
        backers: dict[str, set[str]] = defaultdict(set)
        words: dict[str, set[str]] = defaultdict(set)
        for row in rows:
            lexicon = pivots.get(row["PIVOT_LEXICON"])
            if lexicon is None:
                continue
            words[row["PIVOT_ISO"]].add(row["PIVOT_WORD"])
            for synset in lexicon.synsets(row["PIVOT_WORD"]):
                if synset.ili:
                    backers[str(synset.ili)].add(row["PIVOT_ISO"])
        if not backers:
            # no pivot word reached a synset with an ILI. That is an undecided
            # group like any other, and dropping it would understate the queue and
            # hide the difference between "no evidence" and "never looked at"
            review.append({
                "VERDICT": "",
                "FORM": normalise_form(form),
                "DIALECT": dialect,
                "ENGLISH": english,
                "WHY": "no pivot word has an ILI in a loaded wordnet",
                "WIKTIONARY_SENSE": definition,
                "PIVOTS": "; ".join(f"{iso}={'/'.join(sorted(w))}"
                                    for iso, w in sorted(words.items()))[:300],
                "CANDIDATES": "",
            })
            continue
        ranked = sorted(backers.items(), key=lambda kv: (-len(kv[1]), kv[0]))
        best, support = ranked[0]
        runner_up = len(ranked[1][1]) if len(ranked) > 1 else 0
        decided = len(support) >= min_support and len(support) > runner_up
        if decided:
            senses.append(OntSense(
                lemma_index=-1,
                form=normalise_form(form),
                glosses=[english],
                category="",
                note=f"{source}: {len(support)} of {len(words)} pivot languages agree "
                     f"({', '.join(sorted(support))})",
                dialect=dialect,
                pos_override="",
                source=source,
                definition=definition,
            ))
            senses[-1].ili = best
            senses[-1].method = f"triangulated-{len(support)}"
            senses[-1].pos_override = pos_of_ili(best, pivots) or "n"
        else:
            review.append({
                "VERDICT": "",
                "FORM": normalise_form(form),
                "DIALECT": dialect,
                "ENGLISH": english,
                "WHY": "no ILI reached two languages" if len(support) < min_support
                       else "two ILIs equally supported",
                "WIKTIONARY_SENSE": definition,
                "PIVOTS": "; ".join(f"{iso}={'/'.join(sorted(w))}"
                                    for iso, w in sorted(words.items()))[:300],
                "CANDIDATES": " | ".join(
                    f"{ili}({len(langs)}: {','.join(sorted(langs))})"
                    for ili, langs in ranked[:5]),
            })
    return senses, review


def read_pin_file(path: Path) -> dict[str, str]:
    """Lexicon id -> version, from the pin file `load_pivots.py` writes."""
    pinned: dict[str, str] = {}
    if not path.exists():
        return pinned
    for line in path.read_text(encoding="utf8").splitlines():
        if line.strip() and not line.startswith("#"):
            lexicon, _, version = line.partition("\t")
            pinned[lexicon.strip()] = version.strip()
    return pinned


def open_pivots(
    path: Path, pin_file: Path | None = None
) -> tuple[dict[str, wn.Wordnet], list[str]]:
    """Open a Wordnet for each pivot lexicon the file mentions.

    Returns what it opened and what it could not. A missing pivot does not merely
    reduce coverage: triangulation counts languages, so losing one can turn a 2-2
    tie into an accepted 2-1 or drop a winner below the two-language threshold. The
    caller must therefore decide what to do about an incomplete installation rather
    than have one quietly change the links, which is why the list comes back
    instead of only a warning.

    For the same reason the *version* matters, not only the presence: a wordnet at
    a different release has different words in different synsets and can move a
    vote. `pin_file` is the file `load_pivots.py` writes from Cygnet's
    `wordnets.toml`, and where it names a version, only that version is opened; a
    lexicon installed at any other release is reported as missing rather than used.
    """
    pinned = read_pin_file(pin_file) if pin_file else {}
    wanted = set()
    with path.open(newline="", encoding="utf8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row.get("PIVOT_LEXICON", "").startswith("omw-"):
                wanted.add(row["PIVOT_LEXICON"])
    available = {lexicon.id: lexicon for lexicon in wn.lexicons()}
    opened: dict[str, wn.Wordnet] = {}
    mismatched: list[str] = []
    for name in sorted(wanted):
        lexicon = available.get(name)
        if lexicon is None:
            continue
        if name in pinned and lexicon.version != pinned[name]:
            mismatched.append(f"{name} is {lexicon.version}, pinned {pinned[name]}")
            continue
        opened[name] = wn.Wordnet(lexicon=f"{lexicon.id}:{lexicon.version}")
    missing = sorted(wanted - set(opened))
    if mismatched:
        missing = sorted(set(missing) | {m.split()[0] for m in mismatched})
        print("warning: " + "; ".join(mismatched), file=sys.stderr)
    return opened, missing


def pos_of_ili(ili: str, pivots: dict[str, wn.Wordnet]) -> str:
    """The part of speech a pivot wordnet records for an ILI."""
    for lexicon in pivots.values():
        found = lexicon.synsets(ili=ili)
        if found:
            return found[0].pos or ""
    return ""


def merge_into_entries(entries: list[Entry], senses: list[OntSense]) -> int:
    """Fold extra senses into the entry list, sharing an entry where form, part of
    speech and dialect already match. Returns the number of new entries created.

    The dialect is part of the key because White Hmong and Green Mong are separate
    ISO 639-3 languages: `mww` and `hnj`. A shared entry would take whichever
    dialect was seen first and put a Green Mong sense in a White Hmong entry, which
    the `--dialect all` build would then make visible.
    """
    index = {(entry.form, entry.pos, entry.dialect): entry for entry in entries}
    created = 0
    for sense in senses:
        key = (sense.form, sense.pos, sense.dialect)
        entry = index.get(key)
        if entry is None:
            entry = Entry(sense.form, sense.pos, dialect=sense.dialect)
            index[key] = entry
            entries.append(entry)
            created += 1
        entry.senses.append(sense)
        if sense.source and sense.source not in entry.sources:
            entry.sources.append(sense.source)
    return created


#: Linking methods in order of the strength of their evidence, strongest first.
#: Only the prefix is compared, so `triangulated-7` and `intersection+category`
#: are ranked by their route.
METHOD_STRENGTH = (
    "concepticon-id",     # a hand-mapped concept set identifier
    "triangulated",       # several other languages' lexicographers agreeing
    "concepticon",        # a gloss that is also a Concepticon gloss
    "intersection",       # two English glosses meeting in one synset
    "dbnary-sense",       # a Wiktionary definition matched against a gloss
    "monosemous",         # one English gloss with one sense
)


def method_rank(method: str) -> int:
    """Where a linking method sits in `METHOD_STRENGTH`; unknown methods last."""
    for rank, prefix in enumerate(METHOD_STRENGTH):
        if method.startswith(prefix):
            return rank
    return len(METHOD_STRENGTH)


def absorb(keeper: OntSense, loser: OntSense, note: str | None = None) -> None:
    """Fold a duplicate sense into the one being kept.

    Everything the loser carries that the keeper does not has to move across, or
    deduplication silently drops it: a KinDiv identifier, a classifier relation, a
    Concepticon concept set, the part of speech a second source inferred. The
    keeper also takes the *stronger* of the two linking methods and the source that
    goes with it, because the surviving sense is what the reports and the paper's
    figures count, and attributing a triangulated link to the weaker route that
    happened to come first in the file would misreport the evidence.
    """
    for gloss in loser.glosses:
        if gloss not in keeper.glosses:
            keeper.glosses.append(gloss)
    for function in loser.functions:
        if function not in keeper.functions:
            keeper.functions.append(function)
    for pair in loser.classifies:
        if pair not in keeper.classifies:
            keeper.classifies.append(pair)
    for form in loser.classified_by:
        if form not in keeper.classified_by:
            keeper.classified_by.append(form)
    keeper.kindiv = keeper.kindiv or loser.kindiv
    keeper.concepticon = keeper.concepticon or loser.concepticon
    keeper.definition = keeper.definition or loser.definition
    keeper.candidates |= loser.candidates
    for ili, why in loser.candidate_notes.items():
        keeper.candidate_notes.setdefault(ili, why)

    # the source whose evidence is not the one being recorded is still worth
    # naming in the note: two sources agreeing on a sense is itself information
    other = loser.source
    if method_rank(loser.method) < method_rank(keeper.method):
        other = keeper.source
        keeper.method = loser.method
        keeper.source = loser.source or keeper.source
    notes = [n for n in (keeper.note, loser.note, note) if n]
    if other and other != keeper.source:
        notes.append(f"also in {other}")
    keeper.note = "; ".join(dict.fromkeys(notes)) or None


def dedupe_senses(entries: list[Entry], ili_pos: dict[str, str] | None = None) -> int:
    """Collapse senses of one entry that resolved to the same ILI.

    Two sources describing the same word and the same concept are describing one
    sense, not two. Without this the merged lexicon lists the same lemma twice in a
    synset, which is malformed as lexicography even though the DTD permits it.
    `absorb` folds the loser's glosses, notes, relations and identifiers into the
    survivor and keeps whichever linking method is the stronger evidence, so
    nothing is lost but the duplication. Returns the number of senses removed.

    A second pass handles the same collision across two entries. Hmong stative verbs
    correspond to English adjectives, so the ontology may class a word as
    `verb.stative` where a wordlist classes it as an adjective; both then reach the
    same ILI, and the merged synset would list the written form twice. One ILI is one
    concept and so should be one synset, which rules out splitting by part of speech;
    instead the sense whose part of speech matches the ILI's is the one kept.
    """
    ili_pos = ILI_POS if ili_pos is None else ili_pos
    removed = 0
    for entry in entries:
        seen: dict[str, OntSense] = {}
        keep: list[OntSense] = []
        for sense in entry.senses:
            if not sense.ili:
                keep.append(sense)
                continue
            first = seen.get(sense.ili)
            if first is None:
                seen[sense.ili] = sense
                keep.append(sense)
                continue
            absorb(first, sense)
            removed += 1
        entry.senses = keep

    # second pass: the same written form reaching one ILI through two entries
    by_form_ili: dict[tuple[str, str], list[tuple[Entry, OntSense]]] = defaultdict(list)
    for entry in entries:
        for sense in entry.senses:
            if sense.ili:
                by_form_ili[(entry.form, sense.ili)].append((entry, sense))
    for (_, ili), found in by_form_ili.items():
        if len(found) < 2:
            continue
        # prefer the reading whose part of speech the ILI itself is recorded under
        found.sort(key=lambda pair: pair[1].pos != (ili_pos.get(ili) or pair[1].pos))
        keeper = found[0][1]
        for entry, sense in found[1:]:
            absorb(keeper, sense,
                   f"also analysed as {sense.pos}"
                   + (f" by {sense.source}" if sense.source else ""))
            entry.senses.remove(sense)
            removed += 1
    return removed


def lexfiles_for(category: str) -> tuple[str, ...]:
    """Lexicographer files an ontology category is allowed to match."""
    if category.startswith(VERB_PREFIX):
        return (category,)
    return CATEGORY_LEXFILES.get(category, ())


def candidates_for(
    english: wn.Wordnet,
    gloss: str,
    parts: tuple[str, ...],
    allowed: tuple[str, ...],
    seen: dict[str, str],
) -> tuple[set[str], bool, bool]:
    """Candidate ILIs for a gloss.

    Records each candidate's English definition in `seen` so the report can show a
    human what the choices actually are.

    Returns the candidate set, whether the ontology category narrowed it, and
    whether English synsets were found that carry no ILI (and so cannot be linked
    even though the gloss matched). When filtering by lexicographer file would
    discard every candidate the unfiltered set is kept instead, so a category that
    simply disagrees with English WordNet's classification costs recall rather than
    silently producing nothing.
    """
    scored: list[tuple[str, str | None]] = []
    ili_less = False
    for part in parts:
        for synset in english.synsets(gloss, pos=part):
            if not synset.ili:
                ili_less = True
                continue
            scored.append((str(synset.ili), synset.lexfile()))
            definitions = synset.definitions()
            if definitions:
                seen[str(synset.ili)] = definitions[0]
    everything = {ili for ili, _ in scored}
    if not allowed:
        return everything, False, ili_less
    narrowed = {ili for ili, lexfile in scored if lexfile in allowed}
    if narrowed and narrowed != everything:
        return narrowed, True, ili_less
    return (narrowed or everything), False, ili_less


def read_concepticon(path: Path) -> dict[str, tuple[str, str]]:
    """Concepticon gloss -> (ILI, part of speech), exact links only.

    The mapping is the one built for the CLDF-to-WN-LMF converter out of Borin's
    Concepticon conceptlist. Only rows the conceptlist marks `ss`, a genuine
    synonym link, are used: its `ui` and `iu` rows are deliberately inexact and
    would put a sense in the wrong synset.
    """
    mapping: dict[str, tuple[str, str]] = {}
    with path.open(newline="", encoding="utf8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row.get("RELATION") != "ss" or not row.get("ILI"):
                continue
            mapping[normalise_gloss(row["GLOSS"]).lower()] = (row["ILI"], row["POS"] or "")
    return mapping


def read_cili(path: Path) -> dict[str, tuple[str, str, str]]:
    """ILI -> (status, superseded_by, definition), from a CILI release.

    English WordNet is not the authority on which ILIs exist; CILI is. An ILI that
    no English synset carries may still be a current concept that some other
    language lexicalises, and treating it as invalid because one English release
    dropped it is exactly the English-centric reading a shared index exists to
    avoid.
    """
    mapping: dict[str, tuple[str, str, str]] = {}
    with path.open(newline="", encoding="utf8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            mapping[row["ili_id"]] = (row.get("status", ""),
                                      row.get("superseded_by", ""),
                                      row.get("definition", ""))
    return mapping


def read_concepticon_ids(path: Path) -> dict[str, tuple[str, str]]:
    """Concepticon concept set id -> (ILI, part of speech), exact links only."""
    mapping: dict[str, tuple[str, str]] = {}
    with path.open(newline="", encoding="utf8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row.get("RELATION") != "ss" or not row.get("ILI"):
                continue
            mapping[row["CONCEPTICON_ID"]] = (row["ILI"], row["POS"] or "")
            if row["POS"]:
                ILI_POS[row["ILI"]] = row["POS"]
    return mapping


#: ILI -> part of speech. Pre-filled from the Concepticon mapping when one is
#: given, then completed from English WordNet by `record_ili_pos`, which is the
#: authority: the Concepticon file covers only the concepts it maps, so relying on
#: it alone left the tie-break below undecided for most ILIs.
#: Used only to break a tie when two entries reach the same ILI.
ILI_POS: dict[str, str] = {}


def record_ili_pos(senses: list[OntSense], english: wn.Wordnet) -> int:
    """Record the part of speech English WordNet gives each linked ILI.

    `dedupe_senses` keeps the reading whose part of speech matches the ILI's own,
    so it needs that part of speech for every ILI two entries might share --- not
    only for the ones a Concepticon mapping happens to cover. Returns how many
    were added.
    """
    added = 0
    for sense in senses:
        if not sense.ili or sense.ili in ILI_POS:
            continue
        found = english.synsets(ili=sense.ili)
        if found and found[0].pos:
            ILI_POS[sense.ili] = found[0].pos
            added += 1
    return added

#: Semantic categories as CLDF wordlists write them, mapped onto WN-LMF parts of
#: speech. Function words get `x`, "other", which is where WN-LMF puts anything
#: outside the four open classes; they are still linkable, unlike the classifiers,
#: which carry no ILI by design.
CLDF_POS = {"Noun": "n", "Verb": "v", "Adjective": "a", "Adverb": "r",
            "Function word": "x", "Person/Thing": "n", "Action/Process": "v",
            "Property": "a", "Other": "x", "Number": "n", "Classifier": "x"}


def read_cldf(directory: Path, language: str, source: str = "CLDF") -> list[OntSense]:
    """Senses from a CLDF wordlist, for one of its languages.

    This works for any Lexibank-style dataset with `forms.csv` and
    `parameters.csv`, which is what makes it worth having here rather than a
    WOLD-specific reader: the same code takes `wold`, `chenhmongmien` or
    `starostinhmongmien`.

    The reason these senses can be folded in at all is that every CLDF parameter
    carries a Concepticon id, so they reach the interlingual index through the
    concept set directly rather than through a gloss -- no monosemy or intersection
    heuristic, and no risk of the homograph conflation that defeats a merge of
    unaligned gloss lists.

    Where a dataset records more than a form and a meaning, that is kept as a note.
    WOLD's borrowing judgement is the case in point: it is the thing WOLD knows
    that no other source here does.
    """
    parameters = {
        row["ID"]: row
        for row in csv.DictReader((directory / "parameters.csv").open(encoding="utf8"))
    }
    senses: list[OntSense] = []
    with (directory / "forms.csv").open(encoding="utf8") as handle:
        for row in csv.DictReader(handle):
            if row["Language_ID"] != language or not row["Form"]:
                continue
            parameter = parameters.get(row["Parameter_ID"])
            if parameter is None:
                continue
            # meanings are named as phrases: "the world", "to eat"
            gloss = re.sub(r"^(the|a|an|to) ", "", parameter["Name"].strip())
            notes = []
            if row.get("Borrowed") and not row["Borrowed"].startswith("5."):
                notes.append(f"{source} borrowing: {row['Borrowed']}")
            if row.get("Analyzability") and row["Analyzability"] != "unanalyzable":
                notes.append(row["Analyzability"])
            senses.append(
                OntSense(
                    lemma_index=-1,
                    form=normalise_form(row["Form"]),
                    glosses=[gloss],
                    category=parameter.get("Semantic_field", ""),
                    note="; ".join(notes) or None,
                    dialect="WH",
                    pos_override=CLDF_POS.get(
                        parameter.get("Semantic_category")
                        or parameter.get("Ontological_Category", ""), "u"),
                    concepticon=parameter.get("Concepticon_ID", ""),
                    source=source,
                )
            )
    return senses


def link_senses(
    senses: list[OntSense],
    english: wn.Wordnet,
    stative_adjective: bool,
    use_lexfile: bool,
    morphy: object | None = None,
    concepticon: dict[str, tuple[str, str]] | None = None,
    concepticon_by_id: dict[str, tuple[str, str]] | None = None,
) -> None:
    """Assign an ILI to each sense where the evidence is unambiguous.

    Routes run strongest first. A source that already carries a Concepticon
    concept set id reaches the ILI through that, before any gloss is looked up:
    the id was mapped by hand and names the meaning directly, whereas the gloss
    beside it is one English wording of it and may resolve elsewhere.
    """
    for sense in senses:
        if sense.is_classifier or sense.ili or not sense.concepticon:
            continue
        found = (concepticon_by_id or {}).get(sense.concepticon)
        if found and found[1] == sense.pos:
            sense.ili, sense.method = found[0], "concepticon-id"

    for sense in senses:
        if sense.is_classifier:
            # a classifier's <meaning> is a definition, not a gloss, and no
            # individual classifier has an ILI of its own
            sense.method = "classifier"
            continue
        if sense.ili:
            # a sense that already carries an ILI was linked by a route that does
            # not go through glosses at all -- triangulation, or a sense-anchored
            # translation. Gloss lookup must not overwrite it: its evidence is
            # better, and silently replacing it would hide that fact.
            continue
        parts: tuple[str, ...] = (sense.pos,)
        allowed = lexfiles_for(sense.category) if use_lexfile else ()
        gloss_sets: list[set[str]] = []
        narrowed_any = False
        ili_less_any = False
        seen: dict[str, str] = {}

        for gloss in sense.glosses:
            lookup = normalise_gloss(gloss)
            found, narrowed, ili_less = candidates_for(english, lookup, parts, allowed, seen)
            narrowed_any = narrowed_any or narrowed
            ili_less_any = ili_less_any or ili_less
            if not found and morphy is not None:
                # "tweezers" is not an OEWN lemma but "tweezer" is
                for part, forms in morphy(lookup, pos=sense.pos).items():
                    for form in forms:
                        if form == lookup:
                            continue
                        more, narrowed, ili_less = candidates_for(
                            english, form, (part,), allowed, seen
                        )
                        narrowed_any = narrowed_any or narrowed
                        ili_less_any = ili_less_any or ili_less
                        found = found | more
            if stative_adjective and sense.category == "verb.stative":
                bare = re.sub(r"^be\s+", "", lookup)
                if bare != lookup:
                    # adjective lexicographer files are unrelated to verb categories,
                    # so this fallback is never filtered
                    extra, _, _ = candidates_for(english, bare, ("a", "s"), (), seen)
                    found = found | extra
            if found:
                gloss_sets.append(found)

        suffix = "+category" if narrowed_any else ""
        sense.candidate_notes = seen

        if not gloss_sets:
            sense.method = "no-ili" if ili_less_any else "nomatch"
            continue

        if len(gloss_sets) >= 2:
            intersection = set.intersection(*gloss_sets)
            if len(intersection) == 1:
                sense.ili = next(iter(intersection))
                sense.method = "intersection" + suffix
                continue
            if not intersection:
                sense.method = "no-intersection" + suffix
                sense.candidates = set.union(*gloss_sets)
                continue
            sense.method = "ambiguous" + suffix
            sense.candidates = intersection
            continue

        only = gloss_sets[0]
        if len(only) == 1:
            sense.ili = next(iter(only))
            sense.method = "monosemous" + suffix
        else:
            sense.method = "ambiguous" + suffix
            sense.candidates = only

    if concepticon or concepticon_by_id:
        link_by_concepticon(senses, concepticon or {}, concepticon_by_id)


def link_by_concepticon(
    senses: list[OntSense],
    concepticon: dict[str, tuple[str, str]],
    by_id: dict[str, tuple[str, str]] | None = None,
) -> None:
    """Second pass: link what English glosses could not, through Concepticon.

    A Concepticon concept set is a cross-linguistically comparable meaning that
    has already been mapped to a wordnet synset by hand, so a gloss that is also
    a Concepticon gloss resolves without the ambiguity a bare English lemma has:
    WATER is one concept, whereas "water" is eleven English synsets.

    `by_id` maps the concept set id itself, for sources such as WOLD that already
    carry one. That route is exact: it skips the gloss entirely.
    """
    by_id = by_id or {}
    for sense in senses:
        if sense.ili or sense.is_classifier:
            continue
        if sense.concepticon:
            # the exact id route has already run, before gloss lookup; reaching
            # here means the id is not in the mapping, or its part of speech
            # disagrees, and only the gloss is left
            found = by_id.get(sense.concepticon)
            if found and found[1] == sense.pos:
                sense.ili, sense.method = found[0], "concepticon-id"
                continue
        for gloss in sense.glosses:
            found = concepticon.get(normalise_gloss(gloss).lower())
            if found and found[1] == sense.pos:
                sense.ili, sense.method = found[0], "concepticon"
                break


def build_synsets(senses: list[OntSense]) -> dict[str, list[OntSense]]:
    """Group senses into synsets: one per ILI, plus one each for unlinked senses."""
    groups: dict[str, list[OntSense]] = defaultdict(list)
    unlinked = 0
    for sense in senses:
        if sense.ili:
            groups[sense.ili].append(sense)
        else:
            unlinked += 1
            groups[f"u{unlinked:04d}"].append(sense)
    return dict(groups)


def attributes(pairs: list[tuple[str, str | None]]) -> str:
    """Render XML attributes, skipping empty values."""
    return "".join(f" {name}={quoteattr(value)}" for name, value in pairs if value)


def synset_relations(
    entries: list[Entry], synset_of: dict[int, str], concept_id: str
) -> dict[str, set[tuple[str, str, str | None]]]:
    """Every synset relation the ontology's classifier markup implies.

    A classifier synset gets `exemplifies` to the concept `classifier`, and one
    `classifies` per example noun the source gives. The noun gets the converse
    `classified_by`. Where the source's English gloss picks out exactly one sense
    of the Hmong noun the relation is certain; where only the form matches, every
    sense of that form is related at a confidence of 0.5, because the source does
    not say which reading it meant.
    """
    by_form: dict[str, list[tuple[str, OntSense]]] = defaultdict(list)
    for entry in entries:
        if entry.pos == "x":
            continue
        for sense in entry.senses:
            by_form[entry.form].append((synset_of[id(sense)], sense))
    classifier_synsets: dict[str, list[str]] = defaultdict(list)
    for entry in entries:
        if entry.pos == "x":
            for sense in entry.senses:
                classifier_synsets[entry.form].append(synset_of[id(sense)])

    relations: dict[str, set[tuple[str, str, str | None]]] = defaultdict(set)

    def relate(classifier_id: str, noun_id: str, confidence: str | None) -> None:
        relations[classifier_id].add(("classifies", noun_id, confidence))
        relations[noun_id].add(("classified_by", classifier_id, confidence))

    for entry in entries:
        if entry.pos != "x":
            continue
        for sense in entry.senses:
            source = synset_of[id(sense)]
            relations[source].add(("exemplifies", concept_id, None))
            for noun_form, gloss in sense.classifies:
                found = by_form.get(noun_form)
                if not found:
                    continue
                wanted = normalise_gloss(gloss).lower()
                exact = [
                    synset_id for synset_id, noun in found
                    if any(normalise_gloss(g).lower() == wanted for g in noun.glosses)
                ]
                if len(exact) == 1:
                    relate(source, exact[0], "1.0")
                else:
                    for synset_id, _ in found:
                        relate(source, synset_id, "0.5")

    # the converse direction, from the class-noun members that name their classifier
    for entry in entries:
        if entry.pos == "x":
            continue
        for sense in entry.senses:
            for classifier_form in sense.classified_by:
                for classifier_id in classifier_synsets.get(classifier_form, []):
                    relate(classifier_id, synset_of[id(sense)], "1.0")
    return dict(relations)


def write_lmf(
    path: Path,
    entries: list[Entry],
    groups: dict[str, list[OntSense]],
    hierarchy: dict[str, str],
    meta: argparse.Namespace,
) -> None:
    """Write the WN-LMF document."""
    synset_of: dict[int, str] = {}
    synset_ids: dict[str, str] = {}
    for number, (key, members) in enumerate(sorted(groups.items()), start=1):
        synset_id = f"{meta.lexicon}-s{number:05d}-{members[0].pos}"
        synset_ids[key] = synset_id
        for sense in members:
            synset_of[id(sense)] = synset_id

    concept_id = f"{meta.lexicon}-s00000-n"
    relations = synset_relations(entries, synset_of, concept_id)
    need_concept = any(
        any(r[0] == "exemplifies" for r in rels) for rels in relations.values()
    )

    lines: list[str] = ['<?xml version="1.0" encoding="UTF-8"?>', DOCTYPE]
    lines.append(f'<LexicalResource xmlns:dc="{NS}">')
    # id, label, language, email, license and version are #REQUIRED by the DTD,
    # so they are emitted even when empty rather than dropped.
    lines.append(
        "  <Lexicon"
        + "".join(
            f" {name}={quoteattr(value)}"
            for name, value in [
                ("id", meta.lexicon),
                ("label", meta.label),
                ("language", meta.language),
                ("email", meta.email),
                ("license", meta.license or "UNSPECIFIED"),
                ("version", meta.version),
            ]
        )
        + attributes(
            [
                ("url", meta.url),
                ("citation", meta.citation),
                ("dc:creator", meta.creator),
                ("dc:description", meta.description),
            ]
        )
        + ">"
    )

    for number, entry in enumerate(sorted(entries, key=lambda e: (e.form, e.pos)), start=1):
        entry_id = f"{meta.lexicon}-e{number:05d}-{entry.pos}"
        note = "; ".join(entry.notes) or None
        lines.append(
            "    <LexicalEntry"
            + attributes(
                [
                    ("id", entry_id),
                    ("dc:source", ", ".join(entry.sources) or None),
                    ("note", note),
                    ("status", "foreign_word" if entry.foreign else None),
                ]
            )
            + ">"
        )
        lines.append(
            f'      <Lemma writtenForm={quoteattr(entry.form)} '
            f'partOfSpeech="{entry.pos}"/>'
        )
        for variant in entry.variants:
            lines.append(f"      <Form writtenForm={quoteattr(variant)}/>")
        for position, sense in enumerate(entry.senses, start=1):
            lines.append(
                "      <Sense"
                + attributes(
                    [
                        ("id", f"{entry_id}-{position}"),
                        ("synset", synset_of[id(sense)]),
                        ("note", sense.note),
                    ]
                )
                + "/>"
            )
        lines.append("    </LexicalEntry>")

    if need_concept:
        # a local stand-in for the concept `classifier`, so that `exemplifies` has
        # something inside this lexicon to point at; the ILI carries the identity
        lines.append(
            f'    <Synset id={quoteattr(concept_id)} ili={quoteattr(CLASSIFIER_ILI)}'
            ' partOfSpeech="n" lexicalized="false"'
            ' note="target of exemplifies for the classifiers">'
        )
        lines.append(f'      <Definition language="en">{escape(CLASSIFIER_GLOSS)}</Definition>')
        lines.append("    </Synset>")

    for key, members in sorted(groups.items()):
        synset_id = synset_ids[key]
        ili = members[0].ili or ""
        glosses: list[str] = []
        for sense in members:
            for gloss in sense.glosses:
                pretty = normalise_gloss(gloss)
                if pretty not in glosses:
                    glosses.append(pretty)
        categories = sorted({sense.category for sense in members})
        functions = sorted({f for sense in members for f in sense.functions})
        # a KinDiv kin-type code identifies a kinship concept across languages even
        # where the interlingual index has no entry for it, so it goes on the synset
        # as dc:identifier, which is what KinDiv's own build does
        kindiv = sorted({s.kindiv for s in members if s.kindiv})
        # id and ili are #REQUIRED; an unlinked synset carries ili="".
        lines.append(
            "    <Synset"
            + f' id={quoteattr(synset_id)} ili={quoteattr(ili)}'
            + attributes(
                [
                    ("partOfSpeech", members[0].pos),
                    ("dc:subject", ", ".join(categories)),
                    ("dc:type", ", ".join(functions) or None),
                    ("dc:identifier",
                     f"KinDiv:{kindiv[0]}" if len(kindiv) == 1 else None),
                    ("note", f"linked by {members[0].method}" if ili else members[0].method),
                ]
            )
            + ">"
        )
        lines.append(
            f'      <Definition language="en">{escape("; ".join(glosses))}</Definition>'
        )
        for rel_type, target, confidence in sorted(relations.get(synset_id, set())):
            lines.append(
                "      <SynsetRelation"
                + attributes([("relType", rel_type), ("target", target),
                              ("confidenceScore", confidence)])
                + "/>"
            )
        lines.append("    </Synset>")

    lines.append("  </Lexicon>")
    lines.append("</LexicalResource>")
    path.write_text("\n".join(lines) + "\n", encoding="utf8")


def write_report(path: Path, senses: list[OntSense], max_candidates: int = 6) -> None:
    """Write a per-sense linking report.

    Unlinked senses list their candidate ILIs together with the English definition
    of each, so choosing the right one is a reading task rather than a lookup task.
    """
    with path.open("w", encoding="utf8") as handle:
        handle.write("form\tpos\tcategory\tglosses\tmethod\tili\tcandidates\n")
        for sense in sorted(senses, key=lambda s: (s.method, s.form)):
            shown = sorted(sense.candidates)[:max_candidates]
            choices = " | ".join(
                f"{ili}={sense.candidate_notes.get(ili, '?')}" for ili in shown
            )
            if len(sense.candidates) > max_candidates:
                choices += f" | (+{len(sense.candidates) - max_candidates} more)"
            handle.write(
                "\t".join(
                    [
                        sense.form,
                        sense.pos,
                        sense.category,
                        "; ".join(sense.glosses),
                        sense.method,
                        sense.ili or "",
                        choices,
                    ]
                )
                + "\n"
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--ontology", type=Path, required=True,
                        help="hmong_ontology.xml from the hmong-ontology repository")
    parser.add_argument("--output", type=Path, required=True, help="WN-LMF file to write")
    parser.add_argument("--report", type=Path, help="per-sense linking report (TSV)")
    parser.add_argument("--english", default="oewn:2025+",
                        help="English wordnet to link against (default: oewn:2025+, "
                             "the edition Cygnet merges the output with and the one "
                             "facts.py reports against. The `+` edition adds proper "
                             "names, which some Concepticon concept sets name)")
    parser.add_argument("--data-directory", type=Path, default=DATA_DIR,
                        help=f"wn data directory to read from (default: {DATA_DIR}, "
                             f"as written by load_pivots.py; never the user's own)")
    parser.add_argument("--pin-file", type=Path, default=PIN_FILE,
                        help=f"the wordnet releases triangulation may use, written "
                             f"by load_pivots.py from Cygnet's wordnets.toml "
                             f"(default: {PIN_FILE})")
    parser.add_argument("--no-stative-adjective", action="store_true",
                        help="do not try 'be X' stative verb glosses as English adjectives")
    parser.add_argument("--no-morphy", action="store_true",
                        help="do not fall back to morphological analysis of glosses")
    parser.add_argument("--no-category-filter", action="store_true",
                        help="do not use ontology categories to filter candidate synsets")
    parser.add_argument("--dialect", default="WH", choices=["WH", "GM", "all"],
                        help="which dialect to convert (default: WH, White Hmong)")
    parser.add_argument("--concepticon", type=Path,
                        help="concepticon-ili.tsv, to link glosses English WordNet "
                             "lookup cannot resolve")
    parser.add_argument("--pivots", type=Path, metavar="FILE",
                        help="dbnary-pivots.tsv: other languages' translations of the "
                             "same senses, for triangulation. Needs the pivot "
                             "wordnets in the wn data directory")
    parser.add_argument("--pivot-review", type=Path, metavar="FILE",
                        help="write the triangulation groups that did not decide")
    parser.add_argument("--allow-missing-pivots", action="store_true",
                        help="triangulate even though some pivot wordnets are not "
                             "loaded. The links then depend on which wordnets happen "
                             "to be installed, so this is for exploration, not for "
                             "any run whose figures are reported")
    parser.add_argument("--dbnary-review", type=Path, metavar="FILE",
                        help="write the Wiktionary candidates the definition "
                             "comparison could not decide, as an annotation sheet")
    parser.add_argument("--dbnary", type=Path, metavar="FILE",
                        help="dbnary-hmong.tsv, the sense-anchored Wiktionary "
                             "translations produced by fetch_dbnary.py")
    parser.add_argument("--cldf", type=Path, action="append",
                        metavar="DIR:LANGUAGE:NAME[:DIALECT]",
                        help="a CLDF wordlist directory, a language id within it, and "
                             "a short name for provenance, colon-separated; repeatable. "
                             "A fourth field names the dialect the wordlist records, "
                             "WH or GM, and defaults to WH. Needs --concepticon. "
                             "Example: ../wold/cldf:WhiteHmong:WOLD:WH")
    parser.add_argument("--lexicon", default="hmnont", help="lexicon id")
    parser.add_argument("--label", default="Hmong Ontology Wordnet")
    parser.add_argument("--language", default="",
                        help="BCP-47 code; defaults to mww for WH and hnj for GM")
    parser.add_argument("--version", default="0.1")
    parser.add_argument("--email", default="")
    parser.add_argument("--license", default="",
                        help="license URL. The source has no LICENSE file; "
                             "the output cannot be redistributed until this is set")
    parser.add_argument("--url", default="https://github.com/nathanmwhite/hmong-ontology")
    parser.add_argument("--citation", default="")
    parser.add_argument("--creator", default="Nathan M. White")
    parser.add_argument("--description",
                        default="Converted from the Hmong semantic ontology to WN-LMF.")
    args = parser.parse_args()

    if args.data_directory:
        wn.config.data_directory = args.data_directory
    if not args.language:
        args.language = DIALECT_LANGUAGES.get(args.dialect, "hmn")
    if args.dialect != "WH":
        args.lexicon = f"{args.lexicon}-{args.dialect.lower()}"

    senses, hierarchy, entries = read_ontology(args.ontology, args.dialect)
    if not senses:
        raise SystemExit(f"{args.ontology}: no senses for dialect {args.dialect}")
    print(f"read {len(entries)} entries, {len(senses)} senses, "
          f"{len(hierarchy)} categories from {args.ontology} (dialect {args.dialect})")

    try:
        english = wn.Wordnet(lexicon=args.english)
    except wn.Error as error:
        raise SystemExit(
            f"cannot open the English wordnet {args.english!r} in "
            f"{args.data_directory}: {error}\n"
            f"Every linking route goes through English WordNet, so the converter "
            f"needs it. Load the pinned wordnets first:\n"
            f"    uv run load_pivots.py --from ../cygnet/bin/raw_wns\n"
            f"or point --data-directory at a wn database that already has it."
        ) from error
    lemmatiser = None if args.no_morphy else Morphy(english)
    concepticon = by_id = None
    if args.concepticon:
        concepticon = read_concepticon(args.concepticon)
        by_id = read_concepticon_ids(args.concepticon)
        print(f"read {len(concepticon)} exact Concepticon links from {args.concepticon}")

    for spec in args.cldf or []:
        if not by_id:
            raise SystemExit("--cldf needs --concepticon: a CLDF wordlist reaches the "
                             "ILI through Concepticon concept sets")
        parts = str(spec).split(":")
        if len(parts) not in (3, 4):
            raise SystemExit(
                f"--cldf wants DIR:LANGUAGE:NAME[:DIALECT], got {spec!r}")
        directory, language, name = Path(parts[0]), parts[1], parts[2]
        # the dialect the wordlist records, not the dialect being built. WOLD's
        # doculect is White Hmong, so stamping it with whatever --dialect asked for
        # put 1,400 White Hmong forms into the Green Mong lexicon
        wordlist_dialect = parts[3] if len(parts) == 4 else "WH"
        if wordlist_dialect not in DIALECT_LANGUAGES:
            raise SystemExit(f"--cldf dialect must be one of "
                             f"{'/'.join(DIALECT_LANGUAGES)}, got {wordlist_dialect!r}")
        if args.dialect not in ("all", wordlist_dialect):
            print(f"skipping {directory} ({name}): it records {wordlist_dialect}, "
                  f"and this is a {args.dialect} lexicon")
            continue
        extra = read_cldf(directory, language, name)
        if not extra:
            raise SystemExit(f"{directory}: no forms for language {language!r}")
        for sense in extra:
            sense.dialect = wordlist_dialect
        created = merge_into_entries(entries, extra)
        senses.extend(extra)
        print(f"read {len(extra)} {language} senses from {directory} as {name} "
              f"({wordlist_dialect}): {created} new entries, "
              f"{len(extra) - created} on entries already present")

    triangulated: set[tuple[str, str, str]] = set()
    if args.pivots:
        pivot_wordnets, missing_pivots = open_pivots(args.pivots, args.pin_file)
        if not pivot_wordnets:
            raise SystemExit(
                f"{args.pivots}: none of its pivot wordnets are in the wn data "
                f"directory. Load them with load_pivots.py first.")
        if missing_pivots and not args.allow_missing_pivots:
            raise SystemExit(
                f"{args.pivots}: {len(missing_pivots)} of its "
                f"{len(pivot_wordnets) + len(missing_pivots)} pivot wordnets are not "
                f"in the wn data directory: {' '.join(missing_pivots)}.\n"
                f"Triangulation counts languages, so a missing pivot can change which "
                f"ILI wins, not just how many senses are linked. Load them with "
                f"load_pivots.py, or pass --allow-missing-pivots to accept a run "
                f"whose links depend on an incomplete installation.")
        if missing_pivots:
            print(f"warning: triangulating without {len(missing_pivots)} pivot "
                  f"wordnets: {' '.join(missing_pivots)}", file=sys.stderr)
        extra, pivot_review = read_dbnary_pivots(
            args.pivots, args.dialect if args.dialect != "all" else "WH",
            pivot_wordnets)
        triangulated = {(s.form, s.glosses[0], s.definition) for s in extra}
        created = merge_into_entries(entries, extra)
        senses.extend(extra)
        print(f"triangulated {len(extra)} senses through {len(pivot_wordnets)} pivot "
              f"wordnets: {created} new entries, {len(extra) - created} on entries "
              f"already present; {len(pivot_review)} groups undecided")
        if args.pivot_review:
            write_review(args.pivot_review, pivot_review)
            print(f"  wrote {args.pivot_review}")

    if args.dbnary:
        review: list[dict[str, str]] = []
        extra = read_dbnary(args.dbnary, english,
                            args.dialect if args.dialect != "all" else "WH",
                            review=review, already=triangulated)
        created = merge_into_entries(entries, extra)
        senses.extend(extra)
        print(f"read {len(extra)} sense-anchored translations from {args.dbnary}: "
              f"{created} new entries, {len(extra) - created} on entries already present")
        if args.dbnary_review:
            write_review(args.dbnary_review, review)
            print(f"  wrote {args.dbnary_review}: {len(review)} declined candidates "
                  f"for a speaker to choose between")

    link_senses(senses, english, not args.no_stative_adjective,
                not args.no_category_filter, lemmatiser, concepticon, by_id)

    record_ili_pos(senses, english)
    merged = dedupe_senses(entries)
    if merged:
        print(f"  merged {merged} senses that two sources resolved to the same ILI")
        # the discarded senses must not keep their own synsets
        senses = [s for entry in entries for s in entry.senses]

    groups = build_synsets(senses)
    write_lmf(args.output, entries, groups, hierarchy, args)

    methods = Counter(sense.method for sense in senses)
    linked = sum(1 for sense in senses if sense.ili)
    # the classifiers are the senses that carry no ILI by design. Other senses may
    # also have part of speech `x` -- a CLDF wordlist's function words do -- and
    # those are linkable, so count by category rather than by part of speech.
    linkable = [s for s in senses if not s.is_classifier]
    classifiers = len(senses) - len(linkable)
    print(f"\nwrote {args.output}")
    print(f"  synsets           {len(groups)}")
    print(f"  linked to an ILI  {linked} / {len(linkable)} linkable senses "
          f"({100 * linked / max(len(linkable), 1):.0f}%)")
    print(f"  distinct ILIs     {len({s.ili for s in senses if s.ili})}")
    print(f"  classifiers       {classifiers} (no ILI by design)")
    kin = sum(1 for s in senses if s.kindiv)
    if kin:
        print(f"  KinDiv concepts   {kin} senses carry a kin-type identifier "
              f"({len({s.kindiv for s in senses if s.kindiv})} distinct)")
    if args.cldf or args.dbnary or args.pivots:
        ours = {s.ili for s in senses if s.ili and not s.source}
        print(f"  ILIs from the ontology        {len(ours)}")
        for name in dict.fromkeys(s.source for s in senses if s.source):
            theirs = {s.ili for s in senses if s.ili and s.source == name}
            print(f"  ILIs from {name:20} {len(theirs):5}  "
                  f"({len(theirs - ours)} not in the ontology)")
    for method, count in methods.most_common():
        print(f"    {method:16} {count:5}")

    if args.report:
        write_report(args.report, senses)
        print(f"\nwrote {args.report}")

    if not args.license:
        print("\nWARNING: no --license given. The source ontology has no LICENSE file, "
              "so the output is not redistributable until its author sets one.",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
