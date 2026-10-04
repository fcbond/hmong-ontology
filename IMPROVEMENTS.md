# What would improve this resource, in order of value

Every figure below is measured, not estimated, and was recomputed on 2026-10-04
after the switch to the `oewn:2025+` edition. `facts.py` produces all of them, and records the
settings they depend on alongside them:

```sh
uv run facts.py --data-directory .wn_data --english oewn:2025+ \
    --concepticon ../cldf2wn/data/concepticon-ili.tsv \
    --cldf ../wold/cldf:WhiteHmong:WOLD:WH --pristine pristine.xml
```

The `--report` TSV has one row per sense, with the method that linked it or the
reason it did not, and for every unlinked sense the candidate ILIs with the English
definition of each.

## Where it stands

The ontology has gone from 1,263 lemmas and 1,404 senses to **1,565 and 1,785**,
and Green Mong from nothing to **96 lemmas**. For White Hmong:

| | linkable | linked | | distinct ILIs |
|---|---|---|---|---|
| English WordNet lookup alone | 1,545 | 540 | 35.0% | 497 |
| + the Concepticon bridge | 1,543 | 854 | 55.3% | 748 |
| + WOLD | 2,736 | 1,735 | 63.4% | 1,358 |
| + triangulation | 3,084 | 2,083 | 67.5% | 1,582 |
| + Wiktionary definition overlap | 3,095 | **2,094** | **67.7%** | **1,592** |

Of those 1,592 concepts, 494 come from the descriptive sources, 1,019 from WOLD (845
of them reached by no other source), 344 from triangulation (313 likewise), and 11
from the Wiktionary definition comparison (10 likewise). A further **34 senses carry
a KinDiv kin-type identifier** for concepts the interlingual index has no entry for
at all.

What each link rests on: **1,710** senses on a hand-mapped concept set, two glosses
intersecting, or several languages agreeing; **384** on a single monosemous gloss,
labelled as the weaker evidence it is; **1,001** open; **141** classifiers with no
ILI by design.

The English wordnet is **`oewn:2025+`**, the edition that includes proper names.
The plain `oewn:2025` links four more senses by gloss alone but leaves two
Concepticon mappings dangling, `moon` and `sun` being proper-name concepts; see
"Fixed after external review" below.

Green Mong: 25 of 37 linkable senses, 15 distinct ILIs. It had zero of everything
until the classifier, kinship and triangulation work.

## Done

These were the top items; they are kept because the measurements explain the
result and because the mechanisms now serve further sources.

### (0) WOLD's White Hmong vocabulary — +611 concepts, open licence

The World Loanword Database's White Hmong vocabulary, compiled by Martha Ratliff,
is **CC BY 4.0**, distributed as CLDF (`lexibank/wold`), and already mapped to
Concepticon — so the bridge applies to it unchanged, with no new machinery.

`hmong2lmf.py --cldf DIR:LANGUAGE:NAME` is general to any Lexibank-style wordlist,
not specific to WOLD, which is what makes it worth having here. It contributes 1,474
senses, 837 on forms the lexicon did not have, and **611 concepts nothing else
reaches**. 905 of its senses link by Concepticon concept set alone, needing no gloss
lookup and so no disambiguation at all.

It also cross-checks our own linking: of the ILIs both reach, about two thirds share
a Hmong form, and the disagreements are granularity (ours `av`, WOLD `av nkos`)
rather than error.

**`chenhmongmien` needs no new code**: 25 Hmong-Mien varieties, 799 Concepticon
sets, CC BY 4.0, covering the Guizhou varieties `hea`, `hmd`, `mmr`, `cqd`. One
lexicon per language, since they are separate ISO codes.

### (0b) Wiktionary through DBnary — +145 concepts, and Green Mong's first links

