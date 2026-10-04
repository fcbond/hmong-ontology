#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["wn>=1.1", "pytest>=8"]
# ///
"""Tests for the Hmong ontology to WN-LMF converter.

Run with:  uv run --with pytest --with wn pytest test_hmong2lmf.py -q

English WordNet is mocked throughout, so these tests neither need a populated wn
database nor touch one. The single integration test writes into a temporary wn
data directory.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import pytest

import hmong2lmf as m

ONTOLOGY = """<?xml version="1.0" encoding="UTF-8"?>
<root>
<category_set>
  <category><term>animal</term></category>
  <category><term>wild_animal</term><superordinate>animal</superordinate></category>
  <category><term>verb.stative</term></category>
  <category><term>verb.motion</term></category>
  <category><term>classifier</term></category>
  <category><term>sortal_classifier</term><superordinate>classifier</superordinate></category>
  <category><term>mensural_classifier</term><superordinate>classifier</superordinate></category>
</category_set>
<word_set>
  <lemma>
    <form>qav</form>
    <sense><meaning>frog</meaning><category>animal</category></sense>
  </lemma>
  <lemma>
    <form>tsev_kho_mob</form>
    <note>compositional</note>
    <headword>tsev</headword>
    <sense><meaning>hospital</meaning><category>animal</category></sense>
  </lemma>
  <lemma>
    <form>nqe</form>
    <variant>nqi</variant>
    <source>Chinese</source>
    <status>foreign_word</status>
    <sense><meaning>price</meaning><meaning>cost</meaning><category>animal</category></sense>
  </lemma>
  <lemma>
    <form>kaj</form>
    <sense><meaning>be bright</meaning><category>verb.stative</category></sense>
    <sense><meaning>go</meaning><category>verb.motion</category></sense>
  </lemma>
  <lemma>
    <form>tus</form>
    <dialect>WH</dialect>
    <sense>
      <meaning>a sortal classifier used with living beings</meaning>
      <category>sortal_classifier</category>
      <function>classifier</function>
      <classifies form="qav">frog</classifies>
      <classifies form="nqe">price</classifies>
      <note>attestation: B:32</note>
    </sense>
  </lemma>
  <lemma>
    <form>tug</form>
    <dialect>GM</dialect>
    <sense>
      <category>sortal_classifier</category>
      <function>classifier</function>
    </sense>
  </lemma>
  <lemma>
    <form>ntoo_ciab</form>
    <dialect>WH</dialect>
    <headword>ntoo</headword>
    <sense>
      <meaning>larch</meaning>
      <category>animal</category>
      <classified_by form="tus"/>
    </sense>
  </lemma>
