# Resources for enriching the Hmong wordnet

Survey of lexical and semantic resources that could add **lemmas, senses, glosses,
relations or ILI links** to the White Hmong (`mww`) / Green Mong (`hnj`) wordnet
derived from Nathan M. White's `hmong-ontology`.

Compiled 2026-09-28, exploitation status updated 2026-10-04. All counts were checked
against a live API, repository file or catalogue record unless marked
**unverified**; nothing here is estimated by guesswork.

**Already exploited and therefore excluded:** Open English WordNet gloss lookup
(the `2025+` edition, which includes proper names); the Concepticon
`Borin-2015-1532` → ILI bridge; White (2021) chapter 7, Table 29 and Tables 39–41;
Bisang (1993) Appendices I–II; WOLD's White Hmong vocabulary; Wiktionary through
DBnary, both the sense-anchored Hmong translations and the 25 pivot languages'
translations of the same senses; KinDiv; Lexibank `starostinhmongmien`; Strecker's
*Classifiers and Nominalizers in Hmongic* manuscript.

**Measured and rejected:** `kaikki.org`'s bulk Wiktionary extraction — see
`IMPROVEMENTS.md`, which records why pooling its glosses made the result worse.

---

## Contents

**Start here.** The two highest-value items, both found on the second pass:

1. **WOLD's White Hmong vocabulary** (Second pass, Gap 7) — openly licensed
   CC BY 4.0, already in CLDF, already Concepticon-mapped, **632 ILIs we do not
   have**. No permission needed. Do this first.
2. **Strecker's *Mong Leng – English Dictionary*** (X1, held in `external/`) —
   4,442 senses of Green Mong, the language for which our lexicon has no
   interlingual links at all. Needs the author's permission.