Hmong is not a Wiktionary edition, so it appears only as a translation target — but
the English edition's translation tables are **sense-anchored**, and
[DBnary](http://kaiko.getalp.org/dbnary) publishes them as RDF with a SPARQL
endpoint. No scraping, and a citable release. `fetch_dbnary.py` writes
`dbnary-hmong.tsv`; `--dbnary` reads it.

| | |
|---|---|
| sense-anchored translations available | 732 `mww`, 29 `hnj` |
| resolved to a synset | 274 WH, 9 GM |
| distinct ILIs contributed | 165 WH, 5 GM |
| **not already in the ontology** | **145 WH, 5 GM** |

**The Green Mong five matter out of proportion to their number.** `hnj` had *no*
interlingual links, because every one of its senses was a classifier and those carry
no ILI by design. It now has `teg` 'hand', `kas fes` 'coffee', `Meev Teem` 'Myanmar',
`Amelika` 'United States', `Moob` 'Hmong' — the difference between a lexicon that
cannot be queried interlingually at all and one that can.

Two things to know:

- **DBnary stores the target language as a lexvo URI, not a bare code.** A query
  filtering on `"mww"` returns nothing, so it is easy to conclude there is no Hmong
  in DBnary. Filter on
  `dbnary:targetLanguage <http://lexvo.org/id/iso639-3/mww>`. An earlier draft of
  `RESOURCES.md` wrote DBnary off on exactly that mistake.
- The disambiguation is a **tuned heuristic** and the weakest link in the pipeline.
  Wiktionary's sense numbers cannot be mapped to WordNet's, so the converter
  compares definitions by content-word overlap and accepts only a clear winner. It
  declines far more than it accepts, which is the right trade but leaves work on the
  table — see (1b).

### (4) Definitions for the undescribed classifiers — closed

This is now **fully closed**, and the way it closed is worth recording. The stopword
list turned out to be an index into chapter 7 of White (2021) — its headings
"locational classifiers" and "verb classifiers" are his categories, which Bisang has
no counterpart for — so the forms it listed without a description are described
there. The inventory went from 137 to **235** rows.

Of the 12 rows that still carry no definition, **none is added as a classifier**:
six are tone-melody alternants and become `<variant>` of the form they alternate
with, and six are forms no source supports as classifiers at all. **Every classifier
sense in the ontology now has a definition.**

`CHECK: Nathan` on `cev`, and on whether `khaw` and White's `khawv` 'CL:BITE'
(p. 337, occurring once and never discussed) are one form or two.

### (7) The rest of White's thesis — two of four parts

- **Tables 39–41, pp. 381–382.** `underspecified.tsv`: 14 classifier-specified
  compounds over three underspecified nouns, all 14 new. The one place a classifier
  does not agree with a noun but decides what the phrase denotes — `phau ntawv`
  book, `tsab ntawv` letter, `kab ntawv` sentence, from one noun — so each is a
  distinct sense and each populates a `classified_by` relation.
  `CHECK: Nathan` on `nqe lus` 'list', where CL:PARAGRAPH and the gloss do not
  obviously agree.
- **Table 29, p. 288.** `kinship.tsv`: 37 senses over both dialects, **16 with a
  distinct Green Mong form** — the best source of Green Mong content vocabulary we
  have. See (3) for the KinDiv mapping.

## Still to do

### (1) A second gloss for the ambiguous senses — up to +406

**416** senses failed only because their gloss is ambiguous, and **406 have exactly
one gloss**. The converter links a sense when two glosses' candidate sets intersect
in one ILI; a single gloss can only link if it happens to be monosemous. So one more
gloss converts a near-miss into a link, with no new machinery.

**145 have only two candidate ILIs**, each with its English definition already in the
report. That is a binary choice per sense, and settling them takes coverage to
**72.3%**.

This is lexicographic work, not engineering, and it is work the ontology's author or
any fluent speaker can do directly in `hmong_ontology.xml` — add a second
`<meaning>`.

### (1b) The declined candidates and the route conflicts — a speaker's afternoon

Three sheets, in increasing order of yield per row:

- `review-wiktionary-WH.tsv`, **35 rows**: translations the definition comparison
  would not decide, with up to five candidate ILIs, their English definitions and
  the overlap scores.
- `review-triangulation-WH.tsv`, **71 rows**: groups where the pivot languages
  split, with every pivot word grouped by language, so a speaker can see that French
  and Italian point one way and Chinese and Japanese the other.
- `review-conflicts-WH.tsv`, **28 rows**: senses the Concepticon and triangulation
  routes both reach and name different ILIs for. One of the two is wrong, so this is
  where a correction is most likely per row. It also carries our own provisional
  reading in an `ADJUDICATION` column, kept separate from the empty `VERDICT` so a
  non-speaker's judgement is never mistaken for a speaker's.

These are not failures so much as deferred decisions, and they are the cheapest
source of new links in this file: the candidates are already assembled and glossed.

### (2) A gloss in another language

A second gloss need not be English. The pivot is the ILI, so a French, Chinese or
Thai gloss is worth as much, which matters because the standard Hmong dictionaries
are not English.

**The French route got worse on inspection.** PanLex publishes under
**CC BY-NC-SA 4.0**, not CC0 — the Zenodo record's `cc-zero` tag covers the RDF
conversion, and its description says licensing follows the original data. Worse, the
Freelang Hmong–French word list it carries has terms vesting the list in its compiler
and **forbidding format conversion and redistribution**. Aggregation laundered
nothing. The counts were also overstated: 3,042 hmong→fra and 2,872 fra→hmong, not
7,580/7,476.

The better French target is **Bertrais-Charrier (1979)**, about 30,000 lines over 584
pages, in copyright but with a single identifiable rights holder — a permission
problem rather than an impossible one, and the dictionary Bisang leans on throughout.

`omw-fr` (WOLF) and `omw-cmn` are ILI-linked and already in the sibling Cygnet
checkout. Cygnet's `wordnets.toml` also pulls the TUFS basic-vocabulary
dictionaries, adding **Vietnamese, Lao, Thai, Khmer and Burmese** — every country
with a large Hmong population. Those are small, so they confirm links rather than
discover them, but confirmation is what (1) needs.

### (3) Concepts the interlingual index does not have

**204** senses have a gloss English WordNet does not have as a lemma, and **193 of
those glosses are multi-word**: `ciav` 'bamboo aqueduct', `qhov ntswg` 'nose bridge',
`cuab yeem` 'household equipment'. These are not failures of the method; they are
concepts the index lacks, and the right response is to propose them — which makes
the resource a contributor to CILI rather than only a consumer.

**Kinship is the part already solved, and not by proposing.** English does not
lexicalise most of the distinctions Hmong obligatorily makes, so 21 of the 37
kinship senses have no English WordNet lemma. But
[KinDiv](https://github.com/kinship-diversity/KinDiv) — 198 concepts as Murdock kin
types, 1,904 words in 168 languages, 37,370 recorded gaps — already has those
concepts, with an identifier (`Fa;El;Br`) stable across languages **where CILI does
not reach**. `kinship-kindiv.tsv` maps **28** of our senses onto them, 24 exactly. The converter
emits `dc:identifier="KinDiv:Fa;El;Br"` on the synset.

KinDiv's `wn/extra-concepts.tsv` has since added parents, children, spouses and
in-laws, which brought eight more Hmong terms into scope — `niam` 'mother', `txiv`
'father' and 'husband', `tub` 'son', `ntxhais` 'daughter', `poj niam` 'wife', `nyab`
'daughter-in-law', `vauv` 'son-in-law'.

**Four senses need concepts KinDiv does not yet have**, and they are the interesting
ones. Hmong `nus`, `muam`, `tij laug` and `kwv` name the child of a father's sibling
*regardless of whether that sibling is a brother or a sister*, while distinguishing
the speaker's sex and, for the last two, relative age. KinDiv has `Fa;Sb;So` and
`Fa;Sb;Da` in its relations graph as bridging nodes but does not declare them as
concepts, and has no speaker-sex or age-marked variants at all. So these are not
mapping failures: they are concepts KinDiv should have, with Hmong as the evidence
that a language lexicalises them. `kindiv-proposals.tsv` has the six rows to add, in
KinDiv's own format, with their hypernym relations and the Hmong words, all verified
to resolve against KinDiv's existing concepts.

Still unmapped and still needing a concept from somewhere: `yawg koob` 'ancestor',
and the coordinate compounds `kwv tij` 'brothers, patrilineal relatives' and `neej
tsa` 'in-laws, matrilineal relatives'. Those last two are the genuinely novel
concepts — a set of relatives defined by descent line rather than by a path from
ego — and no kinship resource we have looked at has them.

**KinDiv has no Hmong at all**, so this runs both ways: it gives our terms a
comparable identifier, and gives KinDiv a language it lacks. Contributing the Hmong
rows back is the obvious next step, and cheap.

`CHECK: Nathan` on the four cousin rows: confirm that Hmong `nus`, `muam`, `tij
laug` and `kwv` really are indifferent to whether the father's sibling is a brother
or a sister. If they are not, the four collapse onto KinDiv's existing `Fa;Br;*` and
`Fa;Ss;*` concepts and no proposal is needed.

### (5) Seven Concepticon part-of-speech disagreements

Seven unlinked senses have a gloss that *is* a Concepticon concept set, rejected only
because the part of speech disagrees — the familiar verb/adjective and verb/noun
pairings of a language with adjectival verbs:

| form | gloss | ours | Concepticon | ILI |
|---|---|---|---|---|
| `ziab` | dry | v | a | i14155 |
| `foom` | curse | n | v | i25957 |
| `tis` | name | v | n | i69761 |
| `tu` | clean | v | a | i2367 |
| `cub` | steam | v | n | i116291 |
| `qhuas` | praise | v | n | i71660 |
| `sau` | harvest | v | n | i105478 |

Allowing a cross-part-of-speech link is a judgement call, not a bug fix, so it is
listed rather than done. Seven is small, but each is certainly correct in meaning.

CHECK: Nathan

### (6) Green Mong — 96 lemmas is better, still not a lexicon

Green Mong is a separate ISO 639-3 language (`hnj`) with roughly as many speakers as
White Hmong. It has gone from 0 lemmas to 20 (White's chapter 7), then 84, then **96**
(his kinship table), and from 0 interlingual links to 9 ILIs and 10 KinDiv concepts.

That is still mostly function words plus kinship. The fix is in hand but blocked on
permission: **Strecker's (2021) *Mong Leng – English Dictionary*** (`RESOURCES.md`
X1), 995 pages, **4,442 sense entries over 3,539 head forms**, in standard RPA so its
forms match ours with no conversion. A crude first-pass parse already links **1,369
senses to 849 distinct ILIs**. Its per-entry classifier annotations would populate
`classifies` at the same time.

The dictionary states no licence, so it needs Strecker's permission. Useful lever:
its own acknowledgements thank Nathan White.

CHECK: Nathan

### (7b) The two unmined parts of White's thesis

- **§6.7, p. 298** — the noun subgroup scheme (mass/count, common/proper,
  alienable/inalienable, animate/inanimate). A ready skeleton for aligning the
  ontology's categories to wordnet lexicographer files, which `hmong2lmf.py`
  currently does with a hand-written table.
- **§3.2.4.1, pp. 100–103** — the class-term prefix inventory (`pob-` CT:ROUND,
  `txiv-` CT:FRUIT, `tub-` CT:PERSON, `kab-` CT:INSECT, `qhov-` CT:HOLE, `ko-`
  CT:LOWER.EXTREMITY, and more). Derivational, so it predicts compounds the lexicon
  does not list — a different kind of gain from everything else here, and the only
  one that could grow the lexicon without a new source.

### (8) A speaker-judged sample, stratified across the evidence tiers

The one measurement nothing here provides. We report agreement between automatic
routes, which is not accuracy, and the tier labels in the table above order the
evidence without estimating an error rate for any tier. Thirty senses drawn from
each of the three states — concept set or intersection, triangulated, single
monosemous gloss — judged right or wrong by a speaker, would turn the whole
confidence story from a policy into a result. It is a few hours of one person's
time and it is the highest-value item in this file.

## Fixed after external review

Also, after a review of reproducibility: the pivot wordnet **releases** are now
pinned to Cygnet's `wordnets.toml` through `etc/pivots.lock`, and the converter
refuses a lexicon at any other version, because triangulation counts languages and
a wordnet at a different release can move a vote. `cite_wordnets.py` generates the
citation and licence of each from the loaded lexicons. `build.sh` resolves the pins
itself, so the released lexicon, the figures and the credits all describe one build.

- **Three Concepticon mappings reported as naming a non-existent ILI. Two of them
  were ours.** `i21944` bathe, `i85806` moon and `i86272` sun are all *current,
  non-superseded* concepts in CILI, so the mapping was never at fault. `moon` is
  `the natural satellite of the Earth` and `sun` `the star that is the source of
  light and heat...`: the proper-noun readings. OEWN 2025 ships in two editions and
  the proper names are in only one of them, so these two resolved or dangled
  according to which file was on disk. We now link against **`oewn:2025+`**, which
  carries both, at a cost of four gloss-only links — 13,000 extra name synsets make
  a few monosemous glosses ambiguous. `bathe` is the real defect and survives the
  change: OEWN carries `cleanse the entire body` under `i21956`, so the concept is
  there and the identifier has moved. The lesson is that English WordNet is not the
  authority on which ILIs exist; `facts.py` now consults a CILI release
  (`--cili`) and classifies each absence instead of calling it a defect.


Two independent code and paper reviews (`correspondence/`) found route-precedence
and measurement defects that changed published figures. Recorded because each was
invisible in a passing test suite:

- **The exact Concepticon-id route ran after the gloss pass**, so a hand-mapped
  concept set could be overruled by a gloss that happened to resolve elsewhere —
  the opposite of the documented precedence. Fixed: it now runs first. WOLD's
  identifier links went from 665 to **1,149**.
- **The triangulation→Wiktionary exclusion key was `(form, English lemma)`**,
  dropping the Wiktionary definition that anchors the sense, so deciding one sense
  of `bank` suppressed the other. Fixed to the full anchor.
- **`ILI_POS` was filled only from the Concepticon file**, so the deduplication
  tie-break that is supposed to keep the reading matching the ILI's part of speech
  silently fell back to input order for most ILIs. Now read from English WordNet.
- **Deduplication merged only glosses and a note**, dropping the loser's KinDiv
  identifier, classifier relations, Concepticon id and provenance, and keeping
  whichever linking method came first in the file rather than the stronger one —
  which misattributed triangulated links to weaker routes in the contribution
  figures. `absorb()` now moves everything across and keeps the stronger method.
- **`--cldf` stamped the wordlist with the dialect being built**, so a `--dialect
  GM` run put 1,474 White Hmong forms into the Green Mong lexicon. The dialect is
  now a field of the `--cldf` spec and a mismatched wordlist is skipped.
- **Entry keys omitted the dialect**, so a homograph across the two could share one
  entry whose language was whichever came first.
- **The route comparison was measured after deduplication**, which merges the two
  routes' senses wherever they agree and labels the survivor with the stronger
  route. That left the comparison seeing the disagreements and almost none of the
  agreements: the reported result was 0 of 16 agreeing. Measured correctly, before
  deduplication, it is **162 of 190 (85.3%)**. The published claim was wrong and the
  corrected figure is the paper's one cross-route validation.
- **`build.sh` ran neither triangulation nor the Wiktionary route**, so the released
  lexicon was not the one the figures described, and defaulted to a different
  English release than `facts.py`. Both now take the full pipeline and
  `oewn:2025+`.
- Smaller: a zero-row fetch raised `IndexError` or left a stale TSV in place; an
  empty review left the previous run's sheet looking current; a triangulation group
  with no loaded candidates vanished from the queue instead of being reported as
  undecided; `add_classifiers.py` skipped a row whose sense existed but lacked its
  definition or examples; a missing pivot wordnet changed which ILI wins and was
  only a warning, now an error unless `--allow-missing-pivots`.

## Measured and rejected

- **Merging kaikki.org's White Hmong glosses to disambiguate our senses.** 815
  lemmas and 1,400 senses under CC BY-SA, which looked like the cheapest route to the
  second gloss (1) needs. Matching by form and part of speech adds a gloss to 118
  unlinked senses, 111 of them ambiguous, but the link gain is **+7 net** — 9 gained,
  2 lost, 6 previously-linked senses changed ILI. kaikki's senses are separate senses
  of the same form, not further glosses of ours, so pooling them conflates
  homographs: `muag` is 'be soft' here and 'to sell' there, and the intersection goes
  empty rather than decisive. A second gloss helps only when it glosses the same
  sense. Recorded because it is an attractive mistake. The sense-anchored DBnary
  route (0b) is the same data used correctly.
- **Extending the "be X" → English adjective fallback beyond `verb.stative`.** Nine
  unlinked senses outside that category have a `be X` gloss, of which **two** would
  link. Not worth the precision.
- **Head-word backoff for multi-word glosses** — linking `nose bridge` to *bridge*
  because the last word matches. Would add many links and every one would be wrong.
  These belong in (3) as new concepts.
- **Treating underscored glosses specially.** The converter already maps underscore
  to space; the underscores are not the problem, the phrases are.

## Summary

| | concepts | coverage |
|---|---|---|
| now | 1,592 ILIs + 34 KinDiv | 67.7% of linkable senses |
| (1) a second gloss for the 145 two-candidate senses | +145 senses | 72.3% |
| (1b) the 134 rows across the three review sheets | +up to 134 senses | |
| (3) proposing the 238 unknown concepts | +238 | |
| (6) Strecker's dictionary, with permission | ~849 ILIs for Green Mong | |
| (8) a speaker-judged stratified sample | — | the missing evaluation |

(1), (1b), (6) and (8) need no new software. (3) needs a proposal process. (6) needs
an email.