</word_set>
</root>
"""


class FakeSynset:
    """Stands in for a wn.Synset."""

    def __init__(self, ili: str, lexfile: str, definition: str = "",
                 pos: str = "") -> None:
        self.ili = ili
        self.pos = pos
        self._lexfile = lexfile
        self._definition = definition

    def lexfile(self) -> str:
        return self._lexfile

    def definitions(self) -> list[str]:
        return [self._definition] if self._definition else []


class FakeWordnet:
    """Stands in for a wn.Wordnet, keyed on (lemma, pos)."""

    def __init__(self, table: dict[tuple[str, str], list[FakeSynset]]) -> None:
        self.table = table

    def synsets(self, lemma: str | None = None, pos: str | None = None,
                ili: str | None = None) -> list[FakeSynset]:
        if ili is not None:
            return [s for group in self.table.values() for s in group if s.ili == ili]
        return self.table.get((lemma or "", pos or ""), [])


@pytest.fixture
def ontology_file(tmp_path: Path) -> Path:
    path = tmp_path / "ont.xml"
    path.write_text(ONTOLOGY, encoding="utf8")
    return path


# --- pure helpers -----------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("tsev_kho_mob", "tsev kho mob"), ("qav", "qav"), ("  a_b  ", "a b")],
)
def test_normalise_form_replaces_underscores(raw: str, expected: str) -> None:
    assert m.normalise_form(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("be_developed", "be developed"), ("be  bright", "be bright"), (" frog ", "frog")],
)
def test_normalise_gloss_unifies_separators(raw: str, expected: str) -> None:
    assert m.normalise_gloss(raw) == expected


def test_lexfiles_for_verb_category_is_itself() -> None:
    assert m.lexfiles_for("verb.motion") == ("verb.motion",)


def test_lexfiles_for_noun_category_uses_table() -> None:
    assert m.lexfiles_for("wild_animal") == ("noun.animal",)


def test_lexfiles_for_unknown_category_is_empty() -> None:
    assert m.lexfiles_for("no_such_category") == ()


def test_sense_pos_follows_category() -> None:
    noun = m.OntSense(0, "qav", ["frog"], "animal")
    verb = m.OntSense(0, "kaj", ["go"], "verb.motion")
    assert (noun.pos, verb.pos) == ("n", "v")


# --- parsing ----------------------------------------------------------------


def test_read_ontology_counts(ontology_file: Path) -> None:
    senses, hierarchy, entries = m.read_ontology(ontology_file)
    assert len(senses) == 7
    assert hierarchy["wild_animal"] == "animal"
    # kaj has a stative and a motion sense: both verbs, so one merged entry.
    # tug is Green Mong, so the default White Hmong reading leaves it out.
    assert len(entries) == 6


def test_read_ontology_merges_homographs_of_same_pos(ontology_file: Path) -> None:
    _, _, entries = m.read_ontology(ontology_file)
    kaj = next(e for e in entries if e.form == "kaj")
    assert len(kaj.senses) == 2


def test_read_ontology_keeps_variant_source_and_status(ontology_file: Path) -> None:
    _, _, entries = m.read_ontology(ontology_file)
    nqe = next(e for e in entries if e.form == "nqe")
    assert nqe.variants == ["nqi"]
    assert nqe.sources == ["Chinese"]
    assert nqe.foreign is True


def test_read_ontology_records_headword_as_note(ontology_file: Path) -> None:
    _, _, entries = m.read_ontology(ontology_file)
    entry = next(e for e in entries if e.form == "tsev kho mob")
    assert any("headword: tsev" in note for note in entry.notes)


# --- linking ----------------------------------------------------------------


def test_monosemous_gloss_links() -> None:
    english = FakeWordnet({("frog", "n"): [FakeSynset("i100", "noun.animal")]})
    sense = m.OntSense(0, "qav", ["frog"], "animal")
    m.link_senses([sense], english, stative_adjective=False, use_lexfile=True)
    assert (sense.ili, sense.method) == ("i100", "monosemous")


def test_ambiguous_gloss_does_not_link() -> None:
    english = FakeWordnet(
        {("crab", "n"): [FakeSynset("i1", "noun.animal"), FakeSynset("i2", "noun.animal")]}
    )
    sense = m.OntSense(0, "x", ["crab"], "animal")
    m.link_senses([sense], english, stative_adjective=False, use_lexfile=True)
    assert sense.ili is None
    assert sense.method.startswith("ambiguous")
    assert sense.candidates == {"i1", "i2"}


def test_category_filter_resolves_ambiguity() -> None:
    english = FakeWordnet(
        {
            ("crab", "n"): [
                FakeSynset("i1", "noun.animal", "a decapod"),
                FakeSynset("i2", "noun.person", "a grouch"),
                FakeSynset("i3", "noun.food", "edible flesh"),
            ]
        }
    )
    sense = m.OntSense(0, "x", ["crab"], "animal")
    m.link_senses([sense], english, stative_adjective=False, use_lexfile=True)
    assert (sense.ili, sense.method) == ("i1", "monosemous+category")


def test_category_filter_off_leaves_it_ambiguous() -> None:
    english = FakeWordnet(
        {("crab", "n"): [FakeSynset("i1", "noun.animal"), FakeSynset("i2", "noun.person")]}
    )
    sense = m.OntSense(0, "x", ["crab"], "animal")
    m.link_senses([sense], english, stative_adjective=False, use_lexfile=False)
    assert sense.ili is None


def test_category_filter_never_discards_every_candidate() -> None:
    """A category disagreeing with English WordNet must not silently yield nothing."""
    english = FakeWordnet({("thing", "n"): [FakeSynset("i9", "noun.artifact")]})
    sense = m.OntSense(0, "x", ["thing"], "animal")  # noun.animal, matches nothing
    m.link_senses([sense], english, stative_adjective=False, use_lexfile=True)
    assert sense.ili == "i9"
    assert sense.method == "monosemous"  # no "+category": filtering did not apply


def test_two_glosses_intersecting_in_one_ili_link() -> None:
    english = FakeWordnet(
        {
            ("price", "n"): [FakeSynset("i1", "noun.animal"), FakeSynset("i2", "noun.animal")],
            ("cost", "n"): [FakeSynset("i2", "noun.animal"), FakeSynset("i3", "noun.animal")],
        }
    )
    sense = m.OntSense(0, "nqe", ["price", "cost"], "animal")
    m.link_senses([sense], english, stative_adjective=False, use_lexfile=True)
    assert (sense.ili, sense.method) == ("i2", "intersection")


def test_disjoint_glosses_report_no_intersection() -> None:
    english = FakeWordnet(
        {
            ("price", "n"): [FakeSynset("i1", "noun.animal")],
            ("cost", "n"): [FakeSynset("i2", "noun.animal")],
        }
    )
    sense = m.OntSense(0, "nqe", ["price", "cost"], "animal")
    m.link_senses([sense], english, stative_adjective=False, use_lexfile=True)
    assert sense.ili is None
    assert sense.method.startswith("no-intersection")
    assert sense.candidates == {"i1", "i2"}


def test_unmatched_gloss_is_nomatch() -> None:
    sense = m.OntSense(0, "x", ["marriage negotiator"], "person")
    m.link_senses([sense], FakeWordnet({}), stative_adjective=False, use_lexfile=True)
    assert (sense.ili, sense.method) == (None, "nomatch")


def test_stative_verb_falls_back_to_adjective() -> None:
    english = FakeWordnet({("bright", "a"): [FakeSynset("i77", "adj.all")]})
    sense = m.OntSense(0, "kaj", ["be bright"], "verb.stative")
    m.link_senses([sense], english, stative_adjective=True, use_lexfile=True)
    assert sense.ili == "i77"


def test_stative_fallback_can_be_disabled() -> None:
    english = FakeWordnet({("bright", "a"): [FakeSynset("i77", "adj.all")]})
    sense = m.OntSense(0, "kaj", ["be bright"], "verb.stative")
    m.link_senses([sense], english, stative_adjective=False, use_lexfile=True)
    assert sense.ili is None


def test_candidate_definitions_are_recorded_for_review() -> None:
    english = FakeWordnet(
        {
            ("crab", "n"): [
                FakeSynset("i1", "noun.animal", "a decapod"),
                FakeSynset("i2", "noun.animal", "a pubic louse"),
            ]
        }
    )
    sense = m.OntSense(0, "x", ["crab"], "animal")
    m.link_senses([sense], english, stative_adjective=False, use_lexfile=True)
    assert sense.candidate_notes["i1"] == "a decapod"
    assert sense.candidate_notes["i2"] == "a pubic louse"


# --- synset grouping --------------------------------------------------------


def test_senses_sharing_an_ili_share_a_synset() -> None:
    a = m.OntSense(0, "a", ["x"], "animal")
    b = m.OntSense(1, "b", ["x"], "animal")
    a.ili = b.ili = "i5"
    groups = m.build_synsets([a, b])
    assert len(groups) == 1
    assert len(groups["i5"]) == 2


def test_unlinked_senses_get_their_own_synsets() -> None:
    a = m.OntSense(0, "a", ["x"], "animal")
    b = m.OntSense(1, "b", ["y"], "animal")
    groups = m.build_synsets([a, b])
    assert len(groups) == 2
    assert all(len(members) == 1 for members in groups.values())


# --- output -----------------------------------------------------------------


def _meta(**overrides: object) -> argparse.Namespace:
    base: dict[str, object] = {
        "lexicon": "test", "label": "Test", "language": "mww", "email": "",
        "license": "", "version": "0.1", "url": "", "citation": "",
        "creator": "", "description": "",
    }
    base.update(overrides)
    return argparse.Namespace(**base)


def test_written_lmf_has_required_attributes(ontology_file: Path, tmp_path: Path) -> None:
    senses, hierarchy, entries = m.read_ontology(ontology_file)
    groups = m.build_synsets(senses)
    out = tmp_path / "out.xml"
    m.write_lmf(out, entries, groups, hierarchy, _meta())
    text = out.read_text(encoding="utf8")
    # #REQUIRED attributes must survive even when the value is empty
    assert 'email=""' in text
    assert 'license="UNSPECIFIED"' in text
    assert 'ili=""' in text


def test_entry_and_synset_ids_do_not_collide(ontology_file: Path, tmp_path: Path) -> None:
    import xml.etree.ElementTree as ET

    senses, hierarchy, entries = m.read_ontology(ontology_file)
    groups = m.build_synsets(senses)
    out = tmp_path / "out.xml"
    m.write_lmf(out, entries, groups, hierarchy, _meta())
    root = ET.parse(out).getroot()
    ids = [element.get("id") for element in root.iter() if element.get("id")]
    assert len(ids) == len(set(ids))


def test_written_lmf_escapes_markup(tmp_path: Path) -> None:
    sense = m.OntSense(0, "x", ['a & b <c>'], "animal")
    entry = m.Entry('x & y', "n", senses=[sense])
    out = tmp_path / "out.xml"
    m.write_lmf(out, [entry], m.build_synsets([sense]), {}, _meta())
    text = out.read_text(encoding="utf8")
    assert "&amp;" in text and "<c>" not in text


# --- classifiers, class nouns and dialects -----------------------------------


def test_classifier_category_gives_part_of_speech_x() -> None:
    sense = m.OntSense(0, "tus", ["a sortal classifier"], "sortal_classifier")
    assert sense.pos == "x"


def test_classifiers_are_not_linked_by_gloss() -> None:
    """A classifier's meaning is a definition; looking it up as a lemma is nonsense."""
    sense = m.OntSense(0, "lub", ["a sortal classifier used with round objects"],
                       "sortal_classifier")
    m.link_senses([sense], FakeWordnet({}), True, True)
    assert sense.ili is None
    assert sense.method == "classifier"