- [Held locally in `external/`](#held-locally-in-external-gitignored-not-redistributable)
- [(A) Usable now, open licence](#a-usable-now-open-licence)
- [(B) Usable with permission or purchase](#b-usable-with-permission-or-purchase)
- [(C) Print-only or unverified](#c-print-only-or-unverified)
- [Cross-lingual pivots](#cross-lingual-pivots)
- [David Strecker's Academia.edu corpus](#david-streckers-academiaedu-corpus)
- [Not worth pursuing](#not-worth-pursuing)
- [Second pass, 2026-09-28](#second-pass-2026-09-28) — the gaps closed, plus
  Chinese-language sources for the Guizhou varieties
- [Verification notes](#verification-notes)

---

## Held locally in `external/` (gitignored, not redistributable)

Added 2026-09-28. These are copies held for research use; none carries a licence
that lets us redistribute it, and `external/` is gitignored for that reason. The
directory also holds the Bisang (1993) published article and the Strecker
Hmongic manuscript already described above.

### X1. Strecker (2021) *Mong Leng – English Dictionary, revised* — **the single best find**

- **What it is:** a full bilingual dictionary of Mong Leng by David Strecker,
  995 pages, dated 14 July 2021; an earlier 873-page version was uploaded to
  Academia.edu on 21 June 2021. Built from Xiong, Xiong and Xiong (1983), whose
  entire Mong-to-English section and whose appendices on verb intensifiers
  (pp. 553-556) and colour intensifiers (pp. 556-557) he says he incorporated,
  plus Lyman (1974) and the publications of Mong Volunteer Literacy, Inc.
- **Coverage (measured 2026-09-28 from the PDF's text layer):** **4,442 sense
  entries over 3,539 distinct head forms**, of which 1,661 are single-word and
  1,878 multi-word. Entries carry English glosses, text examples with sources,
  and in many cases **the classifier the noun takes** ("(no classifier)",
  "classifier cov").
- **Varieties:** Mong Leng = Moob Leeg = Mong Njua = Green Mong, `hnj`. Strecker
  is explicit that this is the first of the two principal varieties and that the
  ethnonym is *Mong*, not *Hmong*, for its speakers.
- **Orthography:** **standard RPA**, deliberately, in contrast to Lyman's
  idiosyncratic transcription -- so its forms string-match ours directly, with no
  conversion step. This is what makes it immediately usable.
- **Licence:** none stated. Self-published via Academia.edu. **Permission needed.**
  His email appears in the document itself.
- **Machine-readable:** no, but the text layer extracts cleanly and the entry
  format is regular: a sense begins a line as `- <form> 'gloss'`, with examples
  following. The 4,442 figure above came from that regex.
- **How it would enrich the wordnet:** it fixes the worst gap we have. Green Mong
  currently has 84 lemmas, all classifiers, and therefore **zero** interlingual
  links. A crude first-pass parse of this dictionary -- no part-of-speech
  handling, no category filter -- already links **1,369 senses to 849 distinct
  ILIs**. Doing it properly would turn a token presence into a real lexicon, and
  the classifier annotations would populate `classifies` relations, which the
  paper's limitations note are thin.

### X2. Colvin (2026) *A cover analysis of the plural classifier in Hmong*

- **Full citation**, from the PDF's own copyright line: Colvin, Quartz. 2026.
  "A cover analysis of the plural classifier in Hmong." In Sebastian Walter,
  Lennart Fritzsche, Kurt Erbach, Cécile Meier and Manfred Sailer (eds.),
  *Proceedings of Sinn und Bedeutung 30*, 221-231. Frankfurt: Goethe University
  Frankfurt. Presented at SuB30; too recent to be indexed anywhere searchable.
- **What it is:** an 11-page semantics paper analysing White Hmong `cov` as a
  plural classifier generating a set of sets (a cover), with `ib` as a
  choice-functional indefinite. It cites Bisang (1993) directly.
- **Why it matters here:** `cov` is the form our two main sources disagree about.
  Bisang (p. 8) calls it the plural marker; White (2021: 354, 362) makes it one of
  two non-singular classifiers; this paper argues it is a **plural classifier**, a
  third position. The repository's own stopword list files it as mensural, a
  fourth. Four analyses, one form.
- **Varieties:** White Hmong, `mww`. No lexical data; this is analysis, not a
  lexicon.
- **A fifth analysis to chase.** A search for this paper surfaced two others on
  the same form, neither yet read: **Ratliff, Martha. 1991. "Cov, the
  Underspecified Noun, and Syntactic Flexibility in Hmong." *Journal of the
  American Oriental Society* 111(4)** — and Ratliff is also the compiler of the
  WOLD vocabulary that is now our best open source, so her view carries weight
  here; and **Ball, William L. 2023. "*Cov* and Underspecified Nouns: A Syntactic
  and Semantic Analysis of Hmong Classifiers", BA thesis, Swarthmore College,
  <https://works.swarthmore.edu/theses/309>**, which argues the classifier of
  underspecified and mass nouns is merely an *n* head, licensing a second
  classifier. Both bear on the same `cov` question and on the underspecified-noun
  matrices in White's Tables 39-41.

### X3. *Thoughts on Bisang "Classifiers, Quantifiers and Class Nouns in Hmong"*

- **What it is:** a 1,043-word working note, three pages, created 23 September
  2016. The document's metadata gives no author ("My Laptop"), so we do not
  attribute it.
- **What it argues:** that Bisang's classes II-IV (measures, collectives, kinds)
  are **classifiers, not quantifiers**, because all three take the classifier
  frame NUM + CL + N rather than the quantifier frame Q (+CL) + N, and because all
  three combine with numerals where true quantifiers (`ntau`, `coob`, `qee`) do
  not. It observes that Chinese linguistics uses "classifier" and "measure word"
  interchangeably and does not treat measure words as quantifiers.
- **Why it matters here:** this is the reasoning behind the single biggest
  disagreement in `classifiers.tsv` -- White (2021: 301-302) collapses exactly
  those three classes into one mensural category, and this note argues the case
  five years earlier. It also complicates our taxonomic class: on Bisang's Class
  IV (`hom`, `yam`) the note reports that **Heimbach and Mottin list them as
  classifiers while Jay Xiong and Yuepheng Xiong call them nouns**, and is itself
  undecided. So the three rows in our taxonomic class rest on contested ground.

---

## (A) Usable now, open licence

Sorted by expected value.

### A1. Lexibank `chenhmongmien` — Chén Qíguāng (2012) *Miáoyáo yǔwén* 苗瑤语文

- **What it is:** CLDF wordlist dataset derived from Chén Qíguāng 陳其光 (2012)
  *Miáoyáo yǔwén* 苗瑤语文 (China Minzu University Press), digitised by Doug Cooper
  and released via the Wiktionary appendix *Hmong-Mien comparative vocabulary list*.
- **Coverage (verified from `cldf/` and README):** 25 Hmong-Mien varieties (22
  distinct Glottocodes), **883 concepts** mapped to **799 Concepticon concept
  sets**, **22,011 lexemes**, 116,296 segmented tokens. Concepticon linkage 91%,
  Glottolog 96%.
- **Varieties:** Guizhou-relevant ones are directly present — Qiandong North
  (`hea`, Hmu/Black Miao), Qiandong East (`hmq`), Qiandong South (`hms`),
  Qiandong West, Chuanqiandian Northeast Yunnan (`hmd`, A-Hmao/Large Flowery),
  Chuanqiandian Central Guizhou (`hmi`), Chuanqiandian Southern Guizhou (`hmm`),
  Chuanqiandian (`cqd` — the cluster that contains `mww`/`hnj`), Xiangxi West
  (`mmr`, Xong), Xiangxi East (`muq`), Luobuohe E/W (`hml`), plus Bunu, Pa-Hng,
  She, Jiongnai, Iu Mien (`ium`), Kim Mun (`mji`), Biao Min (`bje`), Zao Min (`bpn`).
  **`mww`/`hnj` are not separate rows** — the nearest is Chuanqiandian `cqd`.
- **Licence:** CC-BY-4.0 (stated in repo README and `LICENSE`).
- **URL:** <https://github.com/lexibank/chenhmongmien> · conceptlist
  <https://concepticon.clld.org/contributions/Chen-2012-888> · released versions
  carry Zenodo DOIs.
- **Machine-readable:** yes — CLDF (`cldf/forms.csv`, `parameters.csv`,
  `languages.csv`, `cognates.csv`), loadable with `pycldf`/`cldfbench`.
- **How it would enrich the wordnet:** it is by far the largest single extension
  of the Concepticon→ILI bridge already in use. Measured overlap with the
  `Borin-2015-1532` conceptlist (1,373 distinct Concepticon IDs):
  **473 of its 799 concept sets are Borin-linked**, against only **95 of the 110**
  in `starostinhmongmien` — i.e. **390 Borin-linked concepts that
  `starostinhmongmien` does not cover**, roughly a fourfold expansion of the
  bridge. For `mww`/`hnj` the gain is indirect (via `cqd` cognates, so it needs
  a cognate/regular-correspondence step); for the Guizhou sister project it is
  direct coverage of `hea`, `hmd`, `mmr`.
  Chén's concept list also carries a **Chinese gloss column** (`CHINESE` in
  `Chen-2012-888.tsv`), so it doubles as a Chinese-pivot source (see
  [Cross-lingual pivots](#cross-lingual-pivots)).

### A1b. White (2021) *The Hmong language of North Queensland* — PhD thesis, open access

- **What it is:** the first comprehensive grammar of the Hmong of North
  Queensland, written in Basic Linguistic Theory, by the author of this
  repository's ontology. 742 pages.
- **Coverage (verified 2026-09-28):** **chapter 7, "Classifiers", printed
  pp. 299-381** is a full account of the classifier system, with sections for
  sortal (303), subordinate sortal (329), mensural (332), container (338),
  collective (340), kind (343), time (345), locational (350), non-singular (354),
  the possessed classifier WH `li` / GM `le` (365), and verbal action classifiers
  (367). §1.5.2.1 (p. 25) reviews Bisang (1993). §6.7 (p. 298) gives a
  noun-subgroup scheme. Appendix A is texts; Appendix B documents the Hmong
  Medical Corpus.
- **Varieties:** White Hmong (`mww`) and Green Mong (`hnj`) — he uses the tags
  `WH` and `GM` himself, which is where this repository's convention comes from.
- **Licence:** the JCU record is marked `rights: open`; the PDF downloads without
  authentication. Confirm the exact reuse terms with the author before
  redistributing anything derived from it — he has already agreed to CC BY 4.0
  for the ontology, so asking is realistic.
- **URL:** <https://researchonline.jcu.edu.au/81550/> · DOI
  <https://doi.org/10.25903/f5rd-s089> · PDF
  `https://researchonline.jcu.edu.au/81550/1/JCU_81550_White_2021_thesis.pdf`
  (5,651,122 bytes). The repository's search interface is JavaScript-rendered and
  `cgi/search` returns 403, but **OAI-PMH works**:
  `cgi/oai2?verb=GetRecord&metadataPrefix=oai_dc&identifier=oai:researchonline.jcu.edu.au:81550`.
  Page offset: printed page + 37 = PDF page.
- **Machine-readable:** no, but `pdftotext` extracts cleanly (use `-layout` for
  the tables). The text layer is genuine, not OCR.
- **How it would enrich the wordnet:** this is the highest-value source found for
  the *classifiers* specifically, and the reason is structural. The 37 forms in
  `classifiers.tsv` that carry a class but no definition came from this
  repository's `stopwords_classifiers.txt`, whose headings — including
  "locational classifiers" and "verb classifiers", which have no counterpart in
  Bisang — are chapter 7's own categories. The stopword list is therefore an index
  into this chapter, and the missing definitions are very likely all in it. It
  also gives a second, independent classifier taxonomy to set against Bisang's,
  and the noun-subgroup scheme of §6.7 could be aligned to wordnet lexicographer
  files.

### A2. Ratliff (2010) *Hmong-Mien Language History* — open access, CC BY 4.0

- **What it is:** the standard comparative-historical treatment of Hmong-Mien,
  Pacific Linguistics 613, with reconstructed Proto-Hmong-Mien lexicon and
  English-glossed cognate sets showing reflexes across the family.
- **Coverage:** number of reconstructed items **unverified** (not stated in the
  repository metadata; needs the PDF to be counted).
- **Varieties:** Proto-Hmong-Mien plus reflexes in White Hmong, Mong Leng/Green
  Mong and Guizhou Hmongic varieties; gloss language English.
- **Licence:** **CC BY 4.0** — explicitly "Released under Creative Commons
  License (Attribution 4.0 International)" on the ANU record. Fully reusable.
- **URL / DOI:** <http://hdl.handle.net/1885/146760> · DOI `10.15144/PL-613` ·
  PDF `613 Ratliff.pdf` (2.22 MB).
- **Machine-readable:** PDF, born-digital (text layer, not scanned images), so
  the comparative tables are extractable with effort.
- **How it would enrich the wordnet:** gives English glosses for Hmong forms the
  ontology may not gloss, and — more valuably — supplies cognate sets that let a
  gloss attested for one Hmongic variety be transferred to a `mww`/`hnj` form,
  which is exactly the inference needed to convert `chenhmongmien` coverage into
  `mww`/`hnj` ILI links.

### A3. English Wiktionary via kaikki.org (wiktextract) — White Hmong

- **What it is:** machine-readable extraction of the English Wiktionary
  White Hmong entries.
- **Coverage (verified 2026-09-28):** kaikki reports **815 distinct words /
  1,400 senses**; per-POS sense counts Noun 739, Verb 276, Adjective 190,
  Proper name 44, Adverb 33, **Classifier 31**, Pronoun 23, Numeral 14,
  Interjection 12, Preposition 12, Particle 9, Determiner 7, Conjunction 5.
  Cross-checked on the Wiktionary API: `Category:White Hmong lemmas` = 815 pages,
  `White Hmong nouns` 546, `verbs` 173, `adjectives` 136, `classifiers` 24,
  `terms with IPA pronunciation` 794. Green Hmong is much smaller:
  `Category:Green Hmong lemmas` = **61 pages** (nouns 29, verbs 5).
- **Varieties:** English Wiktionary labels these "White Hmong" (`mww`) and
  "Green Hmong" (`hnj`) — exactly our two.
- **Licence:** CC BY-SA 4.0 + GFDL (Wiktionary content); wiktextract tooling MIT.
- **URL:** <https://kaikki.org/dictionary/White%20Hmong/index.html> · direct
  download `kaikki.org-dictionary-WhiteHmong.jsonl` (1,171,000 bytes,
  last modified 2026-09-25). There is **no** kaikki page for Green Hmong
  (404) — `hnj` entries must be filtered out of the full English-edition dump
  (`https://kaikki.org/dictionary/rawdata.html`, 23.9 GB raw / 2.8 GB gzipped,
  extracted from the enwiktionary dump dated 2026-09-02).
- **Machine-readable:** yes — JSONL, one object per entry, with senses, glosses,
  IPA, tags, topics and categories.
- **How it would enrich the wordnet:** the highest-yield *direct* source for
  `mww`. 1,400 English-glossed senses against our 1,601 senses: it will add new
  lemmas, add second glosses to senses that currently have only one (which is
  precisely what the ILI heuristics need), and supply IPA and POS for validation.

### A4. English Wiktionary translation tables (English → Hmong)

- **What it is:** English lemma pages that carry a Hmong translation inside a
  sense-labelled translation table.
- **Coverage (verified via the Wiktionary API):**
  `Category:Terms with White Hmong translations` = **524 pages**;
  `Category:Terms with Green Hmong translations` = **16 pages**.
- **Varieties:** `mww`, `hnj`.
- **Licence:** CC BY-SA 4.0 / GFDL.
- **Machine-readable:** yes — the `translations` field of the English-language
  entries in the same kaikki/wiktextract dump, filtered on `lang_code` `mww`/`hnj`.
- **How it would enrich the wordnet:** this is the *cleanest* ILI route in the
  whole survey. A translation table entry is anchored to a specific English sense
  gloss, so English lemma + sense gloss → Open English WordNet synset → ILI is a
  near-deterministic mapping, avoiding the monosemy/intersection heuristics
  entirely. ~540 pairs, so realistically a few hundred new or confirmed links.

### A5. SIL — *Honghe Hmong Survey Wordlist Data* (Castro, Flaming & Cohen, 2008–09)

- **What it is:** field wordlist data from an SIL East Asia Hmong dialect survey
  in Honghe Prefecture, Yunnan: edited IPA transcriptions (audio on request).
- **Coverage (verified from the SIL archive record):** "up to 467 words,
  10 datapoints".
- **Varieties:** subject languages listed as Hmong [hmn] with content languages
  Mandarin Chinese [cmn], Chuanqiandian Cluster Miao [`cqd`], English [eng],
  **Hmong Shua [`hmz`]**, **Hmong Daw [`mww`]**.
- **Licence:** **no explicit licence on the record** — the page carries only
  "Copyright © SIL Global" and the site Terms of Use, and the item is marked
  "Draft (posted 'as is' without peer review)". Treat as *freely downloadable but
  not openly licensed*; ask SIL before redistribution. Placed in (A) because the
  file is directly downloadable without permission.
- **URL:** record <https://www.sil.org/resources/publications/entry/88043> ·
  file `Honghe_Hmong_Survey_Wordlist.xlsx` (97.59 KB).
- **Machine-readable:** yes — a single `.xlsx`, glosses in **English and Chinese**.
- **How it would enrich the wordnet:** small but high-quality; gives a `mww`
  wordlist with parallel English *and* Chinese glosses, so it feeds both the
  English route and the Chinese pivot, and its `cqd`/`hmz` columns help bridge
  `chenhmongmien`'s Chuanqiandian data to `mww`.
- **Companion publication:** Castro, Flaming & Luo (2012) *A Phonological and
  Lexical Comparison of Western Miao Dialects in Honghe* 红河州苗语方言的发音与词汇比较,
  SIL Electronic Survey Report 2012-010, 62 pp., free PDFs in English
  (`silesr2012_010.pdf`) and Chinese (`silesr2012_010_Chinese.pdf`) at
  <https://www.sil.org/resources/publications/entry/47764>. Eleven Miao
  sub-branch dialects, ~274,000 speakers in the prefecture.
- **Note:** the record states that "the Wenshan portion of this Hmong survey"
  was "uploaded separately". That second dataset would be directly relevant
  (Wenshan is the core `mww`/`hnj` area in China) but its SIL entry number could
  not be located — SIL's search endpoints return HTTP 403 to non-browser clients.
  **Unverified; worth a manual look.**

### A6. `dmort27/sch-corpus` — soc.culture.hmong Usenet corpus (CC0)

- **What it is:** a Hmong corpus built from `soc.culture.hmong` Usenet posts,
  1996–2016, anonymised, tokenised, with **elaborate-expression spans annotated
  B/I/O** and language-ID annotation.
- **Coverage (verified from the GitHub tree):** 8,395 files, ~72.2 MB of data,
  CoNLL-like format (`data/sch-corpus-langid-elab/sch-NNNNN.conll`).
- **Varieties:** diaspora Hmong, predominantly White Hmong RPA orthography.
- **Licence:** **CC0-1.0** (repo licence field). Caveats in the README: the
  content is user-generated Usenet text, includes offensive material, and the
  maintainer offers takedown on request.
- **URL:** <https://github.com/dmort27/sch-corpus>
- **Machine-readable:** yes.
- **How it would enrich the wordnet:** frequency evidence for ranking senses and
  choosing which lemmas to add; usage examples to attach to senses; and the
  elaborate-expression annotation is the natural source for multiword entries of
  the type Johns & Strecker (1987) describe, a class the current ontology barely
  covers.

### A7. `nathanmwhite/hmong-medical-corpus` (GPL-3.0)

- **What it is:** a POS-tagged corpus of Hmong medical/public-health texts by the
  author of `hmong-ontology` itself, with a trained Stanford CoreNLP POS tagger.
- **Coverage (verified from the GitHub tree):** `hmcorpus_train.conllu` 439 KB +
  `hmcorpus_test.conllu` 31 KB in CoNLL-U, plus source `.docx` documents
  (`corpus-docs/`) and a `hmong-pos-tagger.model` (142 KB).
- **Varieties:** White Hmong (`mww`), diaspora/public-health register.
- **Licence:** GPL-3.0. (GPL on data is awkward for a CC-BY wordnet release —
  use it for validation and tagging rather than copying content.)
- **URL:** <https://github.com/nathanmwhite/hmong-medical-corpus>
- **Machine-readable:** yes — CoNLL-U.
- **How it would enrich the wordnet:** domain vocabulary (body parts, disease,
  treatment) that maps cleanly onto well-populated WordNet lexicographer files,
  plus an independent POS signal for verifying the ontology's part-of-speech
  assignments. Same author, so provenance and orthography already match.

### A8. PanLex — OntoLex-Lemon edition on Zenodo

- **What it is:** PanLex is a panlingual translation database built by merging
  thousands of bilingual dictionaries; the Zenodo release is an RDF/OntoLex
  rendering in 8 batches.
- **Coverage — Hmong sources actually in PanLex** (verified from
  <https://panlex.org/source-list/>; "entries" = PanLex's own count,
  "ingested" > 0 means the data is in the database):

  | PanLex source id | Title | Year | Entries | Ingested |
  |---|---|---|---|---|
  | `hnj-fra:Dourthe` | Dictionnaire FREELANG : Hmong–Français | 2005 | 7,580 | yes |
  | `fra-hnj:Dourthe` | Dictionnaire FREELANG : Français–Hmong | 2005 | 7,476 | yes |
  | `eng-hnj:Lauj` | English–Hmong (Babylon) | 2009 | 7,500 (est.) | yes |
  | `hnj-mww-eng:Yang` | Hmong Words List/Glossary (Shoua Yang) | 1997 | 5,800 (est.) | yes |
  | `eng-hnj:Thao` | English-Hmong Phrasebook with Useful Wordlist (Cheu Thao) | 1981 | 4,000 (est.) | yes |
  | `eng-hnj:Lo` | English–Hmong Legal Glossary (Chercheng Lo) | 2005 | 1,700 (est.) | yes |
  | `hmq-eng:LiHML` | Hmong/Miao Lexicon (Mai Die Li) — East Qiandong Miao | 2008 | 82 | yes |
  | `hnj-eng:HEG` | Hmong English Glossary | 2006 | unknown | **no** |
  | `eng-mww:Xyooj` | English–Mong Legal Glossary (Kub Xyooj) | 2005 | unknown | **no** |
  | `eng-cqd-mul:Castro` | A Phonological and Lexical Comparison of Western Miao Dialects in Honghe | 2012 | unknown | **no** |

  PanLex also lists Heimbach's *White Hmong-English dictionary* as a source: the
  Internet Archive copy `whitehmongenglis00erne` is tagged
  `collection: panlex` with languages `['eng','hmn','mww','mww-000']`. It does
  **not** appear in the public source list — note that the `panlex.org/source-list/`
  page is **truncated by the server at 1,047,575 bytes** (the embedded JSON is cut
  mid-object; 4,877 of an unknown larger number of source records are readable),
  so Heimbach is probably in the unreachable tail. **Total `mww`/`hnj` expression
  counts: unverified** — `api.panlex.org` and `db.panlex.org` do not resolve from
  here, so per-langvar totals could not be queried.
- **Varieties:** note that PanLex assigns almost all of this material to `hnj`,
  not `mww`, including the Freelang French dictionary. That labelling should be
  treated with suspicion (much of it is RPA White Hmong material) and checked
  against our own data.
- **Licence — conflicting statements, check before release:**
  <https://panlex.org/license/> states **CC BY-NC-SA 4.0**, with commercial use
  only by written permission; the Zenodo OntoLex record is tagged **CC0**
  (`cc-zero`). The NC clause would be incompatible with a CC-BY wordnet release,
  so this must be resolved with PanLex directly before any PanLex-derived link
  ships. The Zenodo edition is also a 2022-06-26 snapshot, not current.
- **URL:** <https://panlex.org> · source list <https://panlex.org/source-list/> ·
  Zenodo batch 1 of 8 <https://zenodo.org/records/6757353>
- **Machine-readable:** yes — OntoLex-Lemon RDF (Zenodo), or the live database if
  the API can be reached.
- **How it would enrich the wordnet:** the single largest pool of Hmong↔other
  translation pairs available under any licence — on the order of 20,000+
  ingested denotations — and it is already normalised into a uniform
  expression/denotation model, which is exactly the shape needed for pivoting.
  The French half feeds WOLF (see [Cross-lingual pivots](#cross-lingual-pivots)).

### A9. Lexibank `wanghmongmien` and `hsiuhmongmien`

- **What they are:** two further CLDF Hmong-Mien wordlists.
- **Coverage (verified from READMEs):**
  - `wanghmongmien` — from Wang Feng (2015), *Bulletin of Chinese Linguistics* 8:157–176.
    12 varieties (incl. Proto-Hmong-Mien), **62 concepts**, **794 lexemes**,
    Concepticon 100%, conceptlist `Wang-2015-62`.
  - `hsiuhmongmien` — from Hsiu (2015) on the classification of Na Meo (SEALS 25
    handout). 12 varieties (4 Glottocodes), **315 concepts** (309 Concepticon
    sets), **910 lexemes**, cognate-coded, conceptlist `Hsiu-2015-315`. Includes
    Guizhou Hmu points: Yanghao (`hea`), Caidiwan (`hmq`), Yaogao (`hms`), plus
    Zhenmin, Guncen, Datu, Yangpai, Xiang'ao, Heba, Baixing, and Na Meo (`neo`)
    in Vietnam.
- **Licence:** CC-BY-4.0 (both).
- **URL:** <https://github.com/lexibank/wanghmongmien> ·
  <https://github.com/lexibank/hsiuhmongmien>
- **Machine-readable:** yes — CLDF.
- **How they would enrich the wordnet:** small marginal gain over
  `chenhmongmien`, but `hsiuhmongmien` adds cognate codings and several
  otherwise-undocumented Guizhou Hmu datapoints, which help the Guizhou sister
  project and provide independent confirmation for cognate-transferred glosses.

---

## (B) Usable with permission or purchase

### B1. Johnson & Strecker (2020) *An Overview of Hmong Sha (West Hmongic, Guangnan) Phonology and Lexicon*

- **What it is:** a manuscript phonological sketch **plus a lexicon** of Hmong
  Sha, a previously poorly described West Hmongic dialect of Guangnan county,
  southeast Yunnan, "closely related to well-known Hmong Daw (White Hmong)".
- **Coverage (verified from the abstract):** "a lexicon comprising **close to 600
  roots with subentries**"; also a phonological comparison against three other
  Hmongic dialects. 94 recorded downloads.
- **Varieties:** Hmong Sha (West Hmongic, Guangnan; no separate ISO code —
  closest are `cqd` Chuanqiandian Cluster and `mww`); gloss language **English**.
- **Licence:** **no licence stated** — an Academia.edu manuscript upload. Would
  need the authors' permission. Not downloadable without an Academia.edu login.
- **URL:** <https://www.academia.edu/44730663/> (a near-duplicate upload sits at
  `.../44589444/`).
- **Machine-readability:** unknown; a text-layer PDF is likely since it is a
  born-digital manuscript, but this could not be confirmed without downloading.
- **How it would enrich the wordnet:** ~600 English-glossed roots in a variety
  close enough to White Hmong that most forms will be recognisably cognate — a
  direct source of second glosses for currently unlinkable `mww` senses, and the
  single best candidate in this report for closing the 662-sense gap. **Ask
  Strecker; he has already been in contact about the Hmongic manuscript, and
  Michael Johnson is the co-author.**

### B2. Heimbach (1969/1979/1980) *White Hmong–English Dictionary*

- **What it is:** the standard White Hmong–English dictionary, Cornell Southeast
  Asia Program Linguistics Series IV.
- **Coverage:** entry count **unverified** (318 scanned pages in the Internet
  Archive copy).
- **Varieties:** `mww`; gloss language English.
- **Licence / availability:** in copyright. The Internet Archive holds a
  digitised copy but it is `access-restricted-item: true` — controlled digital
  lending only, so the OCR text is not downloadable. **However**, the item is
  tagged `collection: panlex` with languages `['eng','hmn','mww','mww-000']`,
  which means PanLex has already licensed or processed it; the practical route is
  to obtain it through PanLex (A8) rather than to re-digitise it.
- **URL:** <https://archive.org/details/whitehmongenglis00erne> ·
  Open Library work `/works/OL2165553W`
- **Machine-readable:** not as distributed (scanned, restricted). Via PanLex, yes.
- **How it would enrich the wordnet:** the canonical `mww` gloss source; would
  plausibly resolve most of the remaining unlinked senses on its own.

### B3. Strecker's Hmong intensifier / expressive series (~25 manuscripts, 2021–22)

- **What it is:** a run of short Academia.edu notes documenting individual Hmong
  *zhuàng cí* (intensifiers / expressives) with textual examples — `hlo`,
  `nkaus`, `lawg`/`laws`, `quas`, `zuj zus`, and a preliminary overview.
- **Coverage:** ~25 notes; the overview is titled *White Hmong and Mong Leng
  intensifiers, a preliminary overview with text examples*. Item counts per note
  **unverified**.
- **Varieties:** White Hmong (`mww`) and Mong Leng / Green Mong (`hnj`) —
  both of ours; gloss language English.
- **Licence:** **no licence stated** — Academia.edu uploads; needs the author's
  permission.
- **URL:** entry points <https://www.academia.edu/71783630/> (overview),
  <https://www.academia.edu/72679601/> (`hlo`), <https://www.academia.edu/73033315/> (`nkaus`).
- **Machine-readable:** PDF, born-digital.
- **How it would enrich the wordnet:** expressives/intensifiers are a
  well-populated Hmong word class with essentially no WordNet counterpart. They
  would not gain ILI links, but they would add a coherent and linguistically
  defensible block of `mww`/`hnj` lemmas with definitions — the same role
  Bisang's classifier appendices already play in the build.

### B4. Thai–Hmong dictionaries (Thai pivot)

See [Cross-lingual pivots](#cross-lingual-pivots) — print-only, library access
required.

### B5. Miao–Chinese dictionaries published in China (Chinese pivot)

See [Cross-lingual pivots](#cross-lingual-pivots) — purchase or library access.

### B6. Bertrais (1964/1979) *Dictionnaire hmong (mèo blanc)–français* (French pivot)

See [Cross-lingual pivots](#cross-lingual-pivots).

### B7. `ogde0004/hmongdict` — a four-way Hmong dictionary SQLite database

- **What it is:** a GitHub mirror of the abandoned Google Code project
  `hmongdict`, a .NET desktop dictionary application. It ships a bundled SQLite
  database.
- **Coverage (verified from the repo tree and `HmongDict Sqlite Db Struct.txt`):**
  `HmongDict/Dict.db`, 446,464 bytes, with four tables declared —
  `HmongChineseTable` (苗汉词典 Hmong–Chinese), `ChineseHmongTable` (汉苗词典
  Chinese–Hmong), `HmongEnglishTable` (Hmong–English), `EnglishHmongTable`
  (English–Hmong). Entry counts per table **unverified** (would require opening
  the file).
- **Varieties:** unlabelled "Hmong"; the RPA orthography and the app's
  zh-CHS/en resource files suggest a China-facing White Hmong resource.
- **Licence:** **none stated** — no `LICENSE` file, and the underlying dictionary
  content has no stated provenance, so it may well be a redistribution of a
  commercial dictionary. **Do not use without establishing provenance.**
- **URL:** <https://github.com/ogde0004/hmongdict>
- **Machine-readable:** yes, trivially — SQLite.
- **How it would enrich the wordnet:** the only *directly machine-readable*
  Hmong–Chinese dictionary found anywhere in this survey, which makes it the
  cheapest possible feed for the `omw-cmn`/`cow` pivot. Its value is entirely
  gated on the licence question.

---

## (C) Print-only or unverified

### C1. Lyman (1974) *Dictionary of Mong Njua*

- Mouton (Janua Linguarum, Series Practica). The standard Green Mong (`hnj`)
  dictionary, gloss language English. In copyright; **no digitised copy found**
  on the Internet Archive, Open Library (works `/works/OL4558049W`,
  `/works/OL27315472W`, `/works/OL4558050W`) or in PanLex's source list. Entry
  count unverified. Print-only; would need scanning plus permission. Directly
  relevant because `hnj` is our weaker of the two varieties (only 61 Green Hmong
  Wiktionary lemmas exist).

### C2. Xiong, Xiong & Xiong (1983) *English–Hmong / Hmong–English Dictionary*

- Not located in the catalogues searched. What **was** found is a different and
  later work: **Xiong, Yuepheng L. (2011) *English-Hmong/Hmong-English
  dictionary*, Hmongland Publishing, St Paul** — Internet Archive
  `englishhmonghmon0000xion`, 502 pages, `access-restricted-item: true`
  (controlled digital lending, OCR not downloadable). Also
  **McKibben (1992) *English–White Hmong dictionary*** (Open Library
  `/works/OL3990874W`), no digital copy found. All print/restricted.

### C3. Strecker & Vang (1986) *White Hmong Dialogues*

- Southeast Asian Refugee Studies Occasional Papers 3, University of Minnesota.
  A glossed dialogue collection; also *Hmong For Beginners Part I* (1995), listed
  in OpenAlex as available via eScholarship. Both would yield glossed `mww`
  vocabulary in a controlled pedagogical register. Availability and licence
  unverified. Related Academia.edu upload:
  <https://www.academia.edu/63491201/> (*Hmong For Beginners Part I*).

### C4. SIL Wenshan Hmong Survey Wordlist

- Referenced from the Honghe record (A5) as "uploaded separately", and Wenshan
  is the principal `mww`/`hnj` area in China, so this is potentially more
  valuable than the Honghe set. **Entry number not located** — SIL's search
  endpoints (`/resources/search/...`) return HTTP 403 to non-browser clients and
  the bot-protection layer blocks proxied fetches. Needs a manual browser lookup.

### C5. Other Pacific Linguistics / ANU open-access Hmong items

- The ANU Open Research repository (same CC BY collection as Ratliff) also holds
  *Hmong secret languages: themes and variations* (2003), *Hmong and areal
  South-East Asia* (1989), *Process and Goal in White Hmong* (2010), and
  *Qhuab Ke (Guiding the Way) From the Hmong Ntsu of China, 1943* (2008).
  These are analytical papers and text editions rather than lexicons; individual
  licences and lexical content unverified. `Qhuab Ke` is a glossed ritual text
  and may contain a wordlist.

### C6. Jarkey (2015) *Serial Verbs in White Hmong*

- Brill (Brill's Studies in South and Southwest Asian Languages). Closed access
  (verified: OpenAlex `oa_status: closed`). See
  [Frame and argument-structure resources](#frame-and-argument-structure-resources).

---

## Cross-lingual pivots

The pivot logic: a Hmong–X dictionary gives `Hmong form → X gloss`; the X gloss
is looked up in an X-language wordnet that is already ILI-linked; the resulting
ILI is the same one the English route targets. Where two pivot languages agree,
the link is much more trustworthy than a single-language match.

**Which pivot wordnets actually exist.** Against the `wn` library's lexicon index
(<https://github.com/goodmami/wn/blob/main/wn/index.toml>): `omw-fr` = **WOLF
(Wordnet Libre du Français)**; `omw-cmn` = **Chinese Open Wordnet**; `omw-th` =
**Thai Wordnet**; also `omw-id`/`omw-zsm` (Wordnet Bahasa). There is no `omw-vi`
in that index.

**But the `wn` index is not the whole picture.** Cygnet's own `wordnets.toml`
(`../cygnet/wordnets.toml`) now pulls the **TUFS basic-vocabulary dictionaries**,
which cover every mainland Southeast Asian language that matters here. All
verified present at the `v2026.04.06` release on 2026-09-28:

| pivot | file | size |
|---|---|---|
| Vietnamese | `tufs-vi-2026.04.06.tar.xz` | 51,304 bytes |
| Lao | `tufs-lo-2026.04.06.tar.xz` | 59,964 bytes |
| Thai | `tufs-th-2026.04.06.tar.xz` | 48,256 bytes |
| Khmer | `tufs-km-2026.04.06.tar.xz` | 81,068 bytes |
| Burmese | `tufs-my-2026.04.06.tar.xz` | 89,376 bytes |
| Chinese | `tufs-zh-2026.04.06.tar.xz` | 45,088 bytes |
| French | `tufs-fr-2026.04.06.tar.xz` | 165,388 bytes |

So **Vietnamese and Lao do have a pivot after all** — small ones, being basic
vocabulary lists rather than full wordnets, but ILI-linked and covering exactly
the two countries with large Hmong populations that the earlier draft of this
file wrote off. They are also already in the build, so they cost nothing to try.
Basic vocabulary is the right size for this job anyway: it is where Hmong glosses
are densest and where a single English lemma is least able to choose a sense.

### P1. French → `omw-fr` (WOLF)

**P1a. Freelang Hmong–French / French–Hmong (Dourthe 2005) — via PanLex. Group (A/B).**
- **Coverage (verified from PanLex's source list):** `hnj-fra:Dourthe` **7,580
  entries**, `fra-hnj:Dourthe` **7,476 entries** — both *ingested* into PanLex.
- **Gloss shape:** short — a Freelang dictionary file is a word-list format with
  one or a few comma-separated equivalents per headword, **not** definitional
  phrases. Ideal for lookup.
- **Licence:** the Freelang original is freeware, distributed as a Windows
  installer (`https://www.freelang.com/download/dictionnaire/dic_hmong.exe`),
  with its own copyright page — not an open licence. The usable route is PanLex,
  whose licence conflict (CC BY-NC-SA on the website vs CC0 on Zenodo) must be
  resolved first. **Pivot wordnet: `omw-fr`.**
- **Note:** PanLex labels this `hnj`. Verify against our own `mww`/`hnj` forms
  before trusting the variety assignment.
- **Why it matters:** ~7,500 French-glossed Hmong entries is the largest
  non-English gloss set obtainable without scanning a book, and it is already
  normalised. This is the highest-value cross-lingual pivot in the report.

**P1b. Bertrais (1964, repr. 1979) *Dictionnaire hmong (mèo blanc)–français*. Group (B/C).**
- Mission Catholique / Institut de l'Asie du Sud-Est. Open Library
  `/works/OL6353994W`. The standard French dictionary of White Hmong
  (`mww` — "mèo blanc"), heavily cited by Bisang. Entry count **unverified**;
  **no digitised copy found** on the Internet Archive or in PanLex. In copyright;
  needs purchase/library access and permission. Gloss shape: a missionary
  dictionary of this period mixes short equivalents with longer explanatory
  glosses — expect a mixture, so weaker per-entry than Freelang but far larger
  and authoritative. **Pivot wordnet: `omw-fr`.** Also relevant: Bertrais (1979)
  *Abécédaire hmong*.
- **Correction to the brief:** **Mottin (1978) is not a dictionary** — it is
  *Éléments de grammaire hmong blanc*. His other works are *Contes et légendes
  hmong blanc* (1980), *55 chants d'amour hmong blanc* (1980) and *History of the
  Hmong* (1980). Useful as glossed text, not as a lexicon.

### P2. Chinese → `omw-cmn` (Chinese Open Wordnet) / `cow`

**P2a. Chén (2012) Chinese gloss column in `chenhmongmien`. Group (A).**
- The Concepticon conceptlist `Chen-2012-888` carries a `CHINESE` column
  alongside `GLOSS` (verified: header
  `ID NUMBER CHINESE GLOSS PAGE CONCEPTICON_ID CONCEPTICON_GLOSS ...`, e.g.
  `天 / sky`, `太阳 / sun`). 888 rows.
- **Gloss shape:** single words — this is a Swadesh-style concept list, so the
  Chinese side is exactly one lexical item per concept. Optimal for lookup.
- **Licence:** CC-BY-4.0 (Concepticon and `chenhmongmien`).
- **Pivot wordnet: `omw-cmn` / `cow`.** Because the concepts are *already*
  Concepticon-mapped, the Chinese pivot here mainly serves as an independent
  confirmation of Concepticon→ILI assignments rather than a new source of links —
  valuable for raising confidence on the 473 Borin-linked sets.
- **Varieties:** the Guizhou set listed under A1, including `hea`, `hmd`, `mmr`.

**P2b. SIL Honghe wordlist + Castro et al. (2012). Group (A).** See A5: Chinese
and English glosses side by side for `mww`/`cqd`/`hmz`, ~467 concepts, plus a
62-page bilingual report. Gloss shape: single-word survey elicitation glosses.
**Pivot wordnet: `omw-cmn`.**

**P2c. Miao–Chinese dictionaries published in China. Group (B/C).**
Located via Open Library; all print, in copyright, entry counts **unverified**,
no digitised copies found:

| Work | Author(s) | Year | Publisher | Variety |
|---|---|---|---|---|
| 苗汉词典（黔东方言）*Miao Han ci dian: Qian dong fang yan* | Zhang Yongxiang, Cao Cuiyun | 1990 | Guizhou Nationalities Press 贵州民族出版社 | **Qiandong = Hmu / Black Miao `hea`** |
| 汉苗词典（黔东方言）*Han Miao ci dian: Qian dong fang yan* = *Diel hmub cif dieex* | Wang Chunde | 1992 | Guizhou Nationalities Press | **Qiandong `hea`** |
| 汉苗词典 *Han Miao ci dian* | Xiang Rizheng | 1992 | Sichuan Nationalities Press | Miao (Sichuan; likely Chuanqiandian) |
| 苗汉词典 *Miao Han ci dian* | Pan Zhengfeng | 1993 | Yunnan People's Press | Miao (Yunnan; likely Chuanqiandian/`mww`-adjacent) |
| 苗汉词典 *Miao Han ci dian* | Long Shengguang | 2012 | Yunnan Nationalities Press | Miao (Yunnan) |

- **Gloss shape:** a 词典 of this type gives short Chinese equivalents plus
  example phrases — good for lookup.
- **Pivot wordnet: `omw-cmn` / `cow`.**
- **Why they matter:** the two Guizhou Nationalities Press Qiandong volumes are
  the single most valuable acquisitions for the **Guizhou sister project** — they
  are full-scale bilingual dictionaries of Hmu (`hea`), the variety for which
  `chenhmongmien` currently gives only 883 concepts. The Yunnan volumes are the
  closest thing to a Chinese-side Hmong Daw dictionary. Availability: Chinese
  academic booksellers, CNKI and Duxiu/超星 hold scans of many Guizhou
  Nationalities Press titles; **not verified for these specific volumes**.

**P2d. `ogde0004/hmongdict` `Dict.db`.** See B7 — the only ready-made
machine-readable Hmong–Chinese table found, licence unknown.
**Pivot wordnet: `omw-cmn`.**

**P2e. Chinese Wiktionary. Group (A), low yield.**
- **Coverage (verified via the zh.wiktionary API):** `Category:白苗語詞元`
  (White Hmong lemmas) = **62 pages**. No Green Hmong category exists.
- **Licence:** CC BY-SA 4.0. **Machine-readable:** yes — kaikki publishes a
  Chinese-edition extract, `zh-extract.jsonl` (1.9 GB, 222.5 MB gzipped) at
  <https://kaikki.org/dictionary/rawdata.html>.
- **Gloss shape:** dictionary-style short Chinese definitions.
  **Pivot wordnet: `omw-cmn`.** 62 lemmas, so a rounding error — but free.

### P3. Thai → `omw-th` (Thai Wordnet)

**P3a. Suriya Ratanakul (1972) *Photčhanānukrom Thai-Mong* (Thai–Mong dictionary). Group (C).**
- Open Library record found; entry count, publisher detail and variety
  (White vs Green Mong) **unverified**; no digital copy found. Print-only.
  Thailand-based, so the variety is very likely one of ours.
  **Pivot wordnet: `omw-th`.**

**P3b. *Sapthānukrom Thai-Khammư̄ang-Mong Khāo-Karīang Sakō̜-Mūsœ̄ Dam* (1987). Group (C).**
- Chulalongkorn University, Faculty of Arts and Faculty of Education. A
  multilingual glossary: Thai – Kham Mueang (Northern Thai) – **Mong Khao
  ("White Mong", i.e. `mww`)** – Sgaw Karen – Black Lahu. Entry count
  **unverified**; print-only. Gloss shape: a *sapthānukrom* is a glossary, so
  short equivalents — good for lookup. **Pivot wordnet: `omw-th`.**
- Bisang's (1993) fieldwork was Thailand-based and his note 1 credits the Tribal
  Research Centre, Chiang Mai; the Centre's wordlists would be the other obvious
  Thai-side source, but nothing of theirs could be located online.

### P4. Vietnamese, Lao, Khmer and Burmese → the TUFS dictionaries

**Corrected 2026-09-28.** An earlier version of this file said to write these off
for want of a pivot wordnet. That was wrong: Cygnet's `wordnets.toml` carries TUFS
basic-vocabulary dictionaries for `vi`, `lo`, `km` and `my` (plus `th`, `zh` and
`fr`), all ILI-linked and all already downloaded by the build. See the table at
the head of this section for the verified releases.

They are small, so treat them as a *confirmation* route rather than a discovery
route: a Hmong–Vietnamese or Hmong–Lao gloss that lands on the same ILI as the
English or French route is a second independent vote for that link, which is
worth more than either alone. Vietnam and Laos both have large Hmong populations,
so bilingual material exists; what was missing was the pivot, and it is not
missing any more. (The one Hmong-Mien item of Vietnamese relevance, Hsiu's Na Meo
data, is already open via `hsiuhmongmien`, A9.)

---

## David Strecker's Academia.edu corpus

Strecker's profile has **4 "Papers" and 130 "Drafts"**
(<https://independent.academia.edu/StreckerDavid>). Academia.edu serves only the
20 most recent uploads per tab and blocks paginated and proxied access, so the
listing was reconstructed from four Internet Archive snapshots of the profile
(2021-06-08, 2022-09-22, 2024-05-03, 2026-04-08), recovering **~105 distinct
titles**. Roughly 25 of them remain unseen, and two recovered ids now 404
(`47685009 A to T`, `47881607 Hairy Toadstools`) — Strecker appears to delete and
re-upload. **A complete list should be requested from him directly**; he has
already been in contact about the Hmongic classifier manuscript, so asking is
realistic.

**Nothing in the recovered set is a substantial bilingual dictionary.** The
lexically useful items, in descending order of value:

| Item | Type | Varieties | Gloss lang. | Group |
|---|---|---|---|---|
| Johnson & Strecker (2020) *An Overview of Hmong Sha (West Hmongic, Guangnan) Phonology and Lexicon* — **~600 roots with subentries** | lexicon | Hmong Sha (West Hmongic, ≈`cqd`/`mww`) | English | **B1** |
| *Classifiers and Nominalizers in Hmongic: A Preliminary Database* (`44079051`) | lexical database | Xong, Hmu, Nu, A-Hmao, White Hmong, Green Mong | English | already held |
| ~25 intensifier / expressive notes (2021–22) | word-by-word studies | `mww`, `hnj` | English | **B3** |
| *The Second Set of Hmong Clan Names* (`45020753`) | onomastic inventory — two parallel sets of Hmong clan names, Chinese-derived and native, in RPA | `mww`, `hnj` (Mong Leng source: Xyooj & Thoj 1984) | English | B |
| *Spiritual and Mundane Geography and Points of the Compass in Hmong* (`44268105`) | semantic-field study | Hmong | English | B |
| *Presyllables in Hmong-Mien* (`45476196`) — published as Strecker (2021) "The morphology and semantics of presyllables in Hmong-Mien languages", *LTBA*, DOI `10.1075/ltba.20007.str` | morphology/semantics | Hmong-Mien | English | B |
| *Nominalization, Relativization and Genitivization in White Hmong and Green Mong: A Preliminary Textual Survey* (`44080183`, `43989289`) | derivational morphology | `mww`, `hnj` | English | B |
| *Johns & Strecker (1987) White Hmong Elaborate Expressions*, *LTBA* 10(2), DOI `10.32655/ltba.10.2.08` | multiword formation | `mww` | English | B (free PDF on the profile) |
| *Three Hmong Folk Etymologies*, *What does Hmong `kheej` mean?*, *The Sound That a Tiger Makes*, *Ghosts and Other Scary Creatures*, *Tsog, the spirit that causes miscarriages* | single-item lexical/semantic notes | `mww`, `hnj` | English | B |
| ~15 glossed folktale / YouTube-transcript texts (*Txiv Nraug Ntsuag thiab Ntxawm Qaum Ntuj*, *How Youngest Daughter Killed the King*, the *mos hlub* series, …) | interlinear texts | `mww`, `hnj` | English | B |
| *Diphthongization, Syllable Structure and the Feature [High] in Hmu* (1988), *Kansas Working Papers in Linguistics* | phonology | Hmu `hea` | English | B (free PDF) |

**Licence for all of the above: none stated.** Academia.edu uploads carry no
reuse terms, so every one of these needs the author's (and for B1, Michael
Johnson's) explicit permission. Format is PDF throughout; the ones that are
born-digital manuscripts will have extractable text, but this could not be
confirmed without downloading, which Academia.edu gates behind a login.

**How this corpus would enrich the wordnet:** B1 is the substantive prize —
~600 English-glossed roots in a variety close to Hmong Daw, which is a direct
attack on the unlinked-sense problem. The rest contribute lemmas in classes
WordNet handles poorly (expressives, clan names, spirit terms) plus glossed
example sentences to attach to existing senses, and two items
(*Presyllables*, *Nominalization…*) would support derivational relations between
existing entries rather than new entries.

---

## Frame and argument-structure resources

There is **no Hmong FrameNet, no Hmong valency lexicon, and no Hmong-specific
semantic classification** that could be aligned to WordNet lexicographer files.
Checks performed: the Intercontinental Dictionary Series CLDF dataset (319
languages — **no Hmong-Mien variety at all**, verified from `cldf/languages.csv`);
OpenAlex searches for Hmong valency/argument structure; the Global WordNet
Association resource listing. What exists is descriptive literature, not a
resource:

- **Jarkey, Nerida (2015) *Serial Verbs in White Hmong*,** Brill — the fullest
  treatment of `mww` verb-complex semantics and argument sharing, with
  Jarkey (2010) "Cotemporal serial verb constructions in White Hmong" as a
  precursor. **Closed access** (verified). Print/paywalled; usable as a source of
  hand-written rules for verb classes, not as data.
- **Jarkey (2010) "Process and Goal in White Hmong"** — appears in the ANU Open
  Research CC BY collection (see C5); licence for that specific item unverified.
- **Riddle (1990) "Parataxis in White Hmong"** — relevant to multiword and
  clause-chaining semantics.
- **`nathanmwhite/classifier-semantic-modeling`** — a repo by the same author as
  `hmong-ontology`, no licence file and no description; contents unexamined. As
  the ontology's classifier semantics are already a build input, this may hold
  the modelling behind them. Worth asking him about.

**Practical conclusion:** the classifier/class-noun system (Bisang's appendices,
already in the build, plus Strecker's classifier database) is the closest thing
Hmong has to a native semantic classification, and it is already being used.
Argument structure would have to be hand-built from Jarkey.

---

## Not worth pursuing

- **PanLex live API** — `api.panlex.org` and `db.panlex.org` do not resolve;
  use the Zenodo OntoLex snapshot or contact PanLex.
- **OPUS / JW300 / Bible parallel corpora** — verified against the OPUS API: the
  *only* corpus in all of OPUS containing `mww` or `hnj` is Tatoeba, with
  **91 sentence pairs for `mww` and 4 for `hnj`**. No JW300, no bible-uedin,
  no CCAligned coverage. Negligible.
- **Tatoeba** — the `mww` collection returns 9 sentences. Negligible.
- **eBible.org** — 1,551 translations listed, **zero** Hmong (grepped the
  translations CSV for `hmong`, `hmn`, `mww`, `hnj`). The major Hmong Bible
  editions (*Vajtswv Txojlus*, *Vaajtswv Txujlug*) are under Bible-society
  copyright and are not in any open corpus; JW.org's large Hmong holdings are
  likewise all-rights-reserved.
- **Wikidata lexemes** — verified by SPARQL: **6 lexemes for `mww`, 0 for `hnj`**.
- **A Hmong-language Wiktionary or Wikipedia** — does not exist. Verified against
  the Wikimedia `sitematrix` API: no `hmn`, `mww` or `hnj` project of any kind.
- **French Wiktionary** — `Catégorie:hmong blanc` has **1 page**,
  `Catégorie:hmong vert` **0**. Not a viable French pivot; use Freelang/PanLex.
- **DBnary** — extracts per Wiktionary *edition* for a couple of dozen major
  edition languages; Hmong is not an edition, so Hmong appears only as
  translation targets already better served by kaikki.
- **FreeDict** — verified against `freedict-database.json`: 306 dictionaries,
  **no Hmong**.
- **Apertium** — GitHub org search: **no Hmong language pair or monolingual data**.
- **Existing Hmong wordnet / OMW entry / ILI proposal set** — none. Verified
  against the `wn` lexicon index (80 ids, no Hmong), the Open Multilingual
  Wordnet site, and the GWA "wordnets in the world" page (which does not mention
  Hmong or Miao). OpenAlex turns up no paper on a Hmong wordnet. **We are first.**
- **Intercontinental Dictionary Series** — 319 languages, no Hmong-Mien. The
  `Borin-2015-1532` bridge cannot be extended through IDS.
- **Concepticon conceptlists other than Borin** — only `Borin-2015-1532` (1,373
  distinct Concepticon IDs) and `Borin-2012-40` (40 items, bomb/…) are
  WordNet-annotated among the 481 conceptlists. There is no general
  Concepticon→ILI mapping to be had; the Borin route is the only one.
- **SEAlang Library** — has Thai, Lao, Khmer, Burmese, Shan, Karen, Mon,
  Vietnamese, Malay, Indonesian, Javanese, Balinese, Maranao, Maguindanao.
  **No Hmong dictionary** (`sealang.net/hmong/` 404).
- **Webonary (SIL)** — could not be checked; `webonary.org` returns HTTP 403 to
  every non-browser client tried, including through a text proxy. Needs a manual
  browser check for a Hmong dictionary; not verified either way.
- **IMTVault** — Glottolog links `[mww] at IMTVault`, but the site currently
  serves a JHipster build-error page instead of data. Re-check later.
- **Glosbe, MUSE** — Glosbe has no bulk export and no usable API; MUSE's
  bilingual dictionaries do not include Hmong.
- **Glottolog reference lists** — the `.bib` endpoint returns HTTP 406 and
  `langdoc.csv?languoid=…` ignores the filter, so per-languoid dictionary
  bibliographies could not be extracted. Not worth further effort; Open Library
  and the PanLex source list covered the same ground.
- **Lexibank `starostinhmongmien`** — already in the build; for the record it
  covers 20 varieties including the only direct `mww` (Hmong Daw) and `hnj`
  (Hmong Njua) rows in Lexibank, but only **110 Concepticon sets**, of which
  95 are Borin-linked. `chenhmongmien` supersedes it on breadth.

---

## Second pass, 2026-09-28

The searches the first pass could not run. Two corrections to this file's own
earlier conclusions are recorded inline below: the PanLex licence question is
**resolved against us**, and the World Loanword Database turned out to hold a
large openly-licensed White Hmong vocabulary the first pass missed entirely.

---

### Closing the verification gaps

Follow-up to `RESOURCES.md`. General search engines were available for this pass,
which the first pass lacked. Everything below is marked **verified** (I fetched
the page, file or API myself and read the value), **reported** (a search engine
returned the claim but the canonical page could not be fetched directly), or
**unverified**.

Chinese-language sources are deliberately excluded — another agent covers those.

Tooling note: `sil.org`, `academia.edu`, `webonary.org`, `conservancy.umn.edu`
and `panlex.org` all sit behind bot protection. A browser `User-Agent` on `curl`
is enough for `sil.org` record pages; Academia.edu and Webonary refuse it
(Cloudflare interstitial); `conservancy.umn.edu` refuses the HTML but serves
OAI-PMH at `/server/oai/request`. `archive.org` was **entirely offline** during
this pass ("Internet Archive services are temporarily offline"), so no Internet
Archive holdings could be re-checked.

---

#### Gap 1 — Webonary (SIL): no Hmong dictionary found

**Status: closed as a negative, with a caveat.**

What I tried:

- `webonary.org` and `www.webonary.org` return **HTTP 403** with a Cloudflare
  "Just a moment…" interstitial to `curl` with a browser `User-Agent`, to
  WebFetch, and to the WordPress REST route `/wp-json/wp/v2/sites`. The
  `/browse-dictionaries/` page is blocked the same way, with and without a
  `?lang=` filter. Direct fetching is not possible without a real browser.
- Two general web searches, plus one search **restricted to the `webonary.org`
  domain** ("Hmong dictionary"). The domain-restricted search returned ten
  distinct Webonary dictionaries — Chin (Falam), Bualkhaw Chin, Mungong, Mbuko,
  Sango, Burmese, Burushaski Hunza, Lohorung — and **no Hmong, Mong, Miao or
  Hmu dictionary**. Individual Webonary entry pages *are* indexed by search
  engines, so a Hmong Webonary would be expected to surface.

**Conclusion:** there is very probably no Hmong dictionary on Webonary. This
fits the wider picture: SIL East Asia's Hmong output is deposited in the SIL
Language & Culture Archives (see Gap 2) rather than published as a Webonary.
**Not proof** — a Webonary can be set to private, in which case no search engine
would see it. A one-minute browser check of `webonary.org/browse-dictionaries/`
would settle it; I could not perform one.

---

#### Gap 2 — SIL Wenshan Hmong Survey Wordlist: found

**Status: closed.** This is the Honghe wordlist's companion, and the survey was
right that it matters more: Wenshan is the core `mww`/`hnj` area in China.

### A5b. SIL — *Wenshan Hmong Survey Wordlist Data* (Castro, Flaming & Cohen, 2008–09)

- **What it is:** field wordlist data from the SIL East Asia Hmong dialect
  survey in **Wenshan Prefecture, Yunnan**. Edited IPA transcriptions of every
  wordlist collected, plus a separate data-point description file and a separate
  wordlist-notes file. "Audio files are available upon request."
- **Coverage (verified from the SIL record):** "**447 words; 15 data points**" —
  five more survey points than Honghe's ten, on a slightly shorter list.
- **Varieties (verified):** subject language Hmong `[hmn]`; content languages
  **Mandarin Chinese `[cmn]`, Chuanqiandian Cluster Miao `[cqd]`, Hmong Shua
  `[hmz]`, Hmong Daw `[mww]`**. Scripts: Han (Simplified) and Latin.
- **Gloss language — important difference from Honghe:** the record states "All
  filenames and content are in **Chinese** except for Hmong variety names, which
  are written in Latin script." Content Language lists `cmn` but **not `eng`**,
  whereas the Honghe record lists `eng`. So unlike Honghe, **this set is very
  likely Chinese-glossed only**, and it feeds the Chinese pivot rather than the
  English route. Treat as probable until the file is opened.
- **Licence / availability:** same posture as Honghe — **no explicit licence**;
  "Publication Status: Draft (posted 'as is' without peer review)"; the page
  footer carries only "Copyright © 2026 SIL Global | Terms of Use". Freely
  downloadable in a browser, not openly licensed. Ask SIL before redistributing.
- **URL:** record <https://www.sil.org/resources/archives/87099> (Entry Number
  87099). File: `Wenshan_Hmong_Survey_Wordlist_Data__Text_.zip`, **221.05 KB**,
  linked from that page at
  `https://www.sil.org/system/files/reapdata/95/83/97/95839777298171138207510820730471238063/Wenshan_Hmong_Survey_Wordlist_Data__Text_.zip`.
  **I could not download it:** the `/system/files/` CDN path returns HTTP 403 to
  `curl` even with a browser `User-Agent`, a matching `Referer` and a cookie jar.
  **Needs a browser download.** File contents therefore unverified.
- **Machine-readable:** a ZIP of text files (the record's "(Text)" qualifier,
  against an `.xlsx` for Honghe), so format per file unverified.
- **Related record, same survey, also not in the survey:**
  *Southeastern Yunnan Hmong Survey Recorded Text Testing Recordings and
  Transcriptions* — <https://www.sil.org/resources/archives/93755> (metadata
  unverified; RTT material, so intelligibility data rather than lexicon).
- **Companion publication (verified to exist):** Castro, Andy & Gu Chaowen
  (2010) *Phonological innovation among Hmong dialects of Wenshan* —
  <https://www.sil.org/resources/archives/3692>, also on Academia
  (`44730663`-adjacent: `https://www.academia.edu/9626316/`) and ResearchGate
  publication 258898455.
- **How it would enrich the wordnet:** 447 concepts × 15 Wenshan points with
  `mww`/`cqd`/`hmz` labelling is the densest China-side sampling of our own two
  varieties' home region; with Chinese glosses it feeds the `omw-cmn` pivot and,
  via shared concepts, cross-checks the Honghe set's English glosses.

---

#### Gap 3 — PanLex licence conflict: resolved, and Freelang overrides it anyway

**Status: closed. The answer is more restrictive than either option in the brief.**

### Three findings

**(a) PanLex's own statement is CC BY-NC-SA 4.0, still (verified 2026-09-28).**
<https://panlex.org/license/> reads: "PanLex materials are a part of the PanLex
project of The Long Now Foundation, and are shared under the **Creative Commons
Attribution-NonCommercial-ShareAlike 4.0 International License**" and
"Commercial use of these materials is permitted only by obtaining written
permission from PanLex." The page makes **no mention of CC0** and says nothing
about the rights of the underlying source dictionaries. (Search-engine summaries
claiming PanLex distributes snapshots under CC0 appear to describe an older
version of the page or the `panlex.org/snapshot` route; the live licence page
does not say it. Do not rely on the CC0 claim.)

**(b) The Zenodo CC0 tag does not govern — the record itself says so
(verified via the Zenodo API, record 6757353).** The `license` metadata field is
`{"id": "cc-zero"}`, but the record's own description ends:

> "Licensing follows the original data. See PanLex batch on language metadata."

The depositors are Chiarcos, Fäth & Ionov (Goethe University Frankfurt), who
converted PanLex to OntoLex-Lemon; they are not the rights holders in the data.
`cc-zero` is best read as covering their conversion, with the data's own terms
passed through. **Therefore PanLex's CC BY-NC-SA 4.0 governs reuse of the
derived data, and the NC clause is incompatible with a CC BY wordnet release.**

**(c) For the Freelang dictionary specifically, PanLex's aggregation licence is
irrelevant — the compiler's permission is required.** Freelang's own conditions
(<https://www.freelang.com/dictionnaire/dic-copyrights.php>, verified):

- Art. 2 — "Les listes de mots sont la propriété de leurs auteurs." The word
  lists belong to their individual compilers, not to Freelang.
- Art. 4 — public online redistribution requires Freelang's consent; private or
  in-house professional use is allowed.
- Art. 11 — the word lists "ne peuvent donc pas être converties et distribuées à
  un autre format": **converting to another format and distributing it is
  expressly forbidden**, which is exactly what a wordnet build does.
- Art. 17 — "Les auteurs sont seuls habilités à autoriser la distribution ou
  l'exploitation de leur liste de mots par un tiers." Only the compiler can
  authorise third-party use.

So PanLex's ingestion did not launder the rights. **Practical route: write to
Aymeric Dourthe (via Freelang) for permission.** That is a single, tractable
request for the best French pivot we have, and it is independent of the PanLex
question.

### Corrections to P1a

- **The compiler is Aymeric Dourthe, not Christian** (verified on the Freelang
  page, "© Aymeric Dourthe").
- **Entry counts as Freelang now distributes them are much smaller than PanLex's
  (verified on <https://www.freelang.com/dictionnaire/hmong.php>):
  hmong→français **3,042 words**, français→hmong **2,872 words**; first
  published 2005-10-14, last updated 2014-03-21.** PanLex's 7,580 / 7,476 are
  presumably denotations or translation pairs rather than headwords, or come
  from a different edition. Either way, **do not plan on ~7,500 French-glossed
  headwords; plan on ~3,000.** This materially reduces P1a's expected value.
- Freelang *also* has a separate **Hmong–English** dictionary, compiler
  **Renato B. Figueiredo**, **8,864 entries** (verified on
  <https://www.freelang.net/online/hmong.php>), under the same conditions. Not
  in the survey. Same permission route; larger than the French one, and it
  targets the English route directly. `© Beaumont 1997-2026` for the site.
- Variety for both is unstated on the Freelang pages (the French page mentions
  both "hmong vert" and "hmong blanc"), so PanLex's `hnj` label remains
  unconfirmed.

---

#### Gap 4 — Strecker and Johnson: contacts, and a non-Academia copy of the dictionary

**Status: contact route found for Strecker; Johnson's contact not found.**

### Strecker, David — contact and permission path

- **Email `davidstrecker950@gmail.com` is confirmed as his own** — I downloaded
  the *Mong Leng – English Dictionary, revised* PDF and read it: the address is
  on p. 1 under his name, dated July 14, 2021, and the PDF's `Author` metadata
  field is "David Strecker". **Currency: cannot be proved.** The same address is
  reported by a search engine on a Scribd upload of his
  *Ntxwj Nyoog, Nyaj Vaab and Saub* (Scribd document 849392404), which is a
  later item than the dictionary, so the address was still in use after 2021.
  It is the only address he publishes.
- **No institutional affiliation.** He posts as an independent scholar
  (`https://independent.academia.edu/StreckerDavid`). No ORCID, personal site or
  university page was found.
- **Second, non-Academia route (new):** a Hmong community site, *Kawm Ntawv
  Moob*, **`https://moob.workwithyang.com/`**, mirrors his dictionary publicly
  with no login —
  `https://moob.workwithyang.com/wp-content/uploads/2022/05/Mong_Leng_English_Dictionary_revised.pdf`
  (verified: HTTP 200, **6,869,521 bytes**, 995 pages, uploaded 2022-05-11).
  Its WordPress REST media index (`/wp-json/wp/v2/media`) lists 18 files
  including `The_Phonetic_Inventory_of_Mong_Leng.pdf` (added 2026-09-27) and
  1982 Mhong Language Council conference papers. Strecker evidently already
  permits informal community redistribution — useful context for the ask,
  **not** a licence.
- **Third route:** the *Hmong Studies Journal* publishes him open-access
  (e.g. "Dragons, Tigers, and Taoism",
  `https://www.hmongstudiesjournal.org/uploads/4/5/8/7/4587788/strecker_hsj_22.pdf`),
  so the HSJ editors are an alternative way to reach him.
- **The dictionary's own front matter names the people to credit and ask:** his
  late wife **Brenda Johns** (co-translator over several decades; the
  Johns & Strecker 1987 elaborate-expressions paper is hers too), **Michael
  Johnson**, **Djoua Xiong / Xeev Nruag Xyooj** (director of Mong Volunteer
  Literacy), **Lopao Vang**, and **Nathan White** — who "commented on the
  examples … and made a number of important suggestions regarding the
  organization and presentation of this dictionary". **Nathan White is already
  an acknowledged contributor to this dictionary and is the author of our own
  base ontology. He is the obvious person to broker the permission request.**

### Johnson, Michael — affiliation and contact **not found**

- **Academia profile located:** `https://independent.academia.edu/mikejohnson247`
  (reported by a search engine; the page itself returns Cloudflare 403). Listed
  as an **independent scholar**, so no institutional address.
- **Publication trail (reported, not fetched):** "Far-western Hmongic" (1998);
  a paper on tone and phonation in Western A-Hmao, *SOAS Working Papers in
  Linguistics* 9 (1999) — implying a **SOAS** connection in the late 1990s;
  "The Reconstruction of Labial Stop + Sonorant Clusters in Proto-Far-Western
  Hmongic", *Transactions of the Philological Society* 100(1) (2002).
- **What Strecker's front matter says about him (verified):** Johnson "has been
  doing research on phonological reconstruction and comparison based on his
  fieldwork on a large number of different Hmong dialects in China, Vietnam, and
  Thailand", works with Mong Leng Bible translations, and has expertise in
  **Southwestern Mandarin**, which he used to add the Chinese etymologies that
  make Strecker's dictionary "two dictionaries", the second "an etymological
  dictionary of Sino-Mong".
- **No email, ORCID, institutional page or personal site found.** His fieldwork
  profile in Yunnan, the Bible-translation work and the 2002 TPS paper are all
  consistent with SIL East Asia Group, but **I did not verify any SIL
  affiliation and it should not be assumed.**
- **Recommendation: go through Strecker.** He is in daily contact with Johnson
  ("continued conversations"), and one email to Strecker can cover both the
  Mong Leng dictionary and the Hmong Sha lexicon.

### Johnson & Strecker (2020) *Hmong Sha* — citation and copies

- **Canonical citation:** Johnson, Michael & David Strecker. 2020. *An Overview
  of Hmong Sha (West Hmongic, Guangnan) Phonology and Lexicon*. Manuscript,
  Academia.edu. No journal, no DOI, no publisher — **verified absent**: no
  OpenAlex/Crossref record surfaced, and the only hosts found are Academia.edu
  (`44730663`, near-duplicate `44589444`).
- **No non-Academia copy exists that I could find.** The *Kawm Ntawv Moob*
  mirror does not hold it; its media index is complete and I read it.
- **It is one of a series, and the survey records only this member.** Reported
  companions, same title pattern, likely the same authorship:
  - *An Overview of **Hmong Sa** (West Hmongic, Thailand ex. Myanmar) Phonology
    and Lexicon* — `https://www.academia.edu/44813266/`
  - *An Overview of **Mong Shi** (West Hmongic, Pingbian) Phonology and Lexicon*
    — `https://www.academia.edu/50648935/`; described as "the phonology and
    lexicon of Mong Shi as recorded from the idiolect of a single elderly
    speaker", Pingbian county, Yunnan, "a member of the **Mong Leng cluster**
    within the Farwestern Hmongic branch". **Mong Leng cluster means this one is
    `hnj`-adjacent**, our weaker variety — potentially more valuable to us than
    Hmong Sha. Entry counts, authorship and licence **all unverified**
    (Academia.edu 403).
  - *The Phonetic Inventory of Mong Leng* — `https://www.academia.edu/879745/`,
    and a copy on the *Kawm Ntawv Moob* mirror (see above). Note a **different**
    document with the same title by Daniel Bruhn at
    `http://linguistics.berkeley.edu/~dwbruhn/dwbruhn_mong_leng.pdf` — a
    Linguistics 110 student project; do not confuse them.
  - Ask for the whole series in the same email.

### Xiong, Xiong & Xiong (1983) — identified; the survey's C2 entry was wrong

The survey could not locate this and substituted a different, later Xiong work.
It exists, and it is the **source of most of Strecker's dictionary**.

- **Canonical record (reported from WorldCat and Glottolog):** Xiong, Lang,
  Joua Xiong & Nao Leng Xiong. 1983. *English–Mong–English Dictionary = Phoo
  txhais lug Aakiv–Moob–Aakiv*. Milwaukee, Wisconsin: **Xiong Partnership**.
  **vii + 570 pp.** OCLC **10519328**; Glottolog reference id **323062**
  (`https://glottolog.org/resource/reference/id/323062`). Also catalogued in the
  UW–Madison Hmong Studies bibliography (`HmongStudies1639`) and referenced by
  WALS. A related 1984 item by Xiong, Lang, William J. Xiong & Nao Leng Xiong is
  Glottolog reference 699799.
- **Variety:** Mong Leng / Green Mong (`hnj`), in **standard RPA** — Strecker
  chose it over Lyman for exactly this reason.
- **Verified from Strecker's front matter:** its appendices are "verb
  intensifiers (pp. 553-556)" and "color intensifiers (pp. 556-557)", which
  corroborates the 570-page extent. Strecker incorporated "everything from the
  Mong-to-English section … and everything from the Xiongs' appendices … as well
  as some material from the English-to-Mong section".
- **Availability / rights:** privately printed, in copyright, **no digital copy
  found anywhere** (no Internet Archive item — though IA was offline and could
  not be re-checked — no HathiTrust hit, not in the PanLex source list). Library
  copies only; OCLC 10519328 is the route via interlibrary loan.
- **Practical conclusion, as you say:** since its Mong→English section is
  absorbed into Strecker's dictionary, the original is worth acquiring only for
  (i) the **English→Mong** section, which Strecker used only partly, and
  (ii) an independent check on his transcription. Rights would have to come from
  the Xiong family, which is likely to be much harder than asking Strecker.

### Mong Volunteer Literacy, Inc. — identified, nothing online

- **Verified from Strecker's front matter:** "a cultural and educational
  organization in Illinois"; its director is **Djoua Xiong (Xeev Nruag Xyooj)**,
  who sent Strecker and Johns the publications and answered their questions; its
  magazine is ***Txooj Moob*** ('the Mong Community'); its logo is "a clump of
  bamboo with three birds … surrounded by the words Mong Volunteer Literacy,
  Inc." Strecker cites *Txooj Moob* by issue and page throughout, e.g.
  "(Txooj Moob No. 2, p. …)".
- **Reported bibliographic detail:** based in **Winfield, Illinois**; known items
  include Xeev Nruag Xyooj, "Txooj Moob Huv Nplaj Teb" in *Txooj Moob* vol. 4
  (May 1989); "Ntaub Ntawv Moob" in *Txooj Moob* no. 5, pp. 3–9 (1990); and
  *Moob Kev Dlaab Qhuas Txawm Qhov Twg Lug?* (1985). Djoua X. Xiong was in
  Wheaton, Illinois in 1992.
- **Availability: nothing found online.** No digital copies, no library holdings
  surfaced, no organisational website; the organisation appears defunct (do not
  confuse it with *Literacy Volunteers of Illinois*, a different body). Strecker
  himself says their publications are "very rich and there is much in them that
  Brenda and I did not get to" — so **he holds the only accessible copies I can
  find, and the ask should include them.**
- ***Tswv Yim Moob* (Mong Ideas) by Laaj Soobleej Hawj**, Milwaukee, no date:
  **not found in any catalogue or online.** Strecker's copy came from Lopao Vang.
  He says it "has a tremendous amount of information on different aspects of
  Mong culture and history, of which Brenda and I read and translated only a
  small portion". Same conclusion: ask Strecker or Lopao Vang.
- One text on the *Kawm Ntawv Moob* mirror may be from this milieu:
  `MOOB-KAAB-LEG-KEV-CAI.pdf` (2022-11-30). Contents unverified.

---

#### Gap 5 — Entry counts and scans for the print dictionaries

**Status: largely closed. The big result is that full scans of Heimbach, Lyman
and Bertrais are openly downloadable from a source the survey did not know
about — with a serious rights caveat.**

### The source: RENINC (Refugee Educators' Network) bookshelf

`http://www.renincorp.org/bookshelf/` (also `reninc.org`) — verified: an HTML
index, last modified 2015-09-01, listing ~100 full-text PDFs on Hmong, Lao and
Southeast Asian material. It is linked from a curated Hmong linguistics resource
list (see Gap 7), so it is not obscure. **Rights: these are scans of works still
in copyright, with no evidence of permission on the site.** Cornell SEAP,
Mouton/De Gruyter and the Mission Catholique are the rights holders. Treat
RENINC as a **research convenience for counting and checking, not a source you
can build from or cite as an open licence.** Everything I report below was
measured from these scans; the permission questions are unchanged.

### B2. Heimbach (1969/1979) *White Hmong–English Dictionary* — count found

- **Edition verified from the scan's title page:** "1979 Revised Edition",
  Cornell Southeast Asia Program, Linguistic Series IV, **Data Paper Number 75**,
  August 1979, price $6.50, ISBN 0-88727-075(-9); "© 1966, 1969, 1979 Cornell
  Southeast Asia Program"; "First published by the Cornell Southeast Asia
  Program in 1969 under the title, *White Meo-English Dictionary*."
- **Entry count — "over 4,900 definitions" (reported).** This is the publisher's
  blurb, returned consistently by search engines from the Cornell University
  Press, Amazon and other retail listings for ISBN 9780877270751. I could **not**
  verify it on the canonical page: `cornellpress.cornell.edu` serves a
  JavaScript-rendered shell (562 KB of HTML with no description text), and the
  string "4,9" does not occur in the served HTML. The figure does not appear
  anywhere in the book's own front matter either (I searched pp. i–xxxiv of the
  scan).
- **My own independent count: 4,476 main-entry lines.** Method, stated so you
  can discount it: `pdftotext -bbox-layout` over the dictionary body (PDF pp.
  30–292) of the RENINC scan, 27,759 text lines; main entries sit at the left
  margin of each of the two columns (x ≈ 35–45 and x ≈ 415–420) while
  sub-entries are indented to x ≈ 65–80 / 445–455; I counted margin lines
  matching an optional homograph number plus a headword. **1,980 distinct head
  forms**, i.e. ~2.3 numbered senses per form — Heimbach numbers homographs
  heavily (`1. hnav`, `2. hnav`, up to `7. pos`). Sampling 30 at random showed
  ~28 true main entries and ~2 artefacts. **So "about 4,500–4,900 main entries"
  is well supported; the publisher's 4,900 and my 4,476 corroborate each other
  within OCR error.**
- **Scans:** full PDF at
  `http://renincorp.org/bookshelf/white-hmong-english-diction.pdf`
  (verified: 13,358,526 bytes, **310 pages**, Adobe "Paper Capture" OCR, so it
  **has a text layer** — imperfect but usable, e.g. `l u b` for `lub`, letters
  spaced out). A second full copy at
  `https://studyhmong.com/wp-content/uploads/2012/09/whitehmongdict.pdf`
  (reported). Also on **HathiTrust, Limited (search-only) view**,
  `babel.hathitrust.org/cgi/pt?id=mdp.39015029511816` (reported), and on
  document-sharing sites (dokumen.pub, vdoc.pub) — all unauthorised.
  The Internet Archive item `whitehmongenglis00erne` remains
  **lending-only** per the survey; IA was offline so I could not re-check.
- **Practical consequence:** the OCR text layer in the RENINC scan means the
  4,476 head forms and their English glosses are **extractable now**, without
  waiting for PanLex. The blocker is purely permission (Cornell SEAP), not
  technology. Given Heimbach's centrality, **a licence request to Cornell
  University Press for a 1979 Data Paper is worth making** — it is a
  long-out-of-print $6.50 pamphlet, and CUP has an open-access programme
  ("Cornell Open").

### C1. Lyman (1974) *Dictionary of Mong Njua* — count not obtained

- **Extent verified:** the RENINC scan is
  `http://www.renincorp.org/bookshelf/dictionary-of-mong-njua_lym.pdf`
  (14,103,732 bytes, **397 PDF pages**, Paper Capture OCR). The *Bulletin of
  SOAS* review gives **403 pp.** (reported; review PDF at
  `cambridge.org/core/…/S0041977X00051521a.pdf`). Janua Linguarum, Series
  Practica **123**; Mouton, The Hague/Paris; LC card 72-94484; ISBN
  9789027926968; now De Gruyter, DOI **10.1515/9783110810813**. The dictionary
  proper runs PDF pp. 65–379, followed by appendices (an English index) to p. 397.
- **Entry count: NOT obtained, and I recommend not guessing one.** I ran the
  same bbox method and it failed: Lyman uses **his own idiosyncratic phonetic
  transcription** with diacritics and superscript tone digits, which the 1970s
  Paper Capture OCR mangles badly (`chdu`, `6 6 ~ 1`, `~ 4 0 q`, `$50`), so
  margin lines cannot be reliably classified as entries. A candidate count of
  1,221 at the left margin was ~50% noise on inspection. No review or catalogue
  I found states a count. **Still unverified.** A count would need re-OCR or a
  page-sample extrapolation by hand.
- **Rights/availability:** in copyright, De Gruyter Brill. No authorised digital
  copy. Still print-only in practice. Note Strecker's verified judgement on it:
  "Lyman's dictionary is not comprehensive. Time and time again, Michael would
  look for a particular word … and fail to find it in Lyman", plus the
  transcription burden. **Given that we now have Strecker's 4,442-sense RPA
  `hnj` dictionary, Lyman drops sharply in priority** — it is worth pursuing only
  as an independent check and for its plant/animal/kinship/clan-name coverage.
- **Related, and openly available:** Lyman's **Grammar of Mong Njua (Green
  Miao)** is on the Internet Archive as `rosettaproject_blu_phon-1` (reported),
  i.e. in the **Rosetta Project** collection — which normally means openly
  viewable rather than lending-only. Worth checking when IA is back up; a
  grammar is not a lexicon, but Rosetta items often include a wordlist.

### C2b. McKibben (1992) *English–White Hmong Dictionary* — still unverified

Open Library work `/works/OL3990874W` (from the first pass). Nothing new: no
entry count, no digital copy, no review found. **Gap remains open.** I spent one
search on it; it is a low-value target now.

### B6 / P1b. Bertrais (1964/1979) *Dictionnaire hmong (mèo blanc)–français* — author's own figure found

- **The author states the extent himself.** From the preface of the RENINC scan
  (`http://www.renincorp.org/bookshelf/dictionaire-hmong-francais_.pdf`,
  verified: 20,599,840 bytes, **584 pages**, Paper Capture OCR of a typescript):

  > "Il doit y avoir environ **30.000 lignes** dans ce dictionnaire. Ce qui ne
  > veut pas dire qu'il s'y trouve 30.000 mots et expressions."

  So **~30,000 lines, explicitly *not* 30,000 headwords**. This is the only
  quantitative statement in the book and the author declines to convert it into
  an entry count. **Entry count therefore remains unverified**, but the extent is
  now bounded: a 584-page dictionary with ~30,000 lines of which headwords are a
  minority — plausibly several thousand headwords with many sub-entries, i.e. the
  same order as Heimbach but with more example material.
- **Other verified facts from the preface:** Bertrais had been a missionary among
  the Hmong of Luang Prabang, then Sam Neua and Xieng Khouang, for 14 years; the
  team included **Yaj Teab**, **Thoov Yeeb Yaj**, **Nom Yaj**, **Lauj Taab, Lauj
  Ntxiv, Lis Teev**; work restarted in **April 1961** after the first eleven
  years' material was lost, and stopped in **November** (year OCR-damaged). He
  states plainly that **no prior Hmong dictionary or lexicon existed** when he
  began ("nous n'avons pas trouvé de dictionnaire ou lexique en Hmong Blanc"),
  and that the work represents mainly the **White Hmong of the Luang Prabang
  region**, adding that White Hmong from Tonkin to the Thai and Burmese borders
  is "étonnamment unifié". He deliberately **omitted onomatopoeia** and much
  ritual/poetic vocabulary — relevant to us, since expressives are precisely the
  class Strecker documents.
- **Gloss shape confirmed:** the sample pages show short French equivalents plus
  full example sentences with translations — so it is richer but noisier for
  automatic pivoting than Freelang.
- **Rights:** in copyright (Mission Catholique / Institut de l'Asie du Sud-Est).
  The RENINC scan is not an authorised copy. Open Library `/works/OL6353994W`.
- **Revised assessment:** with the scan's text layer, Bertrais is now
  *technically* extractable, and at 584 pages it is a much larger French source
  than Freelang's ~3,000 entries. **It is now the better French pivot target of
  the two, and the permission holder (the Oblate mission / IASE) is a single
  identifiable body.** That is a change from the survey's ranking.

### Bonus: Xiong, Xiong & Xiong (1983) — see Gap 4, vii + 570 pp, OCLC 10519328.

---

#### Gap 6 — IMTVault: working, and it does hold Hmong

**Status: closed.** The website is still useless to a script, but the data is
elsewhere and is easy to use.

### A10. IMTVault — interlinear glossed text, CLDF

- **What it is:** interlinear glossed text (IGT) automatically extracted from
  LaTeX sources of open-access linguistics publications — Language Science Press
  books and CLDF-published typological databases — then enriched with Glottolog
  and Wikidata links. Krämer & Nordhoff (2022), LREC/LDL workshop.
- **The website is not the access route.** `imtvault.org` returns HTTP 200 but
  serves a 4,010-byte JavaScript single-page-app shell for every path, including
  `/languages/mww`; no data reaches a non-browser client. The survey's
  "build-error page" has become an empty SPA. **Use the CLDF release instead:**
  <https://github.com/cldf-datasets/imtvault> (Zenodo record 19947331).
- **Hmong coverage (verified from `cldf/languages.csv` and `cldf/examples.csv`,
  fetched today):**

  | Glottocode | Name | Examples |
  |---|---|---|
  | `hmon1333` | Hmong Daw (`mww`) | **90** |
  | `hmon1264` | Hmong Njua (`hnj`) | **12** |

  Total **102**. Provenance, verified from `Contribution_ID`:
  - **90 of the 90 `mww` examples come from one book:** Guérin, Valérie (ed.)
    2018. *Bridging constructions* (Studies in Diversity Linguistics 24), Berlin:
    Language Science Press, DOI **10.5281/zenodo.2563698**. These are
    **connected narrative**, not elicited sentences — running folktale text
    (`nraug zaj` 'young dragon', `Luj Tub`) in RPA with morpheme-by-morpheme
    glosses and free translations.
  - 11 `hnj` examples from **WALS** (Dryer & Haspelmath 2024) and 1 from
    **Ditransitive constructions** (Malchukov & Haspelmath 2024) — pronoun
    paradigms and the like (`kuv` 1SG, `wb` 1DL, `peb` 1PL).
- **Licence:** the IMTVault CLDF repo has no SPDX licence field, but every source
  it draws on is CC BY (Language Science Press books, WALS, the CLDF databases),
  and each example carries its `Source` and `Contribution_ID` so attribution is
  mechanical. **Cite the released version plus the originating publication.**
  Treat individual examples as CC BY from their source book.
- **Machine-readable:** yes — CLDF; `examples.csv` is 50.7 MB with columns
  `Primary_Text`, `Analyzed_Word`, `Gloss`, `Translated_Text`, `LGR_Conformance`,
  `Corpus_Reference`, `Source`.
- **How it would enrich the wordnet:** small, but it is **glossed running text
  with morpheme-level English glosses**, which is the right shape for attaching
  usage examples to senses and for confirming POS. 90 `mww` sentences is a
  rounding error next to `sch-corpus`, but unlike `sch-corpus` they are
  *glossed*, and the `hnj` dozen are worth having for a variety with 61
  Wiktionary lemmas. **Better move: go to Guérin (ed.) 2018 directly** — it is
  CC BY, and the Hmong chapter there will have more material than IMTVault
  extracted. (Chapter author unverified.)

---

#### Gap 7 — General sweep: one major miss, and several smaller ones

### The major miss: WOLD's White Hmong vocabulary (Ratliff)

**This is the highest-value find of the whole pass, and it is CC BY, direct
`mww`, and already Concepticon-linked to the exact bridge we use.**

### A0. WOLD / Lexibank `wold` — *White Hmong vocabulary* (Martha Ratliff)

- **What it is:** one of the 41 language vocabularies of the **World Loanword
  Database** (Haspelmath & Tadmor 2009), a per-language elicitation of the
  **LWT (Loanword Typology) 1,460-meaning list** with, for every word, the
  meaning it expresses, a borrowing judgement on a 5-point scale, an
  etymological note, age, analysability and frequency. The White Hmong
  vocabulary is **by Martha Ratliff** — the author of *Hmong-Mien Language
  History* (A2), so provenance and transcription match a source already in the
  survey.
- **Coverage (verified by counting `cldf/forms.csv` and joining
  `cldf/parameters.csv`):**
  - **1,474 word forms** for `Language_ID = WhiteHmong`
  - across **1,298 distinct LWT meanings**
  - mapping to **1,295 distinct Concepticon concept sets**
  - **of which 1,210 are Borin-2015-1532–linked, i.e. ILI-reachable through the
    bridge already in the build.**
  - For scale, using the survey's own metric: `starostinhmongmien` contributes
    95 Borin-linked sets, `chenhmongmien` 473, and the whole `Borin-2015-1532`
    list has 1,373. **WOLD alone covers 1,210 of those 1,373 — 88% of the entire
    bridge — for `mww` directly.** (The LWT list as a whole overlaps Borin on
    1,360 of 1,373 ids; White Hmong fills 1,210 of them.)
  - The WOLD web page states "1,472 meaning-word pairs corresponding to core LWT
    meanings" (verified on the site); my 1,474 is the CLDF form count, so the two
    agree.
- **Varieties:** **White Hmong, ISO `mww`, Glottocode `hmon1333`** — verified
  from `cldf/languages.csv` row 26:
  `WhiteHmong,White Hmong,hmon1333,Hmong Daw,mww,Eurasia,26,105,Hmong-Mien,25`.
  **No Green Mong vocabulary** in WOLD (`mww` is the only Hmong-Mien language in
  the database).
- **Licence:** the CLDF dataset <https://github.com/lexibank/wold> carries
  **CC-BY-4.0** (verified via the GitHub API `license.spdx_id`). The WOLD web
  edition states **CC BY 3.0 Germany** (verified on the site). Either way it is
  **openly reusable with attribution — group (A), no permission needed.**
- **URL:** <https://wold.clld.org/vocabulary/25> (web) ·
  <https://github.com/lexibank/wold> (CLDF) · underlying publication:
  Haspelmath, Martin & Uri Tadmor (eds.) 2009. *Loanwords in the World's
  Languages*. De Gruyter Mouton.
- **Machine-readable:** yes — CLDF, `cldf/forms.csv` (17.4 MB for all
  languages), `cldf/parameters.csv` carrying `Concepticon_ID` and
  `Concepticon_Gloss` per meaning, plus `Semantic_field` and
  `Semantic_category` columns.
- **How it would enrich the wordnet:** it is the single largest **direct**
  `mww`→ILI feed available under an open licence, and it bypasses the cognate-
  transfer step that `chenhmongmien` requires. The concepts arrive
  Concepticon-mapped, so the Concepticon→Borin→ILI path is already built; no
  gloss-matching heuristic is needed. Beyond the links, it brings three things
  nothing else in the survey has: **`Semantic_field` / `Semantic_category`
  labels**, which map onto WordNet lexicographer files; **borrowing judgements
  with Chinese/Tai etymologies** (e.g. `teb` 'earth' ← 地 *dì*), which help
  decide whether a form deserves its own sense; and **Ratliff's own
  transcription**, consistent with A2.
- **Caveat to check before trusting the count:** `Parameter_ID` is an LWT meaning,
  not a sense, and several forms are multiword (`ntiaj_teb`, `hmoov_av`) or
  numbered variants (`teb (1)`). Expect the usable link count after
  disambiguation to be lower than 1,210 — but even a fraction of it dwarfs the
  current 1,601-sense lexicon's link coverage.

### Other items the survey missed

- **`conservancy.umn.edu` — Strecker & Vang (1986) *White Hmong Dialogues* is
  OPEN ACCESS.** This upgrades **C3** out of "availability unverified".
  Verified via OAI-PMH (`/server/oai/request`, record
  `oai:conservancy.umn.edu:11299/207905`): creators Strecker, David; Vang,
  Lopao; 1986; Southeast Asian Refugee Studies Project Occasional Papers No. 3;
  identifier `M1091`; handle **<https://hdl.handle.net/11299/207905>**;
  `dc:format` `application/pdf`. Abstract: "**Twenty dialogues in White Hmong**
  … presented in Hmong and English as a teaching aid … originally developed for
  an intensive beginning Hmong class and **include vocabulary, grammar notes,
  and pattern drills**." No `dc:rights` field was visible in the record I read,
  so the reuse terms are **unverified** — but the PDF is in an institutional
  repository and Strecker is a co-author we are already contacting. The
  "vocabulary" sections are a glossed `mww` wordlist in a controlled register.
  (Note: the HTML record page is behind an Azure WAF and returns 403; use the
  OAI endpoint or a browser. A microform copy is catalogued at the National
  Library of Australia, record 5483355.)
- **Strecker's *Mong Leng – English Dictionary* has a public non-Academia
  mirror** — see Gap 4. This removes the login wall for the resource you are
  already parsing.
- **`hmongdictionary.us` — *Hmong Dictionary Online*, James B. Xiong,
  St Paul MN.** Reported figures: **~12,000 Hmong words, ~12,000 English words,
  almost 40,000 definitions**, with Hmong text-to-speech and a spell-checker.
  That would make it **the largest Hmong–English lexical database on the web** —
  larger than Heimbach. **Licence: "COPYRIGHT 2011-2026, JAMES B XIONG, ALL
  RIGHTS RESERVED"** (verified on the site). No API, no export, no bulk
  download; basic lookup needs no account. Variety unstated (the curated
  resource list below calls it "White Hmong/Green Mong–English"). **Group (B),
  permission only — but it is one named individual in Minnesota, which is a
  realistic ask, and the size makes it worth asking.** The reported counts are
  **unverified** (they come from search-engine summaries, not a page I read).
  A separate `hmongdictionary.com` also exists, with audio, terms unverified.
- **`studyhmong.com`** — hosts an "A-to-Z Hmong Dictionary" plus PDF copies of
  Ratliff's demonstratives paper, Strecker's Hmong-Mien classification, Annie
  Jasser's *Hmong For Beginners*, and a full Heimbach scan. Aggregator; rights
  status of the scans is the same problem as RENINC. Worth a look for the
  A-to-Z dictionary's provenance; **not examined in detail.**
- **`williamjohnston.github.io/resources/hmong_linguistics`** — a short curated
  Hmong linguistics resource list (grammars, dictionaries, archives) maintained
  by William Johnston, including his own "Annotated bibliography of Hmong syntax
  and semantics" (self-described as "badly out of date"). It is how I found
  RENINC. Also points to **`sealang.net/sala/`** (Southeast Asian Linguistics
  Archives — older papers; distinct from the SEAlang dictionary service the
  survey correctly recorded as having no Hmong) and a **Hmong Language Resource
  Hub** Google Drive of linguistics articles.
- ***Hmong Studies Journal* bibliographies** —
  `hmongstudiesjournal.org/the-hmong-language.html` and
  `…/dictionaries-bibliographies-and-reference-works.html`, compiled by Mark E.
  Pfeifer: the most complete bibliography of Hmong language and dictionary
  literature I found, and open access. **The right place to look for any print
  dictionary we still cannot count.** Not systematically worked through here.
  The journal also publishes Strecker open-access.
- **UW–Madison Hmong Studies bibliography** —
  `hmongstudies.library.wisc.edu` (catalogue records, e.g. `HmongStudies1639`
  for Xiong et al. 1983). A library-catalogue route the first pass lacked.
- **`dmort27`/Mortensen material** — David Mortensen's Green Mong sketch in
  *The Mainland Southeast Asia Linguistic Area* (De Gruyter) and his Oxford
  Bibliographies article on Hmong-Mien. Same author as the CC0 `sch-corpus`
  already in the survey; the bibliography is a good cross-check on our coverage.

### Thai and Vietnamese material: nothing new found

Explicitly a **negative result**, with what I tried:

- A search for Vietnamese Hmong dictionaries (`Từ điển Hmông–Việt`, `tiếng
  Mông`) returned **only the English-facing web dictionaries above** — no
  Vietnamese–Hmong dictionary, no Vietnamese state or university lexicographic
  project, nothing machine-readable. Vietnam has a substantial Hmong population
  and published Hmong–Vietnamese teaching material certainly exists in print,
  but **none of it surfaced online**, and I could not identify a specific title
  to chase. The TUFS `vi` pivot therefore still has nothing to pivot from.
- On the Thai side, nothing was found beyond the two print items the survey
  already has (**P3a** Ratanakul 1972, **P3b** the 1987 Chulalongkorn
  multilingual glossary). No Tribal Research Centre wordlists surfaced. Note
  that **Lyman's and Heimbach's fieldwork were both Thailand-based** (Nan
  Province and Northern Thailand respectively, verified from their prefaces), so
  the Thai-side lexical record is largely already captured in the English-glossed
  dictionaries — which weakens the case for chasing Thai sources at all.
- **Revised view on the Thai/Vietnamese pivots:** the TUFS `th`/`vi`/`lo`
  dictionaries remain in the build and cost nothing, but there is **no
  Hmong–Thai or Hmong–Vietnamese lexical resource to feed them**. They should be
  deprioritised relative to French (Bertrais, Freelang) where a real bilingual
  resource exists, and relative to WOLD where no pivot is needed at all.

---

### Summary of what is still open

| Gap | Status |
|---|---|
| Webonary Hmong dictionary | **Probably none.** Domain-restricted search found nothing; site unfetchable. Needs a 1-minute browser check to be certain. |
| Wenshan wordlist *contents* | Record and extent verified; **the ZIP itself could not be downloaded** (CDN 403). Needs a browser download. Gloss language probably Chinese-only. |
| PanLex vs Zenodo licence | **Resolved: CC BY-NC-SA governs.** Freelang needs Dourthe's permission regardless. |
| Freelang entry counts | **Corrected downward** to 3,042/2,872 (French) as distributed; PanLex's 7,580/7,476 unexplained. |
| Michael Johnson contact | **Not found.** Independent scholar, Academia handle `mikejohnson247`, no email/ORCID/affiliation. Route via Strecker. |
| Heimbach entry count | **~4,500–4,900** (publisher blurb 4,900 reported; my OCR count 4,476). |
| Lyman entry count | **Still unverified.** OCR of his idiosyncratic transcription is too poor to count. 403 pp. |
| Bertrais entry count | **Still unverified as headwords**, but the author states "~30,000 lignes", 584 pp. |
| McKibben (1992) | **Still unverified.** Nothing found. |
| IMTVault | **Working via CLDF**, 90 `mww` + 12 `hnj` examples. Website is a dead SPA. |
| Vietnamese / Thai Hmong lexical sources | **None found.** Negative result, searched. |
| Mong Volunteer Literacy / *Tswv Yim Moob* | **Nothing online.** Strecker and Lopao Vang hold the copies. |

---

### Chinese-language lexical resources for Hmongic (Miao)

Pass date: 2026-09-28. Chinese-language search and catalogue work; the gap left by the
earlier pass. A Chinese gloss reaches the ILI through `omw-cmn`, so Miao–Chinese
dictionaries feed the wordnet as well as Miao–English ones.

**Method note on evidence.** Statements below are marked *verified* where I fetched and
parsed the artefact or record myself, *secondary* where a single reliable source mentions
it and I could not reach the primary, and *unverified* where I could establish existence
but not the detail. No ISBN, entry count or URL in this section is inferred or reconstructed.

**Orthography is the binding constraint.** Each Guizhou variety has its own 1950s Latin
orthography, mutually unintelligible as strings. Any two resources below in different
orthographies need a conversion table before they can be string-matched:

| Variety | ISO | Orthography | Standard reference dialect |
|---|---|---|---|
| Hmu / Qiandong / Central | `hea` | 1956 Qiandong Latin; 32 initials, 26 finals, 8 tones written as final letters `b x d l t s k f` (= 33, 55, 35, 22, 44, 13, 53, 31) — *verified* from the Hmub app's phonology screen | Yanghao 养蒿, Kaili (*secondary*) |
| Xong / Xiangxi / Eastern | `mmr` | 1950s Xiangxi Latin | Layiping 腊乙坪, Jiwei, Huayuan (*secondary*) |
| Chuanqiandian / Western | `cqd` | 1950s Chuanqiandian Latin ("西部方言苗文"); related to but **not** identical with RPA | Dananshan 大南山, Yanzikou, Qixing District, Bijie (*verified* on zh.wikipedia) |
| A-Hmao / Large Flowery | `hmd` | Three competing systems: Pollard script 柏格理苗文 / 石门坎苗文 (1900s); 滇东北苗文改革方案 (1950s Latin); 规范苗文 (1980s, Pollard-based, official in Yunnan) | Shimenkan 石门坎, Weining, Bijie (*verified*) |
| White Hmong / Green Mong | `mww` `hnj` | RPA | — |

A-Hmao is the worst case: three orthographies in live use, and the 2023 survey article
below states plainly that unification is not near ("大花苗民间现存多种文字，近期难以统一").

---

### (A) Usable now, open licence

Thin. The honest finding is that **there is no openly licensed Chinese-glossed Miao
lexical resource of any size.** Everything with scale is either all-rights-reserved or a
print scan. The open items are small or audio-only.

#### A1. Hmong-Mien audio word lists (Hsiu, Zenodo)
- **Title**: e.g. *Hmong (Fengqing) audio word list*
- **Author**: Andrew Hsiu, Center for Research in Computational Linguistics
- **Year / licence**: 2017-12-21; **CC-BY-4.0**
- **Variety**: Chuanqiandian Miao (`cqd`), Dashitouzhai and Malutang, Fengqing County, Yunnan
- **Entry count**: ~50 items, plus four song recordings; 54 WAV files
- **Orthography / gloss**: none — **audio only**, no transcription, no gloss
- **DOI**: `10.5281/zenodo.1123295` (siblings for Mien/Yao varieties at `.1123271`, `.1123285`, `.1123269`, `.1123259`, `.1123267`, `.1123324`, `.1123379`)
- **Machine-readability**: nil for lexical purposes
- **Status**: *verified* (record fetched)
- **Wordnet value**: essentially none for sense linking. Could later supply audio for a
  handful of `cqd` lemmas. Listed so nobody re-finds it and over-rates it.

#### A2. `dmort27/sch-corpus`
- **Title**: A Hmong language corpus derived from the soc.culture.hmong Usenet group
- **Licence**: **CC0-1.0**; **Variety**: White Hmong `mww`, RPA; **Gloss language**: none (monolingual running text)
- **URL**: `https://github.com/dmort27/sch-corpus`
- **Status**: *verified* (GitHub API)
- **Wordnet value**: frequency evidence and attestation for `mww` lemmas — useful for
  ranking which senses to build first, not for building them.

#### A3. `nathanmwhite/hmong-medical-corpus`
- **Licence**: GPL-3.0; **Variety**: `mww`; corpus, not lexicon. *Verified.*
- **URL**: `https://github.com/nathanmwhite/hmong-medical-corpus`

#### A4. 石门坎苗文文献概况与研究展望 (open-access survey article)
- **Journal**: 西南大学学报(社会科学版) / *Journal of Southwest University (Social Sciences)* 49(5), 2023-09
- **DOI**: `10.13718/j.cnki.xdsk.2023.05.020`; landing page `https://xbgjxt.swu.edu.cn/article/doi/10.13718/j.cnki.xdsk.2023.05.020`
- **Availability**: PDF downloadable without subscription — *verified* (fetched and text-extracted)
- **Wordnet value**: not lexical data, but the best available bibliography of A-Hmao
  (`hmd`) written material, and the source that identifies the two A-Hmao dictionaries in
  C3 and B4 below. Read this before any `hmd` sourcing work.

#### A5. Chinese Wiktionary — measured, and negligible
*Verified* by direct MediaWiki API counts of the `詞元` (lemma) categories, 2026-09-28:

| zh.wiktionary category | lemmas | en.wiktionary equivalent |
|---|---|---|
| 白苗語 (White Hmong `mww`) | **62** | 815 |
| 滇東北苗語 (A-Hmao `hmd`) | **11** | category absent |
| 青苗語 | 4 | — |
| 川黔滇苗語 (`cqd`) | **2** | 4 |
| 西部湘西苗語 (Xong `mmr`) | **2** | 4 |
| 北部黔東苗語 (Hmu `hea`) | **1** | 41 |
| 布努語 | 7 | — |
| 畲語 | 1 | — |

`Category:苗語支` has 18 subcategories but several (小花苗語, 角苗語, 中部麻山苗語,
西部麻山苗語, 中部惠水苗語) contain **no** lemma category at all. Total Hmongic lemmas on
zh.wiktionary is **~83**. Licence is CC-BY-SA, so it is reusable — but at this size it is
not a source. English Wiktionary is roughly ten times larger for `mww` and is the better
Wiktionary target. **Conclusion: Wiktionary is not a path for any Guizhou variety.**

---

### (B) Usable with permission or purchase

#### B1. ★ Hmub 有声词典 — Hmu talking dictionary (the headline find)
- **Title**: 苗语中部方言有声词典 / "Hmub Talking Dictionary", Central-dialect Miao
- **Author / team**: 苗族阿松 (A-Song), Pengshui, Chongqing — code and design; 杨文斌 (Miao) — entry pronunciation; 耕夫 (Miao) — project initiator; 吴小花 (Miao) — phonology recordings
- **Publisher**: self-published Android app + web front end; Version 1.0, 2025-04-16
- **Variety / ISO**: **Hmu / Qiandong / Black Miao, `hea`**
- **Orthography**: 1956 Qiandong Latin orthography (`ab`, `gos gheik`, `hxak`, `dlob`), consistent throughout
- **Gloss language**: **Chinese**
- **Entry count** — *verified* by parsing the data file myself:
  - **14,451 entries**, **14,416 unique headwords**
  - **16,910 gloss units** once the `|` sense separator is expanded; **1,607 entries carry more than one `|`-separated sense**, and some also carry internal numbered senses (e.g. `ab` → `1.阿(词头)2.偏,倾斜|输,屈(理)`)
  - 1,394 single-syllable and 13,057 multi-word headwords
  - **1,167 MP3 pronunciation files** (78.5 MB) — audio for ~8% of entries, not all
- **Machine-readability**: **excellent.** The whole dictionary is one flat JS array in `AiIndex.htm`, one object per line, `{ 苗语: "...", 中文: "...", 音频: "audio/....mp3" }`. A ten-line parser gets a clean TSV. The `|` separator already does part of the sense-splitting work.
- **URL**: `https://github.com/absongb2099/Hmub.yscd` (created 2025-04-23, last pushed 2026-09-19 — actively maintained)
- **Licence / availability**: **no open licence; explicitly all rights reserved.** The app's own 资源声明 and 版权声明 read "任何单位和个人未经作者许可，不得擅自传播或用于商业用途" and "所有词库&音频数据未经原著许可，严禁盗用二次利用". The text is public on GitHub with no LICENSE file, so default copyright applies. **Permission is required and must be asked for.**
- **Provenance caveat**: the notes say the compilers copied a source verbatim while crediting it ("明确注明来源的同时，我们将该资源照搬，未做任何修改或加工") and that "经授权的所有词条现已配置完成" — i.e. the wordlist is licensed from an 原著 (original work). **The source is not named anywhere in the file.** Given the orthography, the Chinese glosses and the 14k scale, it is *plausible but unverified* that it derives from 张永祥《苗汉词典（黔东方言）》1990 (C1). This must be settled before use, because permission may need to come from the original publisher as well as the app team.
- **Contact**: WeChat `absongb2099` (given in-app). Named team members are traceable.
- **Wordnet value**: **this is the single most valuable Hmongic resource found in any pass.** 14.4k Hmu headwords with Chinese glosses, already sense-segmented for 1,607 entries, in the official orthography, machine-readable today — enough to build a genuine `hea` wordnet via the `omw-cmn` pivot, not a toy. Audio for 1,167 entries is a bonus no other Guizhou resource offers. **Highest-priority permission request of the whole project.**

#### B2. 苗语查询 — White Hmong (RPA) → Chinese phrasebook
- **Author**: same developer (苗族阿松); **URL**: `https://github.com/absongb2099/mycx`
- **Variety**: **White Hmong `mww`, RPA orthography**; **Gloss language**: Chinese
- **Entry count**: **245 entries, 239 unique headwords**, 105 single-word — *verified* by parsing
- **Licence**: none stated; same all-rights-reserved posture as B1
- **Wordnet value**: small, but it is the **only RPA↔Chinese aligned list found**. Its real
  use is as a seed conversion key between the diaspora `mww` wordnet and the China-side
  `cqd`/`hea` work — the two halves of the project currently share no orthographic bridge.
  Sibling repos `sycx` (She) and `yycx` (Yao) exist; both smaller.

#### B3. Hmub 地名 — Hmu toponyms
- **URL**: `https://github.com/absongb2099/Hmub.dmz`; **~955 Hmu–Chinese place-name pairs** (*verified* by parsing), Qiandong orthography, no licence.
- **Wordnet value**: named entities / instance synsets for Qiandong villages. Marginal for core wordnet, good for a gazetteer.

#### B4. ★ 贵州民族语言学习简本 — three Miao dialects in parallel
- **Title**: 《贵州民族语言学习简本》 / *Concise Reader for Guizhou Ethnic Languages*
- **Publisher / year**: 贵州教育出版社 (Guizhou Education Press), 2015-12-01, ¥32.00
- **ISBN**: the platform displays "978-7-454456-0908-0", which is **malformed and cannot be a valid ISBN-13** — treat as **unverified**; get it from a library catalogue before citing
- **Varieties**: all three Miao dialect groups in one book — 苗语（东部方言）= Xong `mmr`; 苗语（中部方言）= Hmu `hea`; 苗语（西部方言）= Chuanqiandian `cqd`. Also Bouyei, Dong, Yi sections.
- **Orthography**: each variety's own official Latin orthography, **plus a Chinese-character 注音 approximation** for every item
- **Gloss language**: Chinese
- **Entry count** — *verified* by fetching and parsing all three dialect pages:
  - **exactly 300 numbered items per dialect**, 8 thematic sections each (数字, 称谓, 文明礼貌, 生活娱乐, 人体部位, 家禽家畜, 谷物果蔬, 自然现象)
  - per dialect: **~178 short lexical items** and **~111–114 full sentences**
  - **201 of the 300 Chinese glosses are identical across all three dialects** (224/300 for East vs Central), so about two-thirds is a **directly parallel trilingual wordlist**; the rest needs manual alignment (glosses drift, e.g. item 295 is 海/海/龙潭)
- **Availability**: full text **freely readable without login** at 贵州数字出版云村寨平台 (Guizhou Digital Publishing "Cloud Village" platform) — *verified*, pages fetched and parsed
- **URLs**: index `https://www.yuncunzhai.com/book/274242.html`; East `.../274243.jhtml`; Central `.../274252.jhtml`; West `.../274261.jhtml`
- **Machine-readability**: **good** — rigid `NNN.汉语：… / 苗语：… / 注音：…` triples in the HTML, parsed cleanly on first attempt
- **Licence**: **none.** Free to read is not free to reuse; this is an in-copyright 2015 trade book on a commercial platform (the platform shows 会员购买 and login prompts elsewhere). Permission needed from Guizhou Education Press.
- **Wordnet value**: the **only genuinely cross-dialect parallel Miao–Chinese data found**, and the only resource that touches `mmr`, `hea` and `cqd` in one consistent editorial frame with the standard orthographies. ~178 concepts × 3 varieties is small, but it is an ideal **calibration and orthography-conversion set**: the same concept in three orthographies with Chinese as the pivot is exactly what is needed to align B1 (`hea`) with any future `mmr`/`cqd` data. The sentences also give usage examples, which wordnets normally lack for low-resource languages.
- **Wider note**: the same platform hosts Bouyei, Dong and Yi sections of this book, and a large body of 贵州传统村落全景录 village monographs. It surfaced in nearly every Chinese search run and deserves a systematic crawl in its own right — it is the closest thing to a Guizhou minority-language digital library found.

#### B5. ★ A Hua-Miao Archive / On-line Glossary (A-Hmao)
- **Title**: *Songs and Stories and a Glossary of Phrases of the Hua Miao of South West China*
- **Compilers**: 王明基 **Wang Ming-ji** compiled the base list at Shimenkan in **1946** (~2,000 A-Hmao words with short definitions, written in **Pollard script**, four hand-bound booklets); **P. Kenneth Parsons** translated it into English with Wang in **1949**; **R. Keith Parsons** then greatly extended it from his corpus of traditional songs and stories. Archaic items are tagged **OM** ("Old Miao"), following 杨永新 Yang Yung-xin's list of ~70 archaic song words.
- **Host / maintainer**: Department of Electronics and Computer Science, University of Southampton; created and maintained by **Dr Steve Rake** (contact address published on the site)
- **Variety / ISO**: **A-Hmao / Large Flowery Miao, `hmd`** — the `hmd` gap in our survey
- **Orthography**: Pollard script (with a downloadable Ahmao font and template), plus a romanized initials/finals/tone representation used by the search form
- **Gloss language**: **English**; the search form also offers a **Pinyin** field and a Miao field, so some Chinese indexing exists
- **Size**: the printable edition is **26 volumes across 3 books, ~1,170 pages** of PDF (self-extracting EXE or ZIP, 2,076 + 727 + 840 KB) — *verified* from the archive's own Printing page. That is far beyond the 1946 base of ~2,000 words; **a precise current entry count is not published and remains unverified.**
- **URLs**: `https://web-archive.southampton.ac.uk/miao/` (index), `/miao/glossary/index.html`, `/miao/glossary/printing/ReadMe.html`, `/miao/glossary/originofglossary.htm`, `/miao/glossary/search1.htm`
- **Access caveat**: the live site is behind an **Anubis proof-of-work anti-bot wall** (HTTP 401 to scripted requests — *verified*). It loads in a normal browser. Only 14 URLs under `/miao` are in the Wayback Machine, and the glossary body is served by a CGI search, so **the glossary content is not bulk-harvestable**; the 3 printable PDF bundles are the practical route to the full data.
- **Machine-readability**: **poor as published** — PDFs laid out for print, plus a CGI search. Would need PDF text extraction and entry parsing. Not image scans, though, so extraction should be tractable.
- **Licence**: **none stated.** Copyright rests with the Parsons brothers; the archive invites contact. *Secondary* inference: a research-use permission is plausible given the stated aim of filling a documentation gap, but it must be asked for.
- **Wordnet value**: **the only substantial A-Hmao lexical resource in existence, in any language.** It would single-handedly open `hmd`, and because its glosses are English it links to PWN/ILI directly without the `omw-cmn` pivot. The OM tags are a ready-made archaism feature. **Second-highest-priority permission request**, and unusually tractable: one named, contactable maintainer.

#### B6. Chinese academic databases — all subscription-gated
*Verified* that each is paywalled; *not* verified that any holds structured Miao lexical data.
- **CNKI 中国知网** (`cnki.net`, overseas `oversea.cnki.net`) — holds relevant theses, e.g. 苗语中部方言谚语语义研究 (Hmu proverb semantics), 苗语黔东方言的韵母比较研究, 苗语方位词的认知语义学研究 (Jiwu Miao, Huayuan, Hunan). These are **analyses with embedded wordlists, not databases**; harvesting means reading PDFs. Institutional subscription required.
- **读秀 Duxiu / 超星 SuperStar** (`duxiu.com`) — ~3 million Chinese books, **full-text search inside books plus page delivery by email**. This is the most useful of the four for our purpose, because it is where the scanned minority dictionaries actually live (see C5 — the `.pdg` page-image format is Duxiu's native format). Subscription required; Palacký or Guizhou University access would be the lever.
- **万方 Wanfang**, **维普 CQVIP** — checked, subscription, nothing Miao-lexical distinctive surfaced.
- **Action**: Guizhou University almost certainly has CNKI + Duxiu. This is a concrete, cheap ask for the collaboration and the fastest route to C1–C4.

#### B7. 语保工程 / Chinese Language Resources Protection Project
- **Platform**: 中国语言资源保护工程采录展示平台, `https://zhongguoyuyan.cn/` and `https://service.zhongguoyuyan.cn/`
- **Scale** (*secondary*, from MoE announcements): 1,712 survey points nationally, 123 languages; the display platform has aggregated **1,289 Chinese-dialect points and 429 minority-language points**. Registration-based access, stated to be open to the public.
- **Status**: **still inaccessible.** *Verified* this pass: **HTTP 412 from both hosts and from `/about_us`**, with a browser User-Agent. This matches the earlier pass exactly — it is a geo/WAF block, not a transient failure.
- **Wordnet value**: potentially the largest single source of Guizhou Hmongic survey wordlists in existence, and it remains **the biggest unresolved lead in the whole survey**. Cannot be assessed from outside China.
- **Action**: unchanged and now doubly confirmed — **ask Guizhou University to check it from inside China.** Also note the user manual is public and fetchable: `https://service.zhongguoyuyan.cn/resources/用户指南V2.2.pdf`.

---

### (C) Print-only or unverified

#### C1. ★ 苗汉词典（黔东方言）— the Qiandong Miao–Chinese Dictionary
- **Title**: 《苗汉词典：黔东方言》, parallel Miao title **"Hmub diel cif dieex : Hveb qeef dongb"**
- **Editors**: **张永祥 Zhang Yongxiang** (chief editor); 许士仁 Xu Shiren (associate); 曹翠云 Cao Cuiyun, 潘定华 Pan Dinghua (contributing) — *verified* via WorldCat record
- **Publisher / place / year**: **贵州民族出版社 (Guizhou Nationalities Press), 贵阳 Guiyang, 1990**, 第1版 — **the premise's 1990 date is CONFIRMED**
- **Variety / ISO**: Hmu / Qiandong `hea`; **Orthography**: 1956 Qiandong Latin (evident from the parallel title); **Gloss language**: Chinese
- **Award** (*secondary*): second prize, first 中国民族图书奖 (State Ethnic Affairs Commission), 1992 — indicates it is the authoritative work
- **Catalogue ID**: **OCLC 27234172**, `https://search.worldcat.org/title/27234172`
- **ISBN / pagination**: **UNVERIFIED — do not cite yet.** A search-engine summary of this WorldCat record reported ISBN `9787541200656` / `7541200654` and "4, 20, 438 pages", but **a direct fetch of the same record displayed neither ISBN nor pagination**, and the `7-5412-` prefix belongs to **四川民族出版社**, not Guizhou Nationalities Press — so that ISBN is probably contaminated from a neighbouring record. Needs NLC or a university OPAC to settle.
- **Machine-readability**: none — print only. Not found in any digitised collection this pass.
- **Wordnet value**: the reference Hmu dictionary, and the most likely 原著 behind B1. If B1 does derive from it, clearing rights here may be unavoidable — and if it does not, this is the obvious next digitisation target for `hea`.

#### C2. 汉苗词典（黔东方言）— Chinese→Miao, Qiandong
- **Editor**: **王春德 Wang Chunde**; **Publisher / year**: **四川民族出版社 (Sichuan Nationalities Press), 1992**; series **中国少数民族语言系列词典丛书**
- **PREMISE CORRECTION**: web summaries and the premise attribute a 1992 Miao dictionary to 贵州民族出版社. The filename in the digitised series folder (*verified*) reads **四川民族出版社.1992** — Sichuan, not Guizhou. Wang Chunde's Guizhou-published work is 《苗语语法（黔东方言）》, **1986** (*secondary*).
- **Variety**: Hmu `hea`, Qiandong orthography; **Direction**: **Chinese → Miao** (so it indexes by Chinese headword — convenient for `omw-cmn` pivoting, inconvenient for lemma coverage)
- **ISBN / entry count**: **unverified**
- **Machine-readability**: exists only as a `.pdg` scan (see C5)

#### C3. 汉苗词典（湘西方言）— Chinese→Miao, Xiangxi/Xong
**The best-documented print item found this pass.**
- **Editor**: **向日征 Xiang Rizhen**, with the CASS Institute of Ethnology editorial board
- **Publisher / year**: **四川民族出版社, 1992-08**; series 中国少数民族语言系列词典丛书
- **ISBN**: **9787540903008** — *verified* on a bookseller record showing full physical description
- **Pagination / price / format**: **307 pages**, hardcover, 19 cm, ¥6.85
- **Entry count**: **over 11,300 entries** — characters, words, phrases and four-character idioms
- **Variety / ISO**: **Xong / West Hunan Miao, `mmr`**, based specifically on the **western subdialect of Xiangxi**; Xiangxi Latin orthography; **Gloss direction**: Chinese → Miao
- **URL**: `https://www.dushu.com/book/10509811`
- **Machine-readability**: none as published; a `.pdg` scan exists (C5)
- **Related**: 向日征《吉卫苗语研究》, 四川人民出版社, 1999 (*secondary*)
- **Wordnet value**: **the only wordnet-scale `mmr` resource identified.** 11,300 Chinese-indexed entries is directly pivotable through `omw-cmn`; being Chinese-headword-indexed, it maps onto Chinese wordnet senses almost mechanically. If B1 covers `hea` and B5 covers `hmd`, this covers `mmr` — together they would span three of the four Guizhou varieties.

#### C4. 川黔滇方言苗汉简明词典（初稿）— Chuanqiandian concise dictionary
- **Compilers**: 贵州省民族语文指导委员会研究室川滇黔方言组 等编
- **Publisher / year**: **贵州民族出版社, 1958**, marked 初稿 (draft)
- **PREMISE CORRECTION**: the premise expected a 1992 Chuanqiandian 《苗汉词典》 from Guizhou Nationalities Press. **No such 1992 edition was found.** What exists is this **1958 draft** — *verified* as a real, retrievable digitised item (11,590,789 bytes, see C5). The 1990/1992 pair in the premise appears to be 1990 Qiandong 苗汉 (C1) + 1992 Qiandong/Xiangxi 汉苗 (C2/C3), with the Chuanqiandian volume being the much earlier 1958 draft.
- **Variety**: Chuanqiandian `cqd` — the China-side relative of White Hmong, i.e. the bridge to the diaspora project
- **Orthography caveat**: **1958 predates the settled Chuanqiandian orthography.** A 初稿 from 1958 may use a provisional or transitional spelling, so it cannot be assumed to match modern 西部方言苗文. Must be checked on the scan before use.
- **ISBN**: none — pre-ISBN era. **Entry count unverified.**
- **A parallel Qiandong volume**, 《黔东方言苗汉简明词典》 by 贵州省民族语文指导委员会研究室黔东方言组 + 中国科学院少数民族语言调查第二工作队, is attested (*secondary*, single mention) but **I could not locate a copy or a catalogue record**. Existence established; location not.

#### C5. The digitised-scan channel — real, but format-bound and rights-encumbered
*Verified* by directory listing, HEAD requests and a byte-range probe of the ZIP structure.

`downloads.freemdict.com` mirrors a `中国少数民族语言系列词典丛书` folder holding, among 16 items:
| File | Size |
|---|---|
| 汉苗词典（黔东方言）.王春德编著.四川民族出版社.1992.zip | 11,635,618 B |
| 汉苗词典（湘西方言）.向日征编著.四川民族出版社.1992.zip | 9,905,835 B |
| 川黔滇方言苗汉简明词典（初稿）.…贵州民族出版社.1958.zip | 11,590,789 B |
| 汉瑶词典（布努语）.蒙朝吉编著.1996 / 汉瑶词典.毛宗武编著.1992 | (Hmong-Mien, Yao side) |
| **汉水词典.曾晓渝等编著.四川民族出版社.1996** | 8,835,391 B — **Sui, relevant to the wider Guizhou survey** |
| 白汉词典.赵衍荪等.1996 | 17,991,407 B |

Two hard findings:
1. **Format.** I range-probed the Qiandong ZIP's local file header and central directory. It contains `000001.pdg … 000460.pdg` plus `cov001/fow00n/leg001/bok001.pdg` — i.e. **~460 pages of `.pdg`, the proprietary SuperStar/Duxiu page-image format.** These are **scanned bitmaps in a closed container**, not text. Usable only after `.pdg` → image conversion **and** Chinese OCR **and** entry-structure parsing. The leading `10030xxx_` filenames are Duxiu SS book IDs, confirming provenance.
2. **Rights.** These are **unauthorised rips of a commercial digital library** of in-copyright works (1958–1996, 四川民族出版社 / 贵州民族出版社). Files carry MD5/SHA1 in an `fmdl_readme.md` but **no licence of any kind**. They are evidence that a digitisation exists and a way to *inspect* the books; they are **not a lawful source for a released wordnet**. The clean route to the same content is Duxiu under institutional subscription (B6) or licensing from the publishers.

Separately, `xianzhi8.com/article.php?id=481` sells PDF scans of the whole **中国少数民族语言简志丛书 (58 volumes)** — **¥280 for the set, ¥10 per volume**, including **苗语简志 (王辅世, 1985)** and 瑶族语言简志 (毛宗武, 1982). Also an unauthorised reseller; no redistribution rights. *Verified* (page fetched).

#### C6. Comparative Miao-Yao scholarship (Wang Fushi, Mao Zongwu, Chen Qiguang, Li Yunbing)
- **王辅世 主编《苗语简志》**, **民族出版社, 1985-05, 203 pages**, 中国少数民族语言简志丛书. *Secondary* (Douban + zh.wikipedia citation). ISBN unverified. The standard reference that fixed the three-dialect / seven-subdialect classification and subdivided Qiandong into three subdialects. Contains a phonology and grammar sketch; **whether it carries a comparative vocabulary appendix, and of what size, I could not verify** — Douban/search do not expose the TOC. Available as a paid scan (C5).
- **王辅世、毛宗武《苗瑶语古音构拟》**, **中国社会科学出版社, 1995** (*verified* as cited on zh.wikipedia). A CNKI thesis abstract instead cites **王辅世《苗语古音构拟》1994** — a **different, single-author title**. These may be two works or one miscited; **unresolved, and worth settling before citing either.** A proto-Miao-Yao reconstruction of this kind normally carries a large comparative etymon list, which would be the vocabulary appendix of interest — **but I could not confirm its existence or size.**
- **陈其光《苗瑶语文》**, **中央民族大学出版社, 2013-03** (*secondary*). Chapter 3 (词汇) covers 词的结构, 成语, 借词, 混合词. Author 陈其光 b. 1926, Yuanjiang, Hunan. Note our Lexibank `chenhmongmien` is described as derived from Chén's work dated **2012**, so the CLDF dataset and this 2013 imprint may be different editions — **worth checking whether the book's own tables exceed the 883 Concepticon concepts × 25 varieties already in the CLDF set.** A publisher page exists at `minwang.com.cn` but the host **refused connections** this pass (ECONNREFUSED), so the TOC could not be read directly.
- **李云兵《苗瑶语比较研究》**, **商务印书馆, 2018-10, ISBN 978-7-100-16506-8, 529 pages, ¥98** — *verified* on the Commercial Press catalogue page `https://www.cp.com.cn/book/b99d3528-b.html`. Covers nine Hmong-Mien groups (Miao, Bunu, Baheng, Wunai, Younuo, Jiongnai, Bana, She, Yao). Method is descriptive/synchronic-comparative (word formation, morphology, word order, tone sandhi); chapters 6–7 do historical comparison "based on common Miao-Yao vocabulary", but **the catalogue page does not confirm a wordlist appendix or give an etymon count.** The newest and most comprehensive comparative volume; the best single print purchase for classification questions.

#### C7. A-Hmao print items named in the 2023 survey article (A4)
All *secondary*, from the survey article's own text; none located as artefacts.
- **《苗英词典》 (Miao–English Dictionary)** — compiled by **张绍乔 (P. Kenneth Parsons)** and **张继乔 (R. Keith Parsons)** from Flowery Miao material gathered in the late Republican period, capturing mostly "middle-period" A-Hmao vocabulary. Explicitly marked **内部资料 (internal circulation, never published).** This is almost certainly the print antecedent of B5 — the same two brothers, the same corpus.
- **王维阳 Wang Weiyang 《苗汉词典》 (A-Hmao Miao–Chinese Dictionary)** — newly compiled and **published in the early 21st century** in **Bijie, Guizhou**. A separate source describes it as commissioned by **Weining County government**, with 王维扬 working alongside 威宁县民宗局 and 威宁苗学会 over **more than ten years**. **Publisher, year, ISBN and entry count are all unverified**, and I could not find a catalogue record or a vendor. **Existence is well established; where to obtain it is not.** Given that it is the only modern A-Hmao Miao→Chinese dictionary, this is the highest-value unverified item in the report, and the Weining county 民宗局 / 苗学会 are the concrete place to ask.
- **《小学生苗汉成语词典》, 2012** — A-Hmao idiom dictionary for primary pupils, in 规范苗文. **《小学语文词语手册》, 2015.** Part of the Yunnan 规范苗文 school-textbook programme (1988– ). Small, pedagogical, but Miao–Chinese and in the official Yunnan orthography.
- **杨世武 主编《西部苗族古老歌》, 云南民族出版社, 2019** — the most recent published Shimenkan-script book; song texts, not lexicon.
- A substantial grey literature exists in 内部资料 form (陶绍虎《苗文初步》, 《大花苗石门坎语音初探》, 《花苗文简略导学》, distributed free in Kunming; 张文德《苗族中草药》; 朱文光《阿卯迁徙史》 and 《滇中苗族草药》, both Miao–Chinese bilingual). **Circulates within Wumeng-region Miao communities only; not in any catalogue.**

#### C8. Hmu teaching and specialist materials
- **石德富《苗语基础教程（黔东方言）》**, **中央民族大学出版社, 2006-08**, 3 volumes (上中下), from the CMU 十五 / 211 minority-language textbook series; for non-native undergraduates and postgraduates. Amazon ASIN `B001142AGG`; **ISBN unverified.** *Secondary.* Author is an associate professor at Central Minzu University — like 周国炎 (the Bouyei dictionary author already flagged in NOTES.md), **a natural collaborator and a likely route to C1 and B1 rights**.
- **《苗语俗语小词典：黔东方言》** — a Hmu idiom/colloquialism dictionary, catalogued in **CiNii** (`https://cir.nii.ac.jp/crid/1130000797342115840`). Editor, publisher, year and entry count **unverified**; held in Japanese libraries, which makes it obtainable via ILL.
- **《黔东苗语使用现状及其演变》** — sociolinguistic study of Hmu, on Douban (`book.douban.com/subject/37156592/`). Sociolinguistics, not lexicon.

#### C9. National and open-repository searches — verified negatives
Recording these so no later pass repeats them.
- **GitHub**: exhaustively searched (`Hmong dictionary`, `Miao language`, `hmong lexicon`, `hmong wordnet`, `Hmong corpus`, `苗语`, `苗文`) via the API. **`hmong lexicon` and `hmong wordnet` return zero repositories.** Outside the `absongb2099` family (B1–B3) and the two `mww` corpora (A2, A3), **there is no Miao lexical data on GitHub.** Hits for 苗文/苗语 are overwhelmingly 苗绣 (embroidery) heritage websites and unrelated 疫苗/苗苗 string matches.
- **Zenodo**: nothing Hmongic and lexical beyond the Hsiu audio wordlists (A1) and the `chenhmongmien` CLDF set we already hold (`10.5281/zenodo.13149500`, CC-BY-4.0).
- **Gitee**: no distinct Miao lexical project surfaced.
- **中国国家图书馆 (NLC)**: **not reached.** The OPAC was not queryable from here, so **no NLC call number is given for any print item above.** The WorldCat record for C1 is the only catalogue identifier established. This remains an open task, and one a Guizhou University collaborator can do trivially.
- **WorldCat**: individual records resolve (C1), but the **search interface returned no parseable results** to scripted fetching, so I could not enumerate holdings or pin ISBNs for C2, C4 or C6.
- **Chinese university institutional repositories**: no Miao lexical dataset found.
- Note one adjacent live project: `eastmountyxz/Sui-AIResearch`, a Guizhou University team (杨秀璋) applying AI to **Sui** 水族 language, script and manuscripts. Not Hmongic, but a **Guizhou University in-house group already doing minority-language computational work** — a plausible local partner.

---

### What this pass changes

1. **A wordnet-scale, machine-readable, Chinese-glossed Hmu dictionary exists and is
   online today** (B1: 14,451 entries, 16,910 sense units). This is a different situation
   from "everything is print-only Chinese", which is what the previous pass concluded.
   It needs a permission conversation, not a digitisation programme.
2. **Three of the four Guizhou varieties now have an identified wordnet-scale source**:
   `hea` via B1 (and C1 behind it), `mmr` via C3 (11,300 entries, ISBN verified),
   `hmd` via B5 (~1,170 pages, English-glossed). **`cqd` remains the weak case** — only
   the 1958 draft (C4) and 300 items in B4.
3. **Two premise corrections.** The 1990 Qiandong 《苗汉词典》 is confirmed; but the
   expected 1992 Chuanqiandian 《苗汉词典》 from Guizhou Nationalities Press **does not
   appear to exist** — the Chuanqiandian concise dictionary is a **1958 draft**, and the
   1992 volumes are **Sichuan** Nationalities Press 汉苗 dictionaries for Qiandong (C2)
   and Xiangxi (C3).
4. **Wiktionary is definitively ruled out** for Hmongic: ~83 zh lemmas total, measured.
5. **语保 is confirmed blocked** (HTTP 412 again, both hosts) — it is a geo-block, and the
   only way in is a collaborator inside China.
6. **Orthographic conversion is now a named work package**, not a footnote: B1 is Qiandong
   Latin, `chenhmongmien` is IPA, B5 is Pollard, the diaspora work is RPA. B4's 300
   trilingual items are the natural calibration set for building those mappings.

---

## Verification notes

Method: the session's web-search budget was exhausted before this survey began,
so everything here was gathered by direct HTTP against APIs and canonical URLs —
the MediaWiki API (en/fr/zh Wiktionary, Wikimedia `sitematrix`), the Wikidata
SPARQL endpoint, the GitHub API, the OPUS API, the Open Library and Internet
Archive APIs and metadata endpoints, the Zenodo API, OpenAlex, the DSpace REST
API at ANU, raw files from `lexibank/*` and `concepticon/concepticon-data`, and
the Internet Archive Wayback Machine (for the Academia.edu reconstruction).

Known gaps, all flagged inline above: PanLex per-language expression totals
(API unreachable); the PanLex source list tail (server-side truncation at
1,047,575 bytes); ~25 Strecker draft titles and all Strecker PDF internals
(Academia.edu login wall); SIL's Wenshan wordlist entry and any Webonary Hmong
dictionary (HTTP 403); entry counts for every print dictionary in groups (B)/(C).

General search engines were also unavailable — DuckDuckGo (HTTP 202 challenge),
Mojeek (403) and Marginalia (302) all refused programmatic queries — so
**absence of evidence in this report is weaker than presence of evidence**, and
the print-dictionary section in particular would benefit from a library-catalogue
(WorldCat, CNKI, Duxiu) pass that could not be performed here.
