# hmong-ontology

A semantic ontology resource for the Hmong language, inspired by WordNet (Fellbaum, 1998).

This resource is intended for data science and natural language processing purposes, such as computational modeling of semantics or cleaning of raw data for deep learning.

It is also, now, a wordnet. `hmong2lmf.py` converts the ontology to WN-LMF 1.4 and
links its senses to the Collaborative Interlingual Index by six routes, so that a
Hmong word and an English or Chinese or Thai one reach each other through a shared
concept: **2,094 of 3,095 White Hmong senses are linked, over 1,592 concepts.** The
material that makes that possible — a classifier inventory, a kinship paradigm and
a set of classifier-specified compounds, read out of two descriptive publications —
is in the TSV files below, as editable data rather than as generated output.

What a link rests on is recorded on the synset, and what is still undecided ships as
three annotation sheets rather than being guessed. `IMPROVEMENTS.md` says what would
improve the resource and what each improvement is worth, measured; `facts.json`
holds every figure, with the settings it depends on. Nothing here has been checked
by a fluent speaker yet, which is the largest single gap.

## Licence

The data in this repository is released under [Creative Commons Attribution 4.0
International](https://creativecommons.org/licenses/by/4.0/) (see `LICENSE`).
Please cite the repository when you use it.

## Files

| File | What it is |
|---|---|
| `hmong_ontology.xml` | the lexemes (nouns, verbs and classifiers), their senses and their semantic categories |
| `classifiers.tsv` | the numeral classifier and quantifier inventory, with class, definition, example nouns and a source for each |
| `classifiers-white2021.tsv` | the unmerged extraction from chapter 7 of White (2021c) |
| `class_nouns.tsv` | class nouns and their member compounds, with English glosses |
| `underspecified.tsv` | the 14 classifier-specified compounds of White's Tables 39–41 |
| `kinship.tsv` | kinship terms from White's Table 29, both dialects |
| `kinship-kindiv.tsv` | those terms mapped to KinDiv kin-type concepts |
| `kindiv-proposals.tsv` | concepts to add to KinDiv, with Hmong as the evidence |
| `dbnary-hmong.tsv` | sense-anchored Wiktionary translations, via DBnary |
| `dbnary-pivots.tsv` | the other languages' translations of those same senses, for triangulation |
| `stopwords_base.txt` | Hmong stopwords, excluding classifiers and verbal bound roots/affixes |
| `stopwords_classifiers.txt` | Hmong classifiers |
| `stopwords_verbal_adjuncts.txt` | Hmong verbal adjuncts, such as bound roots and affixes |

Three annotation sheets, each a question for a speaker with the candidates already
assembled and glossed. `VERDICT` is theirs to fill in; where a column named
`ADJUDICATION` is present it holds a reading by someone who does not speak the
language, marked as such.

| File | Rows | What is undecided |
|---|---|---|
| `review-conflicts-*.tsv` | 28 | two routes reached the sense and named different ILIs |
| `review-triangulation-*.tsv` | 71 | the pivot languages split |
| `review-wiktionary-*.tsv` | 35 | the definition comparison found no clear winner |

Scripts, in the order they are run:

| File | What it does |
|---|---|
| `fetch_dbnary.py` | queries DBnary's SPARQL endpoint for the two Wiktionary tables |
| `load_pivots.py` | loads the pivot wordnets at their pinned releases into `.wn_data`, and writes `etc/pivots.lock` |
| `add_classifiers.py` | folds the extracted tables into `hmong_ontology.xml`; idempotent |
| `hmong2lmf.py` | converts the ontology to WN-LMF 1.4, linking senses to the Interlingual Index |
| `conflicts.py` | writes the senses two linking routes disagree about |
| `cite_wordnets.py` | the citation, licence and version of every wordnet used |
| `facts.py` | recomputes every figure the paper cites, into `facts.json` |
| `test_hmong2lmf.py` | tests for the converter |
| `hmongnet.py` | WordNet-style access to the ontology (Nathan White's original) |
| `build.sh`, `run.sh` | build and preview the online lookup |

| File | What it is |
|---|---|
| `etc/pivots.lock` | the wordnet releases triangulation may use, from Cygnet's `wordnets.toml` |
| `facts.json` | every figure the paper cites, with the settings they depend on |
| `wordnets-cited.tsv` | each wordnet used, with its citation, licence and BibTeX key |
| `RESOURCES.md` | survey of further resources that could enrich the ontology |
| `IMPROVEMENTS.md` | what would improve the resource, measured and ranked |
| `correspondence/` | external reviews of this code, with the prompts that produced them |

## Schema

`hmong_ontology.xml` has a `<category_set>` declaring the semantic categories and
a `<word_set>` of `<lemma>` elements. A lemma has a `<form>`, optional
`<variant>`, `<status>`, `<source>` (the etymological source language),
`<headword>` (for a compound) and `<note>`, and one or more `<sense>` elements.
A sense has `<meaning>` glosses, a `<category>`, and optionally a `<note>`.

Four elements were added when the classifiers were folded in:

- `<dialect>` on a lemma: `WH` for White Hmong (Hmoob Dawb, ISO 639-3 `mww`) or
  `GM` for Green Mong (Hmoob Ntsuab, `hnj`). Every lemma carries one.
- `<function>` on a sense: `classifier`, `quantifier` or `class_noun`, recording
  Bisang's (1993) three-way distinction. A sense may have more than one, because
  several forms do more than one job.
- `<classifies form="thoob">bucket</classifies>` on a classifier sense: an
  example noun the source gives for that classifier, with its English gloss.
- `<classified_by form="lub"/>` on a noun sense: the classifier that noun takes.

## Classifiers

`classifiers.tsv` holds 235 numeral classifiers and quantifiers, 151 White Hmong
and 84 Green Mong, merged from two independent descriptions.

**White is the base analysis and Bisang fleshes it out.** Chapter 7 of White
(2021c) is the later and fuller treatment, it covers Green Mong as well as White
Hmong, and it states its disagreements with Bisang explicitly, so its categories
are the ones `CLASS` follows and `WHITE_CATEGORY` comes before
`BISANG_CATEGORY`. 118 rows rest on White alone, 45 are described by both, 55 come
from Bisang alone, and 17 only from `stopwords_classifiers.txt`.

What Bisang (1993) adds is of three kinds, and the first two are why this is a
merge rather than a copy of chapter 7:

1. **Measure words**, which White excludes as "not part of the system of noun
   categorization" (p. 366) and Bisang's Appendix I §2.1 counts. The body-part
   lengths are his: `ntiv` the width of a finger, `xib` the width of a palm,
   `taus` the width of one fist. Ten rows, and the single biggest difference
   between the two inventories.
2. **Class nouns**, which White rejects outright — see the caveat below.
3. **Finer categories** inside what White treats as one. White collapses measures,
   intrinsic quantifiers, collectives and kinds into a single mensural category
   (pp. 301–302); `BISANG_CATEGORY` preserves the distinction.

Running the other way, White's **locational** and **verbal action** classifiers
have no Bisang category at all, so those rows rest on him alone.

Each row is classified three ways: in the five-way scheme of Bond and Paik (2000)
— sortal, event, mensural, group, taxonomic — which is the scheme wordnet uses,
and in each source's own. Keeping all three columns makes every remapping
inspectable and reversible in both directions.

Smaller disagreements are in the `NOTE` column and the file's header: `cov` has
four analyses and we resolve none of them, and `daig`, `riag`, `nploog`, `ntsug`,
`ce` and `tug` are tone-melody alternants rather than separate classifiers, so
they become `<variant>` elements. 29 rows carry such a note.

Twelve rows are deliberately not added, recorded with the evidence in
`DISPOSITION`: six tone-melody alternants and six forms no source supports as
classifiers. Five rows are marked `CHECK: Nathan`.

`classifiers-white2021.tsv` is the unmerged extraction from White's chapter 7,
kept separately so the merge can be checked or redone; its own header records the
uncertainties in it.

## Class nouns

**A caveat on this file.** White (2021c: 359–361) rejects Bisang's class-noun
analysis of `phau`, `lo` and the rest, arguing that Bisang gives no supporting
evidence and that the analysis obscures otherwise clear grammatical
distinctions. Since this file is built on Bisang's Appendix II, that objection is
about the whole file and not just a label. It is kept because the *members* —
`ntoo ciab` 'larch', `txiv tsawb` 'banana' — are glossed vocabulary whatever one
calls their head, but the class-noun relation itself is contested.

`class_nouns.tsv` holds 28 class nouns and 121 member compounds. A class noun is
an ordinary, referential noun that heads a compound and fixes its semantic class:
`ntoo` 'tree' heads `ntoo ciab` 'larch'. The members follow the ontology's own
convention for compounds -- an underscored form with a `<headword>` -- so they
need no new machinery. 98 of the 121 were not previously in the ontology.

## Converting to WN-LMF

`hmong2lmf.py` writes WN-LMF 1.4, loadable by the
[`wn`](https://wn.readthedocs.io) library. A sense earns a link to the
Collaborative Interlingual Index only where the evidence is unambiguous: two or
more English glosses whose candidate synsets intersect in exactly one ILI, or a
single gloss that is monosemous for its part of speech, or -- with
`--concepticon` -- a gloss that is also a
[Concepticon](https://concepticon.clld.org) concept set with an exact wordnet
mapping. Everything else is left unlinked and reported, because a wrong link is
worse than none.

Classifiers are handled apart, following Morgado da Costa and Bond (2016): they
are not referential, so they take the part of speech `x`, carry their definition
as a `Definition`, and attach to the concept `classifier` by `exemplifies` rather
than by hypernymy. Their example nouns become `classifies` relations with the
converse `classified_by` on the noun. All four relations are first-class types in
WN-LMF 1.4.

### Folding in a CLDF wordlist

`--cldf DIR:LANGUAGE:NAME[:DIALECT]` adds the vocabulary of any Lexibank-style
CLDF wordlist to the generated lexicon. It is repeatable. Every CLDF parameter
carries a Concepticon id, so these senses reach the ILI through the concept set
directly — no gloss lookup, and so none of the homograph conflation that defeats
merging unaligned gloss lists. That route runs *before* the gloss pass, not after
it, so a hand-mapped concept set is never overruled by a gloss that happened to
resolve.

The fourth field is the dialect the wordlist records, `WH` or `GM`, defaulting to
`WH`. It is the wordlist's own dialect, not the one being built: WOLD's doculect is
White Hmong, so a `--dialect GM` run skips it rather than stamping 1,474 White
Hmong forms as Green Mong.

Folding in the White Hmong vocabulary of the
[World Loanword Database](https://wold.clld.org) (Ratliff's contribution, CC BY
4.0) takes the lexicon from 748 distinct ILIs to **1,358**; WOLD contributes
**1,019 concepts, 845 of them reached by no other source**:

```sh
git clone --depth 1 https://github.com/lexibank/wold.git ../wold
uv run hmong2lmf.py --ontology hmong_ontology.xml --output hmn-wh.xml \
    --concepticon ../cldf2wn/data/concepticon-ili.tsv \
    --cldf ../wold/cldf:WhiteHmong:WOLD:WH \
    --license https://creativecommons.org/licenses/by/4.0/
```

Where two sources give the same form for the same concept, the senses are merged
rather than both kept, so no synset lists a lemma twice. The surviving sense takes
the other's glosses, relations, identifiers and provenance, and the *stronger* of
the two linking methods — otherwise a triangulated link would be reported under
whichever weaker route happened to come first in the file. That also resolves the
adjectival-verb case, where the ontology has `kim` as a stative verb `be
expensive` and WOLD as the adjective `expensive`: one ILI is one concept, so it
stays one synset, and the reading whose part of speech matches the ILI's is the one
kept. The ILI's part of speech is read from English WordNet, so the tie-break does
not depend on a Concepticon file happening to cover that ILI.

WOLD is a loanword database, so its borrowing judgement is kept as a note on the
sense — it is the thing WOLD knows that no other source here does.

Note the licence interaction: the output may only be released under terms that
satisfy *every* source folded in. WOLD is CC BY 4.0 and the ontology is CC BY 4.0,
so that case is simple; a non-commercial or no-derivatives source would constrain
the result.

### Folding in Wiktionary, through DBnary

Hmong is not a Wiktionary edition, so it appears in Wiktionary only as a
translation target — but the English edition's translation tables are
**sense-anchored**, which is exactly the disambiguation a bare English lemma
lacks. [DBnary](http://kaiko.getalp.org/dbnary) publishes that as RDF with a
SPARQL endpoint, so no scraping is needed and the release is citable.

```sh
uv run fetch_dbnary.py                      # writes dbnary-hmong.tsv
uv run hmong2lmf.py ... --dbnary dbnary-hmong.tsv
```

One trap worth recording: **DBnary stores the target language as a lexvo URI, not
as a bare code.** `dbnary:targetLanguageCode` is used only for varieties lexvo does
not cover, so a query filtering on `"mww"` finds no Hmong at all and it is easy to
conclude wrongly that there is none. Querying
`dbnary:targetLanguage <http://lexvo.org/id/iso639-3/mww>` finds 732
sense-anchored translations, and `hnj` 29.

Wiktionary's sense numbering is its own and cannot be mapped to WordNet's, so the
converter compares the two *definitions* — Jaccard overlap of content words —
and accepts a synset only when it is both above a threshold and clearly better than
the runner-up. That is a tuned heuristic and weaker evidence than the Concepticon
route, which needs no threshold; the settings are deliberately conservative, so
most rows are declined rather than guessed. It also runs *last*, on the rows
triangulation has not already decided, since several agreeing lexicographers are
better evidence than two overlapping definitions. The exclusion key is the whole
sense anchor — form, English lemma and Wiktionary definition — because one Hmong
form may translate `bank` under both the financial and the river-edge sense, and
deciding one of those says nothing about the other.

### Dialects

White Hmong and Green Mong are separate ISO 639-3 languages and WN-LMF sets the
language on the lexicon, so one run produces one dialect:

```sh
uv run hmong2lmf.py --ontology hmong_ontology.xml --output hmn-wh.xml \
    --concepticon ../cldf2wn/data/concepticon-ili.tsv \
    --license https://creativecommons.org/licenses/by/4.0/
uv run hmong2lmf.py --ontology hmong_ontology.xml --output hmn-gm.xml --dialect GM \
    --license https://creativecommons.org/licenses/by/4.0/
```

Add `--report report.tsv` for a per-sense account of what linked, what did not,
and which candidate ILIs each unlinked sense had, with the English definition of
each, so that choosing between them is a reading task rather than a lookup task.

Add `--dbnary-review review.tsv` for the Wiktionary translations the definition
comparison would not decide, and `--pivot-review` for the triangulation groups the
pivot languages split on — 35 and 71 for White Hmong. Each row has the Hmong form,
the English lemma, the Wiktionary sense it was filed under, the candidate ILIs with
their English definitions, and an empty `VERDICT` column. Choosing between two or
three glossed candidates takes a speaker seconds, and it is work no threshold should
be doing on their behalf. A run with nothing to review writes a header-only file
rather than leaving the previous run's sheet in place.

### Which wordnets, at which release

Triangulation counts languages, so a pivot wordnet at a different release can
change which ILI wins — not just how many senses link. The releases are therefore
pinned, and the pins come from Cygnet's `wordnets.toml`, which is the same file the
online lookup is built from, so the two can never disagree:

```sh
uv run load_pivots.py --from ../cygnet/bin/raw_wns
```

That reads the release URLs out of `../cygnet/wordnets.toml`, loads the matching
WN-LMF files into `.wn_data` beside this script, checks that what landed is what
was pinned, and writes `etc/pivots.lock`. The English wordnet it pins is
**`oewn:2025+`**, the edition that includes curated proper names: the plain
`oewn:2025` has neither `Moon` (`i85806`) nor `Sun` (`i86272`), so two Concepticon
mappings dangle against it. The `+` edition costs four gloss-only links in exchange,
since 13,000 extra name synsets make a few monosemous glosses ambiguous. `hmong2lmf.py`, `facts.py` and
`conflicts.py` all read that lock file by default and refuse to use a lexicon at
any other version; `--allow-missing-pivots` overrides the refusal for exploration.
Nothing here ever reads or writes the user's `~/.wn_data`, and `load_pivots.py`
refuses that path explicitly.

`cite_wordnets.py` writes the citation, licence and version of every wordnet in
the lock file, generated from the loaded lexicons rather than typed, so the credits
cannot drift from what was actually queried:

```sh
uv run cite_wordnets.py --latex ../paper-hmong/wordnets.tex
```

Two lexicons declare no citation of their own (Open English WordNet and the Slovak
wordnet); the script supplies one for each and marks it as our attribution.

### Where two routes disagree

`conflicts.py` runs the Concepticon and triangulation routes separately and writes
every sense they both reach but name different ILIs for, with both candidates'
English lemmas and definitions on one line:

```sh
uv run conflicts.py --data-directory .wn_data \
    --concepticon ../cldf2wn/data/concepticon-ili.tsv \
    --cldf ../wold/cldf:WhiteHmong:WOLD:WH
```

They both reach 190 White Hmong senses and agree on 162 (85.3%). The 28
disagreements are in `review-conflicts-WH.tsv`, with an empty `VERDICT` column for
a speaker and separate `ADJUDICATION`/`BY` columns so that a reading by someone who
does not speak the language is never mistaken for a speaker's.

The comparison has to be made *before* `dedupe_senses` runs. Where both routes
reach one ILI, deduplication merges the two senses and labels the survivor with the
stronger route, so a comparison made afterwards sees the disagreements and almost
none of the agreements — 0% agreement, which is what we first measured.

Run the tests with:

```sh
uv run --with pytest --with wn pytest test_hmong2lmf.py -q
```

## Online lookup

`build.sh` also builds a browsable wordnet with
[Cygnet](https://github.com/fcbond/cygnet), which merges the two Hmong lexicons
with English WordNet so that an English word and a Hmong word reach each other
through the shared ILI. Cygnet is expected as a sibling checkout (`../cygnet`).

```sh
./build.sh          # ontology -> WN-LMF -> docs/hmong.db.gz
./run.sh            # serve docs/ and open it in a browser
```

Cygnet renders the part of speech `x` as **NREF**, non-referential, so the
classifiers display correctly with no extra work. `docs/relations.json` is
Cygnet's own file with `classifies` and `classified_by` added, since upstream has
`exemplifies` but not yet the two classifier relations.

Deployment goes through `.github/workflows/pages.yml`: the `.db.gz` files are
attached to a release and the workflow republishes them through Pages, because a
browser cannot fetch them from a release URL directly. The repository's
**Settings → Pages** source has to be **GitHub Actions** rather than "Deploy from
branch".

## Kinship, and KinDiv

Kinship is where this lexicon most needs *concepts* rather than links. English does
not lexicalise most of the distinctions Hmong obligatorily makes, so English
WordNet has no lemma for them: there is no `maternal uncle`, no `paternal uncle
older than father`, no `brother of a female`. Measured against English WordNet, 21
of the 37 kinship senses in `kinship.tsv` would have to be proposed from scratch.

They do not have to be. [KinDiv](https://github.com/kinship-diversity/KinDiv) is a
database of lexical diversity in the kinship domain — 198 concepts as Murdock kin
types, 1,904 words in 168 languages, 37,370 recorded gaps — and it gives each
concept a stable identifier (`Fa;El;Br` for a father's elder brother) that holds
across languages **even where the interlingual index does not reach**.

`kinship-kindiv.tsv` maps 28 of our kinship senses onto KinDiv concepts, 24 exactly.
The remaining four need concepts KinDiv does not yet declare — Hmong `nus`, `muam`,
`tij laug` and `kwv` name the child of a father's sibling regardless of whether that
sibling is a brother or a sister — and `kindiv-proposals.tsv` has those six rows
ready to paste into KinDiv, with their hypernym relations and the Hmong words. The converter emits the code as
`dc:identifier="KinDiv:Fa;El;Br"` on the synset, which is what KinDiv's own build
does, so an ILI-less kinship synset is still identified:

```xml
<Synset id="hmnont-s01509-n" ili="" partOfSpeech="n"
        dc:subject="consanguineal_relation" dc:identifier="KinDiv:Fa;Fa">
```

**KinDiv has no Hmong at all**, so this runs both ways: it gives our terms a
comparable identifier, and it gives KinDiv a language it lacks. The Green Mong
column is the most valuable part — White gives 16 distinct GM kinship forms, where
the classifier tables gave almost no GM content vocabulary.

## Rebuilding

`add_classifiers.py` folds the two TSV files into the ontology. It is idempotent,
so it can be re-run after either file is edited by hand:

```sh
uv run add_classifiers.py --class-nouns --underspecified --kinship
uv run add_classifiers.py --class-nouns --underspecified --kinship --check
```

The flags are separable because each adds material from a different table, and
each is a judgement a reader might want to decline: `--class-nouns` rests on an
analysis White rejects, `--underspecified` and `--kinship` on his own tables.
Re-running after a table gains a definition, a function or an example folds that
into the sense already there rather than skipping the row.

`facts.py` recomputes every figure the paper cites into `facts.json`, which also
records the settings — English wordnet, Concepticon file, wordlist, pivot lexicons
— that the figures depend on:

```sh
uv run facts.py --data-directory .wn_data --english oewn:2025+ \
    --concepticon ../cldf2wn/data/concepticon-ili.tsv \
    --cldf ../wold/cldf:WhiteHmong:WOLD:WH --pristine pristine.xml
```

## TODO

1. Create Python code to load the Hmong ontology as a WordNet-style library. Begun as hmongnet.py.
2. Expand vocabulary based on additional forms attested in speaker community using an automated approach.
3. ~~Label forms as White Hmong where distinct and add Green Mong forms.~~ Done for
   the existing lemmas and for the classifier inventory; the Green Mong vocabulary
   beyond the classifiers is still to come.
4. Implement stopword files.
5. ~~Write documentation.~~ This file, plus `IMPROVEMENTS.md` for what is
   measured and `RESOURCES.md` for what else exists.
6. ~~Supply definitions for the classifiers that had a class but no
   description.~~ Done, and six of them turned out to be tone-melody alternants
   or not classifiers at all; those are `<variant>` elements or declined rows
   with the evidence in the `DISPOSITION` and `NOTE` columns of
   `classifiers.tsv`. Five remain marked `CHECK: Nathan`.
7. Review the senses the converter leaves unlinked. 1,001 for White Hmong, of
   which 134 are already on the three annotation sheets above; `--report` ranks
   the rest, and `IMPROVEMENTS.md` says which stage returns most per row.
8. Mine the rest of White (2021c). Done: the kinship table (Table 29, p. 288) and
   the noun-to-classifier matrices (Tables 39–41, pp. 381–382). Still to do: the
   noun-subgroup scheme (§6.7, p. 298) and the class-term prefix inventory
   (§3.2.4.1, pp. 100–103).
9. A speaker-judged sample stratified across the evidence tiers. Nothing here is
   checked by a speaker yet, and this is the measurement that would turn the
   confidence story from a policy into a result — see `IMPROVEMENTS.md` item 8.

## To consider

1. Revisit distinction between object and artifact categories: it does not seem to have significance in Hmong.
2. Provide an additional xml file containing roots with additional bound root possibilities.

## References

### By the ontology's author

White, Nathan M. 2014. *Non-spatial setting in White Hmong*. Earlier thesis,
cited by White (2021b); we have not established the degree or the institution.

White, Nathan M. 2019. Classifiers in Hmong. In Alexandra Y. Aikhenvald and
R. M. W. Dixon (eds.), *Classifiers and Noun Categories*. Oxford University
Press. <https://doi.org/10.1093/oso/9780198842019.003.0008>

White, Nathan M. 2020. Word in Hmong. In *Word: A Cross-Linguistic Exploration*.
Oxford University Press. <https://doi.org/10.1093/oso/9780198865681.003.0008>

White, Nathan M. 2021a. Language and variety mixing in diasporic Hmong.
*Rivista di Linguistica*. <https://doi.org/10.26346/1120-2726-172>

White, Nathan M. 2021b. Grammaticalization and phonological reidentification in
White Hmong. *Studies in Language* 45(3).
<https://doi.org/10.1075/sl.19052.whi>

White, Nathan M. 2021c. *The Hmong language of North Queensland*. PhD thesis,
James Cook University. <https://doi.org/10.25903/f5rd-s089>\
Open access, 742 pages; the first comprehensive grammar of the variety, written
in Basic Linguistic Theory. **Chapter 7 (pp. 299–381) is a full account of the
classifier system**, and its categories — sortal, mensural (container,
collective, kind, time), locational, non-singular, possessed and verbal action —
are the ones `stopwords_classifiers.txt` in this repository is organised by, so
the stopword list is an index to that chapter rather than an ad-hoc list.
§1.5.2.1 (p. 25) reviews Bisang (1993), from which `classifiers.tsv` is built,
and §6.7 (p. 298) gives a noun-subgroup scheme.

White, Nathan M. et al. 2022. The Hmong Medical Corpus: a biomedical corpus for
a minority language. *Language Resources and Evaluation*.
<https://doi.org/10.1007/s10579-022-09596-2>

White, Nathan M. 2024. Quantifier float in Hmong. *Folia Linguistica*.
<https://doi.org/10.1515/flin-2024-2041>

White, Nathan M. 2025. *A Grammar of Hmong*. Berlin: De Gruyter.
<https://doi.org/10.1515/9783111546681>

### Other works cited

Bisang, Walter. 1993. Classifiers, quantifiers and class nouns in Hmong.
*Studies in Language* 17(1): 1–51. <https://doi.org/10.1075/sl.17.1.02bis>

Bond, Francis and Kyonghee Paik. 2000. Reusing an ontology to generate numeral
classifiers. In *COLING 2000*. <https://aclanthology.org/C00-1014/>

Fellbaum, Christiane (ed.). 1998. *WordNet: An Electronic Lexical Database*. MIT Press.

Morgado da Costa, Luís and Francis Bond. 2016. Wow! What a useful extension!
Introducing non-referential concepts to Wordnet. In *LREC 2016*, 4207–4214.
<https://aclanthology.org/L16-1685/>

T'sou, Benjamin K. 1976. The structure of nominal classifier systems.
In *Austroasiatic Studies* II, 1215–1247.