def test_read_ontology_keeps_dialect_of_requested_variety(ontology_file: Path) -> None:
    _, _, white = m.read_ontology(ontology_file, "WH")
    _, _, green = m.read_ontology(ontology_file, "GM")
    assert {e.form for e in green} == {"tug"}
    assert "tug" not in {e.form for e in white}
    assert "tus" in {e.form for e in white}


def test_read_ontology_dialect_all_keeps_both(ontology_file: Path) -> None:
    _, _, entries = m.read_ontology(ontology_file, "all")
    assert {"tus", "tug"} <= {e.form for e in entries}


def test_undescribed_classifier_falls_back_to_its_class(ontology_file: Path) -> None:
    senses, _, _ = m.read_ontology(ontology_file, "GM")
    assert [s.glosses for s in senses] == [["a sortal classifier"]]


def test_classifies_is_read_with_its_gloss(ontology_file: Path) -> None:
    senses, _, _ = m.read_ontology(ontology_file, "WH")
    classifier = next(s for s in senses if s.pos == "x")
    assert classifier.classifies == [("qav", "frog"), ("nqe", "price")]
    assert classifier.functions == ["classifier"]


def test_class_noun_member_records_its_classifier(ontology_file: Path) -> None:
    senses, _, _ = m.read_ontology(ontology_file, "WH")
    larch = next(s for s in senses if s.glosses == ["larch"])
    assert larch.classified_by == ["tus"]


