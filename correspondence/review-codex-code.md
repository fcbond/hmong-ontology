<!-- Codex CLI 0.144.1, read-only sandbox, run 3 October 2026. The whole
     repository (code and data tables, not the external/ PDFs) was sent to
     OpenAI's API for this review. Prompt reproduced below. -->

# Codex review of the Hmong wordnet code

Requested review as a careful reviewer of research code would give it, with the
linking logic first.

<details>
<summary>Prompt</summary>

```
Review the Python in this repository as a careful reviewer of research code would:
hmong2lmf.py, add_classifiers.py, fetch_dbnary.py, load_pivots.py, facts.py and
test_hmong2lmf.py. Read README.md for what it is meant to do.

It builds a wordnet for Hmong from several sources and links senses to the
Collaborative Interlingual Index. Correctness of the LINKING LOGIC matters most: a
wrong interlingual link propagates into every wordnet that trusts the index.

Please focus on, in order:

1. Correctness bugs in the linking and merging logic. In particular:
   - read_dbnary_pivots: the triangulation decision rule. It requires >= 2 languages
     backing the WINNING ILI and strictly more than the runner-up. Is that what the
     code does? Are there ways a single language's multiple senses inflate support?
   - dedupe_senses: two passes, within an entry and across entries. Can it lose a
     sense that should have been kept, or keep a duplicate?
   - link_senses: it skips senses that already have an ILI. Is that skip complete,
     and is the ordering of routes in main() consistent with the precedence the
     docstrings claim?
   - merge_into_entries and the (form, pos) keying.
2. Anything where the code's behaviour contradicts its own docstring or the README.
3. Silent failure modes: places where a missing file, an unloaded lexicon, or an
   unexpected column yields a quietly wrong result rather than an error.
4. Test gaps: which of the above is untested, and which tests assert something
   weaker than they appear to.
5. Reproducibility: facts.py is supposed to recompute every figure the paper cites.
   Does it compute them the same way the main pipeline does?

Be concrete: name the file and line, say what input triggers the problem, and say
what the consequence is. Do not rewrite the code. Rank findings by severity and say
plainly if you think something is fine.
```

</details>

---

## Findings

### Critical

1. Exact Concepticon IDs do not actually take precedence over gloss lookup  
   [hmong2lmf.py:829](/home/bond/git/hmong-ontology/hmong2lmf.py:829), [hmong2lmf.py:904](/home/bond/git/hmong-ontology/hmong2lmf.py:904), [hmong2lmf.py:925](/home/bond/git/hmong-ontology/hmong2lmf.py:925)

   `link_senses()` performs English gloss linking first and only runs `link_by_concepticon()` afterward. The latter skips every sense that already received an ILI.

   Trigger: a CLDF sense has a manually assigned Concepticon ID mapping to `i-A`, but its English gloss is monosemous or resolves by intersection to `i-B`.

   Consequence: the converter keeps `i-B`, even though the README says CLDF senses “reach the ILI through the concept set directly — no gloss lookup,” and `link_by_concepticon()` calls the ID route exact. This can create a wrong interlingual link from weaker evidence.

   The test at [test_hmong2lmf.py:552](/home/bond/git/hmong-ontology/test_hmong2lmf.py:552) uses a “nonsense gloss” with no English candidates, so it does not exercise the precedence conflict. The test at line 489 explicitly codifies English-over-Concepticon precedence for gloss-based Concepticon links, but there is no corresponding conflict test for exact Concepticon IDs.

2. Triangulation suppresses distinct DBnary senses sharing the same form and English lemma  
   [hmong2lmf.py:1291](/home/bond/git/hmong-ontology/hmong2lmf.py:1291), [hmong2lmf.py:1301](/home/bond/git/hmong-ontology/hmong2lmf.py:1301), [hmong2lmf.py:400](/home/bond/git/hmong-ontology/hmong2lmf.py:400)

   The precedence key is only `(normalised Hmong form, English lemma)`. It omits the Wiktionary definition, even though that definition is the sense anchor and is included in the triangulation grouping key.

   Trigger: Hmong form `X` translates English `bank` under both the financial and river-edge Wiktionary senses. Triangulation resolves one of them; definition comparison could resolve the other.

   Consequence: resolving either sense by triangulation causes `read_dbnary()` to skip every DBnary row for `X` + `bank`, losing the other legitimate sense. This is not merely route precedence; it conflates the very Wiktionary senses the code says must remain distinct.

   No test covers two definitions with the same `(form, English lemma)`.

### High

