# Copyright and licensing

**Everything in this repository is under the Creative Commons Attribution 4.0
International licence in `LICENSE`, except the files listed below.** Those are
derived from sources with their own terms, and are redistributed under those terms
rather than under `LICENSE`.

The distinction matters in one direction only: the licence on `LICENSE` is
permissive, so a file governed by a *stricter* source licence needs saying. Nothing
here is more permissive than `LICENSE`.

## Files under their source's licence

| File | Derived from | Under |
|---|---|---|
| `dbnary-hmong.tsv` | [DBnary](http://kaiko.getalp.org/about-dbnary/), itself extracted from English Wiktionary | CC BY-SA 3.0 Unported |
| `dbnary-pivots.tsv` | the same | CC BY-SA 3.0 Unported |
| `kinship-kindiv.tsv` | its `KINDIV_LABEL` column is [KinDiv](https://github.com/kinship-diversity/KinDiv)'s concept labels | CC BY-SA 3.0 Unported |

The two DBnary tables hold Wiktionary sense definitions verbatim — 762 and 29,301
rows of them — so share-alike plainly applies and we do not argue otherwise.

They are kept in the repository rather than regenerated on demand so that nobody
has to query DBnary's SPARQL endpoint to reproduce this work. `fetch_dbnary.py`
will rebuild them for anyone who prefers to, but it is a public service and there
is no reason for every reader to hit it for data that does not change.

Note that these three files carry no comment header stating their licence, as the
scripts in this repository read them with a plain TSV reader that would take a
leading `#` line as the column names. That is why this file exists.

## Files extracted from publications

These are our own tables, but what is *in* them is a record of facts stated in
somebody else's work, with a page number on every row:

| File | Extracted from | That source |
|---|---|---|
| `classifiers.tsv`, `class_nouns.tsv` | Bisang (1993), Appendices I and II | in copyright, All rights reserved |
| `classifiers-white2021.tsv`, `underspecified.tsv`, `kinship.tsv` | White (2021), ch. 7 and Tables 29, 39–41 | open access thesis |
| `hmong_ontology.xml` | the ontology, plus the above folded in | CC BY 4.0, and see above |

Our position is that a classifier inventory and its glosses is a table of facts
about a language rather than an expressive work, and that recording where each fact
was stated is the right way to use it. That is a position and not a licence, and
anyone redistributing these files should form their own view. Nothing is quoted
from Bisang (1993) at length; the glosses are our wording, and the handful of
quotations in the file headers are short and attributed.

## Generated files

`wordnets-cited.tsv` reproduces, for each wordnet this work queries, the citation
its own WN-LMF metadata asks for. Those strings are their authors' and are
reproduced as bibliographic attribution. `facts.json` and the `review-*.tsv` sheets
are computed from the files above and inherit whatever applies to their inputs.

## The lexicons this builds

`build.sh` writes WN-LMF lexicons that contain no text from the share-alike
sources: what reaches them from DBnary is an interlingual index identifier chosen
by counting which of 25 other languages' wordnets agree, with a note recording
which, and what reaches them from KinDiv is 21 kin-type identifiers in Murdock's
standard notation. We therefore do not treat the lexicons as share-alike works.
This too is a position rather than a licence, and the `--license` the converter
stamps on its output is whatever the person running it passes.