def _relations(ontology_file: Path, tmp_path: Path) -> str:
    senses, hierarchy, entries = m.read_ontology(ontology_file, "WH")
    groups = m.build_synsets(senses)
    out = tmp_path / "out.xml"
    m.write_lmf(out, entries, groups, hierarchy, _meta())
    return out.read_text(encoding="utf8")


def test_classifier_exemplifies_the_classifier_concept(ontology_file, tmp_path) -> None:
    text = _relations(ontology_file, tmp_path)
    assert f'ili="{m.CLASSIFIER_ILI}"' in text
    assert 'relType="exemplifies"' in text


def test_classifies_and_its_converse_are_both_written(ontology_file, tmp_path) -> None:
    text = _relations(ontology_file, tmp_path)
    assert text.count('relType="classifies"') == text.count('relType="classified_by"')
    assert text.count('relType="classifies"') >= 2


def test_gloss_confirmed_classifies_is_certain(ontology_file, tmp_path) -> None:
    """qav has one sense glossed 'frog', so <classifies form="qav">frog</classifies>
    names it unambiguously and the relation carries full confidence."""
    text = _relations(ontology_file, tmp_path)
    assert 'relType="classifies"' in text and 'confidenceScore="1.0"' in text


def test_unknown_classified_form_is_skipped(tmp_path: Path) -> None:
    classifier = m.OntSense(0, "tus", ["a sortal classifier"], "sortal_classifier",
                            classifies=[("nonesuch", "nothing")])
    entry = m.Entry("tus", "x", senses=[classifier])
    out = tmp_path / "out.xml"
    m.write_lmf(out, [entry], m.build_synsets([classifier]), {}, _meta())
    text = out.read_text(encoding="utf8")
    assert 'relType="classifies"' not in text
    assert 'relType="exemplifies"' in text


def test_concepticon_links_only_exact_relations(tmp_path: Path) -> None:
    table = tmp_path / "concepticon.tsv"
    table.write_text(
        "CONCEPTICON_ID\tGLOSS\tILI\tPOS\tRELATION\n"
        "1\tFIREWOOD\ti100\tn\tss\n"
        "2\tVULTURE\ti200\tn\tui\n"
        "3\tNOTHING\t\tn\tss\n",
        encoding="utf8")
    mapping = m.read_concepticon(table)
    assert mapping == {"firewood": ("i100", "n")}


def test_concepticon_links_what_english_lookup_could_not() -> None:
    sense = m.OntSense(0, "taws", ["firewood"], "object")
    m.link_senses([sense], FakeWordnet({}), True, True,
                  concepticon={"firewood": ("i100", "n")})
    assert (sense.ili, sense.method) == ("i100", "concepticon")


def test_concepticon_respects_part_of_speech() -> None:
    sense = m.OntSense(0, "taws", ["firewood"], "verb.motion")
    m.link_senses([sense], FakeWordnet({}), True, True,
                  concepticon={"firewood": ("i100", "n")})
    assert sense.ili is None


def test_concepticon_never_overrides_an_english_link() -> None:
    sense = m.OntSense(0, "qav", ["frog"], "animal")
    m.link_senses([sense], FakeWordnet({("frog", "n"): [FakeSynset("i1", "noun.animal")]}),
                  True, True, concepticon={"frog": ("i999", "n")})
    assert (sense.ili, sense.method) == ("i1", "monosemous")


# --- CLDF wordlists folded in at conversion time -----------------------------


@pytest.fixture
def cldf_dir(tmp_path: Path) -> Path:
    """A minimal CLDF wordlist: forms.csv plus parameters.csv."""
    d = tmp_path / "cldf"
    d.mkdir()
    (d / "parameters.csv").write_text(
        "ID,Name,Concepticon_ID,Concepticon_Gloss,Semantic_category,Semantic_field\n"
        "1-1,the frog,100,FROG,Noun,Animals\n"
        "1-2,to go,200,GO,Verb,Motion\n"
        "1-3,and,300,AND,Function word,Miscellaneous\n",
        encoding="utf8")
    (d / "forms.csv").write_text(
        "ID,Language_ID,Parameter_ID,Form,Borrowed,Analyzability\n"
        "a,Target,1-1,qav,5. no evidence for borrowing,unanalyzable\n"
        "b,Target,1-2,mus,1. clearly borrowed,unanalyzable\n"
        "c,Target,1-3,thiab,5. no evidence for borrowing,analyzable compound\n"
        "d,Other,1-1,nope,5. no evidence for borrowing,unanalyzable\n",
        encoding="utf8")
    return d


def test_read_cldf_takes_only_the_named_language(cldf_dir: Path) -> None:
    senses = m.read_cldf(cldf_dir, "Target", "TEST")
    assert [s.form for s in senses] == ["qav", "mus", "thiab"]


