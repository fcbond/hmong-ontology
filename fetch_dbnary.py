#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
r"""Fetch the Hmong translations of the English Wiktionary from DBnary.

DBnary <http://kaiko.getalp.org/dbnary> publishes Wiktionary as RDF, with a
SPARQL endpoint. It is preferable to scraping Wiktionary or to parsing a raw dump:
it is a maintained, citable release, and it carries the one thing we actually want,
which is the *sense* a translation attaches to rather than merely the page.

Hmong is not a Wiktionary edition, so it appears in DBnary only as a translation
target in other editions -- but the English edition's translation tables are
sense-anchored, which is exactly the disambiguation an English lemma alone lacks.
Note that DBnary records the target language as a lexvo URI, not as a bare code:
`dbnary:targetLanguageCode` is used only for varieties lexvo does not cover, so a
query filtering on the code finds no Hmong at all.

It also fetches the *other* languages' translations of the same senses, into
`dbnary-pivots.tsv`. Those are what makes triangulation possible: the sense a Hmong
word translates is usually translated into a dozen other languages too, and where
several of those languages' wordnets agree on an ILI, that agreement is evidence
about the concept rather than about how two glosses happen to be worded. The method
is that of \citet{bond-etal-2008-japanese} and \citet{bond-foster-2013-omw}.

    uv run fetch_dbnary.py                      # both TSVs
    uv run fetch_dbnary.py --language mww       # one Hmong variety only
    uv run fetch_dbnary.py --no-pivots          # skip the sibling translations
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ENDPOINT = "http://kaiko.getalp.org/sparql"

#: ISO 639-3 codes we want, and the dialect tag each maps to
LANGUAGES = {"mww": "WH", "hnj": "GM"}

#: Pivot languages: ISO 639-3 as DBnary writes it -> the `wn` lexicon that covers
#: it. Only languages whose wordnet is linked to the Interlingual Index are useful,
#: because the whole point is to intersect ILIs. Every one of these ships in the
#: Open Multilingual Wordnet release.
PIVOTS = {
    "fra": "omw-fr", "cmn": "omw-cmn", "jpn": "omw-ja", "spa": "omw-es",
    "ita": "omw-it", "fin": "omw-fi", "cat": "omw-ca", "eus": "omw-eu",
    "ell": "omw-el", "bul": "omw-bg", "dan": "omw-da", "glg": "omw-gl",
    "heb": "omw-he", "hrv": "omw-hr", "ind": "omw-id", "isl": "omw-is",
    "lit": "omw-lt", "nld": "omw-nl", "nob": "omw-nb", "nno": "omw-nn",
    "pol": "omw-pl", "ron": "omw-ro", "slk": "omw-sk", "sqi": "omw-sq",
    "swe": "omw-sv", "tha": "omw-th", "zsm": "omw-zsm", "arb": "omw-arb",
}

QUERY = """
PREFIX dbnary: <http://kaiko.getalp.org/dbnary#>
PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX lexinfo: <http://www.lexinfo.net/ontology/2.0/lexinfo#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?hmong ?english ?pos ?defn WHERE {
  GRAPH <http://kaiko.getalp.org/dbnary/eng> {
    ?t dbnary:targetLanguage <http://lexvo.org/id/iso639-3/%s> ;
       dbnary:writtenForm ?hmong ;
       dbnary:isTranslationOf ?sense .
    ?sense skos:definition/rdf:value ?defn .
    ?entry ontolex:sense ?sense ;
           ontolex:canonicalForm/ontolex:writtenRep ?english ;
           lexinfo:partOfSpeech ?pos .
  }
}
"""


def query(sparql: str, timeout: int = 180) -> list[dict[str, dict[str, str]]]:
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": sparql})
    request = urllib.request.Request(
        url, headers={"Accept": "application/sparql-results+json",
                      "User-Agent": "hmong-wordnet/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as handle:
        return json.load(handle)["results"]["bindings"]


PIVOT_QUERY = """
PREFIX dbnary: <http://kaiko.getalp.org/dbnary#>
PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?hmong ?english ?defn ?lang ?word WHERE {
  VALUES ?lang { %s }
  GRAPH <http://kaiko.getalp.org/dbnary/eng> {
    ?t dbnary:targetLanguage <http://lexvo.org/id/iso639-3/%s> ;
       dbnary:writtenForm ?hmong ;
       dbnary:isTranslationOf ?sense .
    ?sense skos:definition/rdf:value ?defn .
    ?entry ontolex:sense ?sense ;
           ontolex:canonicalForm/ontolex:writtenRep ?english .
    ?other dbnary:isTranslationOf ?sense ;
           dbnary:targetLanguage ?lang ;
           dbnary:writtenForm ?word .
  }
}
"""


def fetch_pivots(iso: str, dialect: str, chunk: int = 7) -> list[dict[str, str]]:
    """The other languages' translations of the senses our Hmong words translate.

    The pivot list is queried in chunks: a single VALUES clause with thirty URIs
    times out on the public endpoint.
    """
    codes = sorted(PIVOTS)
    rows: list[dict[str, str]] = []
    for start in range(0, len(codes), chunk):
        batch = codes[start:start + chunk]
        values = " ".join(f"<http://lexvo.org/id/iso639-3/{c}>" for c in batch)
        found = query(PIVOT_QUERY % (values, iso))
        print(f"  {iso}: {len(found):5} rows for {' '.join(batch)}", file=sys.stderr)
        for b in found:
            rows.append({
                "FORM": b["hmong"]["value"].strip(),
                "DIALECT": dialect,
                "ENGLISH": b["english"]["value"].strip(),
                "DEFINITION": " ".join(b["defn"]["value"].split()),
                "PIVOT_ISO": b["lang"]["value"].rsplit("/", 1)[-1],
                "PIVOT_LEXICON": PIVOTS[b["lang"]["value"].rsplit("/", 1)[-1]],
                "PIVOT_WORD": " ".join(b["word"]["value"].split()),
            })
    return rows


#: Columns of the two outputs, so that a fetch which returns nothing still writes
#: a well-formed empty file. Leaving the previous run's rows on disk is the worse
#: failure: a stale TSV is indistinguishable from a fresh one and silently becomes
#: the input to everything downstream.
COLUMNS = {
    "hmong": ["FORM", "DIALECT", "ISO", "ENGLISH", "POS", "DEFINITION"],
    "pivots": ["FORM", "DIALECT", "ENGLISH", "DEFINITION", "PIVOT_ISO",
               "PIVOT_LEXICON", "PIVOT_WORD"],
}


def write_tsv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    """Write rows as a TSV, header only when there are none."""
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else columns,
                                delimiter="\t",
                                lineterminator="\n", quoting=csv.QUOTE_NONE,
                                escapechar="\\")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("dbnary-hmong.tsv"))
    parser.add_argument("--language", action="append", choices=sorted(LANGUAGES),
                        help="restrict to one language; repeatable")
    parser.add_argument("--pivots-out", type=Path, default=Path("dbnary-pivots.tsv"))
    parser.add_argument("--no-pivots", action="store_true",
                        help="do not fetch the other languages' translations")
    args = parser.parse_args()

    wanted = args.language or sorted(LANGUAGES)
    rows = []
    for iso in wanted:
        found = query(QUERY % iso)
        print(f"{iso}: {len(found)} sense-anchored translations", file=sys.stderr)
        for binding in found:
            rows.append({
                "FORM": binding["hmong"]["value"].strip(),
                "DIALECT": LANGUAGES[iso],
                "ISO": iso,
                "ENGLISH": binding["english"]["value"].strip(),
                "POS": binding["pos"]["value"].rsplit("#", 1)[-1],
                # a Wiktionary definition may run over lines; a TSV may not
                "DEFINITION": " ".join(binding["defn"]["value"].split()),
            })

    seen, unique = set(), []
    for row in rows:
        key = (row["FORM"], row["DIALECT"], row["ENGLISH"], row["DEFINITION"])
        if key not in seen:
            seen.add(key)
            unique.append(row)

    write_tsv(args.out, unique, COLUMNS["hmong"])
    print(f"wrote {args.out}: {len(unique)} rows, "
          f"{len({r['FORM'] for r in unique})} distinct Hmong forms", file=sys.stderr)

    if args.no_pivots:
        return 0
    pivots: list[dict[str, str]] = []
    for iso in wanted:
        pivots.extend(fetch_pivots(iso, LANGUAGES[iso]))
    seen, unique_pivots = set(), []
    for row in pivots:
        key = (row["FORM"], row["DIALECT"], row["DEFINITION"],
               row["PIVOT_ISO"], row["PIVOT_WORD"])
        if key not in seen:
            seen.add(key)
            unique_pivots.append(row)
    write_tsv(args.pivots_out, unique_pivots, COLUMNS["pivots"])
    print(f"wrote {args.pivots_out}: {len(unique_pivots)} rows, "
          f"{len({r['PIVOT_ISO'] for r in unique_pivots})} pivot languages",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