3. Cross-entry deduplication does not reliably keep the sense whose POS matches the ILI  
   [hmong2lmf.py:651](/home/bond/git/hmong-ontology/hmong2lmf.py:651), [hmong2lmf.py:660](/home/bond/git/hmong-ontology/hmong2lmf.py:660), [hmong2lmf.py:751](/home/bond/git/hmong-ontology/hmong2lmf.py:751)

   The documented rule depends on global `ILI_POS`, but that table is populated only while reading a Concepticon mapping. If no Concepticon file is supplied, or the particular ILI is absent from it, the sort expression makes every candidate equally preferred and keeps input order.

   Trigger: an ontology stative verb and an adjective from another source resolve to the same adjective ILI, without that ILI appearing in the loaded Concepticon table.

   Consequence: the verb entry will normally survive because ontology entries precede added entries, contradicting the docstring and README claim that the ILI’s own POS is retained. The same issue affects triangulated and DBnary links even though their source wordnets know the POS.

   The test at [test_hmong2lmf.py:608](/home/bond/git/hmong-ontology/test_hmong2lmf.py:608) manually sets `m.ILI_POS["i5"]`, so it proves only the populated-cache case and masks the missing-data behavior. It also leaves global state behind for later tests.

4. Deduplication loses semantic and provenance fields despite claiming “nothing is lost”  
   [hmong2lmf.py:612](/home/bond/git/hmong-ontology/hmong2lmf.py:612), [hmong2lmf.py:641](/home/bond/git/hmong-ontology/hmong2lmf.py:641), [hmong2lmf.py:663](/home/bond/git/hmong-ontology/hmong2lmf.py:663)

   Both passes merge only glosses and a synthesized note. They do not merge `functions`, `classifies`, `classified_by`, `kindiv`, `concepticon`, candidate information, or structured `source`. The within-entry pass retains the first sense’s `method` and `source`, regardless of evidence strength.

   Trigger: duplicate senses from two sources share an ILI, but one carries a KinDiv identifier, classifier relation, borrowing judgment/provenance, or a stronger linking method.

   Consequence: relations or identifiers can disappear from the generated LMF. Source contribution and method statistics can also be wrong: because ontology senses are generally first, a triangulated/DBnary/CLDF duplicate is removed and counted as the ontology’s weaker method. Adding “also in SOURCE” to free text does not preserve `dc:source`.

   The within-entry dedupe test checks only glosses. The cross-entry test checks only gloss/POS/note. No test checks the other fields or evidence method.

5. `(form, POS)` entry keys merge dialects  
   [hmong2lmf.py:264](/home/bond/git/hmong-ontology/hmong2lmf.py:264), [hmong2lmf.py:331](/home/bond/git/hmong-ontology/hmong2lmf.py:331), [hmong2lmf.py:593](/home/bond/git/hmong-ontology/hmong2lmf.py:593)

   Both ontology parsing and `merge_into_entries()` omit dialect from the key.

   Trigger: `--dialect all`, or an added sense carrying a different dialect from an existing homographic `(form, POS)` entry.

   Consequence: White Hmong and Green Mong senses share one lexical entry whose `dialect` is whichever was encountered first. The second-pass dedupe can then collapse cross-language senses on `(form, ILI)`. This contradicts the code’s own explanation that they are separate ISO 639-3 languages.

   Existing merge tests use only one dialect.

### Medium

6. Partial pivot installations quietly change the decision rule  
   [hmong2lmf.py:562](/home/bond/git/hmong-ontology/hmong2lmf.py:562), [hmong2lmf.py:577](/home/bond/git/hmong-ontology/hmong2lmf.py:577), [hmong2lmf.py:1293](/home/bond/git/hmong-ontology/hmong2lmf.py:1293)

   Missing pivot lexicons are merely noted and ignored; the main command fails only when none are loaded.

   Trigger: 5 of 28 pivot wordnets are missing, including languages supporting a competing ILI.

   Consequence: a former 2–2 tie may become 2–1 and be accepted, or a valid winner may fall below two votes. Thus an incomplete local installation can silently alter interlingual links rather than merely reduce coverage. For research linking, a warning is too weak unless incompleteness is deliberately requested and recorded.

   `load_pivots.py` similarly catches all load errors and returns success even when lexicons fail to load at [load_pivots.py:78](/home/bond/git/hmong-ontology/load_pivots.py:78).

7. Undecided triangulation groups with no loaded candidates disappear from review  
   [hmong2lmf.py:523](/home/bond/git/hmong-ontology/hmong2lmf.py:523)

   The docstring says it returns a review row “for every group it could not” link, but a group with no `backers` is silently skipped.

   Trigger: its pivot lexicons are missing, its words have no synsets, or all matching synsets lack ILIs.

   Consequence: the reported undecided count is too low, and investigators cannot distinguish “no evidence” from a group never processed.