def test_read_cldf_maps_semantic_category_to_part_of_speech(cldf_dir: Path) -> None:
    senses = {s.form: s for s in m.read_cldf(cldf_dir, "Target", "TEST")}
    assert senses["qav"].pos == "n"
    assert senses["mus"].pos == "v"
    # a function word is `x`, "other" -- but unlike a classifier it is still linkable
    assert senses["thiab"].pos == "x"
    assert not senses["thiab"].is_classifier


def test_read_cldf_strips_the_article_from_the_meaning_name(cldf_dir: Path) -> None:
    senses = {s.form: s for s in m.read_cldf(cldf_dir, "Target", "TEST")}
    assert senses["qav"].glosses == ["frog"]
    assert senses["mus"].glosses == ["go"]


def test_read_cldf_keeps_the_borrowing_judgement(cldf_dir: Path) -> None:
    senses = {s.form: s for s in m.read_cldf(cldf_dir, "Target", "TEST")}
    assert "clearly borrowed" in senses["mus"].note
    # no evidence of borrowing is the default and is not worth a note
    assert senses["qav"].note is None
    assert "analyzable compound" in senses["thiab"].note


def test_read_cldf_records_provenance(cldf_dir: Path) -> None:
    assert {s.source for s in m.read_cldf(cldf_dir, "Target", "TEST")} == {"TEST"}


def test_concepticon_id_links_without_consulting_the_gloss() -> None:
    """A CLDF parameter already names a concept set, so no gloss lookup is needed."""
    sense = m.OntSense(0, "qav", ["nonsense gloss"], "Animals", pos_override="n",
                       concepticon="100")
    m.link_senses([sense], FakeWordnet({}), True, False,
                  concepticon_by_id={"100": ("i42", "n")})
    assert (sense.ili, sense.method) == ("i42", "concepticon-id")


def test_concepticon_id_still_respects_part_of_speech() -> None:
    sense = m.OntSense(0, "qav", ["frog"], "Animals", pos_override="v",
                       concepticon="100")
    m.link_senses([sense], FakeWordnet({}), True, False,
                  concepticon_by_id={"100": ("i42", "n")})
    assert sense.ili is None


def test_merge_into_entries_shares_an_entry_for_the_same_form_and_pos() -> None:
    first = m.OntSense(0, "qav", ["frog"], "animal")
    entries = [m.Entry("qav", "n", senses=[first])]
    extra = m.OntSense(0, "qav", ["toad"], "Animals", pos_override="n", source="TEST")
    created = m.merge_into_entries(entries, [extra])
    assert created == 0
    assert len(entries) == 1 and len(entries[0].senses) == 2
    assert entries[0].sources == ["TEST"]


def test_merge_into_entries_creates_an_entry_for_a_new_form() -> None:
    entries = [m.Entry("qav", "n", senses=[m.OntSense(0, "qav", ["frog"], "animal")])]
    extra = m.OntSense(0, "nas", ["rat"], "Animals", pos_override="n", source="TEST")
    assert m.merge_into_entries(entries, [extra]) == 1
    assert len(entries) == 2


def test_dedupe_collapses_two_senses_of_one_entry_on_the_same_ili() -> None:
    a = m.OntSense(0, "qav", ["frog"], "animal")
    a.ili = "i1"
    b = m.OntSense(0, "qav", ["toad"], "Animals", pos_override="n", source="TEST")
    b.ili = "i1"
    entry = m.Entry("qav", "n", senses=[a, b])
    assert m.dedupe_senses([entry]) == 1
    assert len(entry.senses) == 1
    # nothing is lost: the surviving sense carries both glosses
    assert entry.senses[0].glosses == ["frog", "toad"]


def test_dedupe_keeps_senses_on_different_ilis() -> None:
    a = m.OntSense(0, "qav", ["frog"], "animal")
    a.ili = "i1"
    b = m.OntSense(0, "qav", ["drum"], "object")
    b.ili = "i2"
    entry = m.Entry("qav", "n", senses=[a, b])
    assert m.dedupe_senses([entry]) == 0
    assert len(entry.senses) == 2


def test_dedupe_collapses_across_entries_and_keeps_the_ilis_own_pos() -> None:
    """A stative verb and an adjective reaching one ILI are one sense, and the
    part of speech the ILI is recorded under is the one that survives."""
    verb = m.OntSense(0, "kim", ["be expensive"], "verb.stative")
    verb.ili = "i5"
    adj = m.OntSense(0, "kim", ["expensive"], "Property", pos_override="a",
                     source="TEST")
    adj.ili = "i5"
    verb_entry = m.Entry("kim", "v", senses=[verb])
    adj_entry = m.Entry("kim", "a", senses=[adj])
    assert m.dedupe_senses([verb_entry, adj_entry], {"i5": "a"}) == 1
    assert (len(adj_entry.senses), len(verb_entry.senses)) == (1, 0)
    assert "also analysed as v" in adj_entry.senses[0].note


# --- DBnary sense-anchored translations --------------------------------------


@pytest.fixture
def dbnary_file(tmp_path: Path) -> Path:
    p = tmp_path / "dbnary.tsv"
    p.write_text(
        "FORM\tDIALECT\tISO\tENGLISH\tPOS\tDEFINITION\n"
        # the definition matches the animal sense, not the machine sense
        "miv\tWH\tmww\tcat\tnoun\tA small furry carnivorous mammal kept as a pet\n"
        # no definition overlap with either sense: should be declined
        "xyz\tWH\tmww\tcat\tnoun\tSomething entirely unrelated to felines\n"
        # Green Mong, so absent from a White Hmong read
        "phoo\tGM\thnj\tbook\tnoun\tA collection of sheets of paper bound together\n"
        # a part of speech DBnary uses that we do not map
        "abc\tWH\tmww\tand\tconjunction\tA conjunction\n",
        encoding="utf8")
    return p


class DefWordnet:
    """A wordnet whose synsets carry definitions, for the overlap comparison."""

    def __init__(self, table):
        self._table = table

    def synsets(self, form, pos=None):
        return self._table.get((form, pos), [])


class DefSynset:
    def __init__(self, ili, definition):
        self.ili = ili
        self._definition = definition

    def definitions(self):
        return [self._definition]

    def lexfile(self):
        return None


def test_dbnary_picks_the_sense_whose_definition_overlaps(dbnary_file: Path) -> None:
    en = DefWordnet({("cat", "n"): [
        DefSynset("i-animal", "a small furry carnivorous mammal often kept as a pet"),
        DefSynset("i-machine", "a large tracked vehicle used in construction"),
    ]})
    senses = m.read_dbnary(dbnary_file, en, "WH")
    assert [(s.form, s.ili) for s in senses] == [("miv", "i-animal")]
    assert senses[0].method == "dbnary-sense"


def test_dbnary_declines_when_no_definition_is_close_enough(dbnary_file: Path) -> None:
    en = DefWordnet({("cat", "n"): [DefSynset("i-animal", "a small furry mammal")]})
    # 'miv' still matches; 'xyz' shares nothing with the definition and is dropped
    assert {s.form for s in m.read_dbnary(dbnary_file, en, "WH")} == {"miv"}


def test_dbnary_declines_when_two_senses_are_too_close(dbnary_file: Path) -> None:
    twin = "a small furry carnivorous mammal kept as a pet"
    en = DefWordnet({("cat", "n"): [DefSynset("i-a", twin), DefSynset("i-b", twin)]})
    assert m.read_dbnary(dbnary_file, en, "WH") == []


def test_dbnary_takes_only_the_requested_dialect(dbnary_file: Path) -> None:
    en = DefWordnet({("book", "n"): [
        DefSynset("i-book", "a collection of sheets of paper bound together")]})
    assert [s.form for s in m.read_dbnary(dbnary_file, en, "GM")] == ["phoo"]
    assert m.read_dbnary(dbnary_file, en, "WH") == []


def test_dbnary_skips_parts_of_speech_we_do_not_map(dbnary_file: Path) -> None:
    en = DefWordnet({("and", None): [DefSynset("i-and", "a conjunction")]})
    assert m.read_dbnary(dbnary_file, en, "WH") == []


def test_definition_words_drops_function_words_and_short_tokens() -> None:
    assert m.definition_words("A small furry mammal of the family Felidae") == {
        "small", "furry", "mammal", "family", "felidae"}


# --- triangulation through pivot languages ------------------------------------


@pytest.fixture
def pivots_file(tmp_path: Path) -> Path:
    p = tmp_path / "pivots.tsv"
    p.write_text(
        "FORM\tDIALECT\tENGLISH\tDEFINITION\tPIVOT_ISO\tPIVOT_LEXICON\tPIVOT_WORD\n"
        # three languages agree on i-cat: decided
        "miv\tWH\tcat\ta small furry mammal\tfra\tomw-fr\tchat\n"
        "miv\tWH\tcat\ta small furry mammal\tita\tomw-it\tgatto\n"
        "miv\tWH\tcat\ta small furry mammal\tspa\tomw-es\tgato\n"
        # one language only: not enough support
        "xyz\tWH\tthing\tsomething\tfra\tomw-fr\tchose\n"
        # one backer each, so neither reaches the support floor
        "abc\tWH\tbank\ta thing\tfra\tomw-fr\tbanque\n"
        "abc\tWH\tbank\ta thing\tita\tomw-it\triva\n"
        # a genuine tie: two languages for each of two ILIs
        "tie\tWH\tbank\ta thing\tfra\tomw-fr\tbanque\n"
        "tie\tWH\tbank\ta thing\tnld\tomw-nl\tbank\n"
        "tie\tWH\tbank\ta thing\tita\tomw-it\triva\n"
        "tie\tWH\tbank\ta thing\tspa\tomw-es\torilla\n"
        # Green Mong, absent from a White Hmong read
        "phoo\tGM\tbook\ta book\tfra\tomw-fr\tlivre\n",
        encoding="utf8")
    return p


class PivotSynset:
    def __init__(self, ili, pos="n"):
        self.ili = ili
        self.pos = pos

    def definitions(self):
        return []


class PivotWordnet:
    def __init__(self, table):
        self._table = table

    def synsets(self, form=None, pos=None, ili=None):
        if ili is not None:
            return [s for v in self._table.values() for s in v if str(s.ili) == ili][:1]
        return self._table.get(form, [])