8. A single language cannot inflate support numerically, but ambiguous senses can create misleading apparent agreement  
   [hmong2lmf.py:511](/home/bond/git/hmong-ontology/hmong2lmf.py:511), [hmong2lmf.py:520](/home/bond/git/hmong-ontology/hmong2lmf.py:520)

   The requested support rule itself is correct: `backers[ili]` is a set of ISO codes, so multiple words or multiple synsets from one language contribute at most one vote to a given ILI. The winner must have `>= 2` languages and strictly more than the runner-up.

   However, every sense of an ambiguous pivot word votes. For example, French backs `{i1,i2}` and Italian backs `{i1,i3}`; `i1` wins 2–1–1 even though neither lexical item uniquely identifies it. This is set intersection-style evidence and may be acceptable, but it is weaker than the prose’s suggestion that lexicographers independently “put” each word in the winning synset. There is no test documenting or evaluating this case.

9. Fetching zero rows can either crash or leave stale output  
   [fetch_dbnary.py:138](/home/bond/git/hmong-ontology/fetch_dbnary.py:138), [fetch_dbnary.py:180](/home/bond/git/hmong-ontology/fetch_dbnary.py:180), [fetch_dbnary.py:196](/home/bond/git/hmong-ontology/fetch_dbnary.py:196)

   `write_tsv()` indexes `rows[0]`, so zero Hmong results raises `IndexError`. Conversely, zero pivot results cause no write at all.

   Consequence: an existing `dbnary-pivots.tsv` remains in place and can be mistaken for the new fetch, a particularly dangerous stale-data failure for reproducibility.

10. Empty review output also leaves a stale review file  
    [hmong2lmf.py:448](/home/bond/git/hmong-ontology/hmong2lmf.py:448)

    `write_review()` returns without touching the requested file when there are no rows. A review file from an earlier run therefore continues to look current.

11. `add_classifiers` treats same-form/same-category as fully merged  
    [add_classifiers.py:152](/home/bond/git/hmong-ontology/add_classifiers.py:152), [add_classifiers.py:195](/home/bond/git/hmong-ontology/add_classifiers.py:195)

    `has_sense()` tests only category. If an existing sense has that category but lacks a row’s functions, examples, definition, or source note, the entire row is skipped.

    Consequence: rerunning on a partially enriched ontology does not actually fold in missing information, despite the script being presented as a merge operation. There is no test for partial existing senses.

## `facts.py` reproducibility problems

- Its default English WordNet is `oewn:2025`, while the main converter defaults to `oewn:2024`: [facts.py:47](/home/bond/git/hmong-ontology/facts.py:47), [hmong2lmf.py:1204](/home/bond/git/hmong-ontology/hmong2lmf.py:1204). Running both with defaults does not measure the same pipeline.
- It always enables Morphy, category filtering, and stative-adjective linking, without recording those settings.
- It inherits partial-pivot behavior, so the figures depend on which wordnets happen to be installed.
- Source tables other than the main arguments are opened relative to the current working directory at [facts.py:63](/home/bond/git/hmong-ontology/facts.py:63), not relative to the repository or ontology.
- Pivot summary groups use `(FORM, DEFINITION)` at [facts.py:108](/home/bond/git/hmong-ontology/facts.py:108), whereas the actual linker groups by `(FORM, ENGLISH, DEFINITION)`. Its “groups” and median can therefore combine groups that the pipeline keeps separate.
- The claimed independent Concepticon/triangulation comparison is not fully independent: `tri_only` calls `run(concepticon=True, pivot=True)` at [facts.py:195](/home/bond/git/hmong-ontology/facts.py:195), and deduplication may remove the triangulated sense in favor of the earlier ontology sense. This can omit comparable pairs and bias agreement upward or downward.
- Contribution figures rely on the surviving sense’s structured `source`, so the dedupe provenance loss described above directly affects paper figures.

## What appears correct

- The core triangulation threshold and strict runner-up rule are correct.
- Multiple senses or words from one pivot language do not inflate that language above one vote per ILI.
- `link_senses()` completely skips senses already carrying an ILI for its English-gloss pass.
- The pipeline intentionally orders triangulation before DBnary and passes an exclusion set to DBnary. The implementation problem is the overly broad exclusion key, not the basic ordering.
- Within a single entry, two linked senses with different ILIs remain distinct.
- After deduplication, `main()` rebuilds the flat sense list before constructing synsets, so removed senses do not retain orphan synsets.

I could not execute the suite because `pytest` is not installed in the environment (`ModuleNotFoundError: pytest`). The review above is therefore based on source tracing rather than a successful test run.