@pytest.fixture
def pivot_wordnets():
    return {
        "omw-fr": PivotWordnet({"chat": [PivotSynset("i-cat")],
                                "chose": [PivotSynset("i-thing")],
                                "banque": [PivotSynset("i-bank-money")],
                                "livre": [PivotSynset("i-book")]}),
        "omw-it": PivotWordnet({"gatto": [PivotSynset("i-cat")],
                                "riva": [PivotSynset("i-bank-river")]}),
        "omw-es": PivotWordnet({"gato": [PivotSynset("i-cat"), PivotSynset("i-jack")],
                                "orilla": [PivotSynset("i-bank-river")]}),
        "omw-nl": PivotWordnet({"bank": [PivotSynset("i-bank-money")]}),
    }


def test_triangulation_links_when_languages_agree(pivots_file, pivot_wordnets) -> None:
    senses, _ = m.read_dbnary_pivots(pivots_file, "WH", pivot_wordnets)
    assert [(s.form, s.ili) for s in senses] == [("miv", "i-cat")]
    assert senses[0].method == "triangulated-3"
    assert "fra, ita, spa" in senses[0].note


def test_triangulation_needs_two_languages(pivots_file, pivot_wordnets) -> None:
    """One language backing an ILI is not agreement, it is a single opinion."""
    senses, review = m.read_dbnary_pivots(pivots_file, "WH", pivot_wordnets)
    assert "xyz" not in {s.form for s in senses}
    assert any(r["FORM"] == "xyz" and "two languages" in r["WHY"] for r in review)


def test_triangulation_declines_when_no_ili_reaches_the_floor(
        pivots_file, pivot_wordnets) -> None:
    senses, review = m.read_dbnary_pivots(pivots_file, "WH", pivot_wordnets)
    assert "abc" not in {s.form for s in senses}
    assert any(r["FORM"] == "abc" and "two languages" in r["WHY"] for r in review)


def test_triangulation_declines_a_genuine_tie(pivots_file, pivot_wordnets) -> None:
    """Two languages for each of two ILIs clears the support floor but decides
    nothing, so it goes to review rather than to the lexicon."""
    senses, review = m.read_dbnary_pivots(pivots_file, "WH", pivot_wordnets)
    assert "tie" not in {s.form for s in senses}
    row = next(r for r in review if r["FORM"] == "tie")
    assert "equally supported" in row["WHY"]


def test_triangulation_counts_languages_not_candidate_producers(
        pivots_file, pivot_wordnets) -> None:
    """Spanish `gato` points at two ILIs, so three languages produce candidates for
    `miv` but only the winner's backers count. Counting producers instead is the
    mistake that cost precision in earlier work on this method."""
    senses, _ = m.read_dbnary_pivots(pivots_file, "WH", pivot_wordnets)
    # i-jack is reached by one language only and must not win
    assert senses[0].ili == "i-cat"


def test_triangulation_respects_the_dialect(pivots_file, pivot_wordnets) -> None:
    wh, _ = m.read_dbnary_pivots(pivots_file, "WH", pivot_wordnets)
    gm, _ = m.read_dbnary_pivots(pivots_file, "GM", pivot_wordnets)
    assert "phoo" not in {s.form for s in wh}
    # one language only, so GM decides nothing either
    assert gm == []


def test_triangulation_review_rows_show_the_pivot_words(
        pivots_file, pivot_wordnets) -> None:
    _, review = m.read_dbnary_pivots(pivots_file, "WH", pivot_wordnets)
    row = next(r for r in review if r["FORM"] == "abc")
    assert "fra=banque" in row["PIVOTS"] and "ita=riva" in row["PIVOTS"]
    assert row["VERDICT"] == ""


@pytest.mark.integration
def test_generated_lexicon_loads_into_wn(ontology_file: Path, tmp_path: Path) -> None:
    """Round-trip: the output must be loadable by the wn library itself."""
    import wn

    senses, hierarchy, entries = m.read_ontology(ontology_file)
    groups = m.build_synsets(senses)
    out = tmp_path / "out.xml"
    m.write_lmf(out, entries, groups, hierarchy,
                _meta(email="a@example.org", license="https://example.org/l"))

    data_dir = tmp_path / "wn_data"
    data_dir.mkdir()
    wn.config.data_directory = data_dir  # isolated: never touches the user's database
    wn.add(str(out), progress_handler=None)

    lexicon = wn.Wordnet(lexicon="test:0.1")
    assert len(lexicon.words()) == 6
    # one synset over the groups: the local stand-in for the concept `classifier`
    assert len(lexicon.synsets()) == len(groups) + 1
    assert lexicon.words("tsev kho mob")
    assert lexicon.words("tus", pos="x")


# --- route precedence and deduplication, as the reviews probed them ----------


def test_concepticon_id_beats_a_gloss_that_resolves_elsewhere() -> None:
    """The exact route must win even when the gloss would also have resolved.

    A hand-mapped concept set names the meaning; the English gloss beside it is
    one wording of that meaning and may be monosemous for something else. Running
    the gloss pass first silently preferred the weaker evidence.
    """
    sense = m.OntSense(0, "qav", ["frog"], "Animals", pos_override="n",
                       concepticon="100")
    english = FakeWordnet({("frog", "n"): [FakeSynset("i99", "noun.animal")]})
    m.link_senses([sense], english, True, False,
                  concepticon_by_id={"100": ("i42", "n")})
    assert (sense.ili, sense.method) == ("i42", "concepticon-id")


def test_triangulation_does_not_suppress_another_sense_of_one_form(
    tmp_path: Path,
) -> None:
    """Two Wiktionary senses of one form and one English lemma stay distinct.

    `txhab` translates `bank` under both the financial and the river-edge sense.
    Deciding one by triangulation says nothing about the other, so the exclusion
    key has to be the whole sense anchor, definition included.
    """
    path = tmp_path / "dbnary.tsv"
    path.write_text(
        "FORM\tDIALECT\tISO\tENGLISH\tPOS\tDEFINITION\n"
        "txhab\tWH\tmww\tbank\tnoun\ta financial institution for money\n"
        "txhab\tWH\tmww\tbank\tnoun\tthe sloping side of a river\n",
        encoding="utf8")
    english = FakeWordnet({("bank", "n"): [
        FakeSynset("i1", "noun.group", "a financial institution that accepts money"),
        FakeSynset("i2", "noun.object", "sloping land beside a body of water"),
    ]})
    decided = {("txhab", "bank", "a financial institution for money")}
    senses = m.read_dbnary(path, english, "WH", already=decided)
    assert [s.ili for s in senses] == ["i2"]
    assert senses[0].definition == "the sloping side of a river"


def test_record_ili_pos_reads_the_part_of_speech_from_english_wordnet() -> None:
    """The tie-break cannot depend on a Concepticon file happening to cover the ILI."""
    sense = m.OntSense(0, "kim", ["expensive"], "Property", pos_override="a")
    sense.ili = "i5"
    english = FakeWordnet({("expensive", "a"): [FakeSynset("i5", "adj.all", pos="a")]})
    table: dict[str, str] = {}
    saved, m.ILI_POS = m.ILI_POS, table
    try:
        assert m.record_ili_pos([sense], english) == 1
        assert table["i5"] == "a"
    finally:
        m.ILI_POS = saved


def test_dedupe_carries_relations_and_identifiers_across() -> None:
    """Whatever the discarded sense carried has to move to the survivor."""
    first = m.OntSense(0, "nus", ["brother"], "person")
    first.ili = "i1"
    second = m.OntSense(0, "nus", ["male sibling"], "Kinship", pos_override="n",
                        source="KINSHIP", kindiv="o;Fa;Sb;So",
                        functions=["kin"], classified_by=["tus"])
    second.ili = "i1"
    entry = m.Entry("nus", "n", senses=[first, second])
    assert m.dedupe_senses([entry]) == 1
    kept = entry.senses[0]
    assert kept.kindiv == "o;Fa;Sb;So"
    assert kept.functions == ["kin"] and kept.classified_by == ["tus"]
    assert "also in KINSHIP" in (kept.note or "")


def test_dedupe_keeps_the_stronger_linking_method() -> None:
    """The survivor is what the reports count, so it must not inherit the weaker
    route merely because that source came first in the file."""
    weak = m.OntSense(0, "cua", ["wind"], "phenomenon")
    weak.ili, weak.method = "i1", "monosemous"
    strong = m.OntSense(0, "cua", ["air"], "", pos_override="n",
                        source="triangulated")
    strong.ili, strong.method = "i1", "triangulated-7"
    entry = m.Entry("cua", "n", senses=[weak, strong])
    assert m.dedupe_senses([entry]) == 1
    kept = entry.senses[0]
    assert (kept.method, kept.source) == ("triangulated-7", "triangulated")


def test_merge_into_entries_keeps_the_two_dialects_apart() -> None:
    """WH is `mww` and GM is `hnj`: a homograph across them is two entries."""
    entries = [m.Entry("npua", "n", dialect="WH",
                       senses=[m.OntSense(0, "npua", ["pig"], "animal")])]
    extra = m.OntSense(0, "npua", ["pig"], "Animals", pos_override="n",
                       dialect="GM", source="TEST")
    assert m.merge_into_entries(entries, [extra]) == 1
    assert [e.dialect for e in entries] == ["WH", "GM"]


def test_write_review_replaces_a_stale_sheet_with_an_empty_one(tmp_path: Path) -> None:
    """An earlier run's annotation task must not survive as the current one."""
    path = tmp_path / "review.tsv"
    m.write_review(path, [{"VERDICT": "", "FORM": "qav", "WHY": "two candidates"}])
    assert "qav" in path.read_text(encoding="utf8")
    m.write_review(path, [])
    body = path.read_text(encoding="utf8")
    assert "qav" not in body and body.startswith("VERDICT")


# --- pinned wordnet releases -------------------------------------------------


def test_read_pin_file_ignores_comments_and_blanks(tmp_path: Path) -> None:
    path = tmp_path / "pivots.lock"
    path.write_text("# a comment\n\nomw-fr\t2.0\nomw-ja\t2.0\n", encoding="utf8")
    assert m.read_pin_file(path) == {"omw-fr": "2.0", "omw-ja": "2.0"}


def test_read_pin_file_is_empty_when_absent(tmp_path: Path) -> None:
    assert m.read_pin_file(tmp_path / "nothing.lock") == {}



if __name__ == "__main__":
    sys.exit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-q"]))
