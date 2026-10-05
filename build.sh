#!/usr/bin/env bash
#
# build.sh - Generate the Hmong WN-LMF lexicons and build the Cygnet databases.
#
# Two steps. First hmong2lmf.py turns hmong_ontology.xml into one WN-LMF file per
# dialect; then Cygnet merges those with English WordNet, so that a Hmong synset
# is reachable from an English word through the shared Interlingual Index.
#
# Cygnet is expected as a sibling checkout (../cygnet). Pre-downloaded English
# WordNet and CILI files are reused from it when present, so a rebuild needs no
# network. Pass --download to let Cygnet fetch what is missing.
#
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Cygnet is optional. Stage 1 -- the part that makes the wordnet -- needs only
# this repository; stage 2 builds the browsable lookup and is skipped when the
# Cygnet checkout or the lookup's own configuration is not here, so that the
# lexicons can be built on a branch that does not carry them.
CYGNET_DIR="$(cd "$PROJECT_DIR/../cygnet" 2>/dev/null && pwd || true)"
WORK_DIR="$PROJECT_DIR/build/cygnet-work"
CONCEPTICON="${CONCEPTICON:-$PROJECT_DIR/../cldf2wn/data/concepticon-ili.tsv}"
ENGLISH="${ENGLISH:-oewn:2025+}"
WN_DATA="${WN_DATA:-$PROJECT_DIR/.wn_data}"
PIN_FILE="${PIN_FILE:-$PROJECT_DIR/etc/pivots.lock}"
# Set CLDF to DIR:LANGUAGE:NAME[:DIALECT] to fold in a CLDF wordlist, e.g.
# CLDF=../wold/cldf:WhiteHmong:WOLD:WH
CLDF="${CLDF:-$PROJECT_DIR/../wold/cldf:WhiteHmong:WOLD:WH}"
LICENSE="https://creativecommons.org/licenses/by/4.0/"
VERSION="0.1"

DOWNLOAD=--build-only
[[ "${1:-}" == "--download" ]] && DOWNLOAD=""

# --- 1. ontology -> WN-LMF ------------------------------------------------
mkdir -p "$PROJECT_DIR/build" "$WORK_DIR/bin/raw_wns"

# Every route the paper reports is part of the build, so that the released
# lexicon is the one the figures describe. A route whose input is missing is
# skipped with a note saying what that costs; facts.py reports the full figures.
route_args=()
if [[ -f "$CONCEPTICON" ]]; then
    route_args+=(--concepticon "$CONCEPTICON")
else
    echo "note: $CONCEPTICON not found; building without the Concepticon route," >&2
    echo "      which costs about 1,150 of the 2,100 interlingual links." >&2
fi
# The pivot wordnets are pinned to the releases named in etc/pivots.toml.
# load_pivots.py resolves those pins into etc/pivots.lock and hmong2lmf.py refuses
# to triangulate against any other version: triangulation counts languages, so a
# wordnet at a different release can change which ILI wins.
# `etc/pivots.lock` is in the repository, so its presence says nothing about
# whether the wordnets it names are on *this* machine. What matters is the data
# directory, which is not in the repository: a fresh clone has the lock file and
# no lexicons at all, and passing --english to a wn database with nothing in it
# fails deep inside the library with "no lexicon found".
if [[ ! -f "$WN_DATA/wn.db" && -n "$CYGNET_DIR" ]]; then
    echo "=== loading the pinned wordnets -> $WN_DATA ==="
    uv run "$PROJECT_DIR/load_pivots.py" \
        --data-directory "$WN_DATA" \
        --from "$CYGNET_DIR/bin/raw_wns" \
        --lock "$PIN_FILE" || true
fi
if [[ -f "$WN_DATA/wn.db" ]]; then
    route_args+=(--data-directory "$WN_DATA" --pin-file "$PIN_FILE"
                 --english "$ENGLISH")
    [[ -f "$PROJECT_DIR/dbnary-pivots.tsv" ]] && \
        route_args+=(--pivots "$PROJECT_DIR/dbnary-pivots.tsv")
    [[ -f "$PROJECT_DIR/dbnary-hmong.tsv" ]] && \
        route_args+=(--dbnary "$PROJECT_DIR/dbnary-hmong.tsv")
else
    echo "note: no wordnets are loaded in $WN_DATA, so this build has neither" >&2
    echo "      triangulation nor the Wiktionary route, which together cost" >&2
    echo "      about 350 interlingual concepts. To add them:" >&2
    echo "        uv run load_pivots.py --from ../cygnet/bin/raw_wns" >&2
fi
if [[ -n "$CLDF" && -d "${CLDF%%:*}" ]]; then
    route_args+=(--cldf "$CLDF")
else
    echo "note: ${CLDF%%:*} not found; building without the CLDF wordlist," >&2
    echo "      which costs about 845 interlingual concepts." >&2
fi

for dialect in WH GM; do
    case "$dialect" in
        WH) stem=hmnont ;;
        GM) stem=hmnont-gm ;;
    esac
    echo "=== $dialect -> $stem ==="
    uv run "$PROJECT_DIR/hmong2lmf.py" \
        --ontology "$PROJECT_DIR/hmong_ontology.xml" \
        --output "$PROJECT_DIR/build/$stem.xml" \
        --report "$PROJECT_DIR/build/$stem-report.tsv" \
        --dialect "$dialect" \
        --version "$VERSION" \
        --license "$LICENSE" \
        --citation "$(tr '\n' ' ' < "$PROJECT_DIR/etc/citation.rst")" \
        --pivot-review "$PROJECT_DIR/review-triangulation-$dialect.tsv" \
        --dbnary-review "$PROJECT_DIR/review-wiktionary-$dialect.tsv" \
        "${route_args[@]}"
    gzip -cf "$PROJECT_DIR/build/$stem.xml" > "$WORK_DIR/bin/raw_wns/$stem.xml.gz"
done

# --- 2. WN-LMF -> Cygnet databases ---------------------------------------
if [[ -z "$CYGNET_DIR" || ! -f "$PROJECT_DIR/etc/wordnets.toml" ]]; then
    echo
    echo "built $PROJECT_DIR/build/hmnont.xml and hmnont-gm.xml"
    [[ -z "$CYGNET_DIR" ]] \
        && echo "skipping the online lookup: no ../cygnet checkout" >&2 \
        || echo "skipping the online lookup: no etc/wordnets.toml" >&2
    exit 0
fi

cp "$PROJECT_DIR/etc/wordnets.toml" "$WORK_DIR/wordnets.toml"

# Stage exactly one English wordnet, the pinned edition, derived from $ENGLISH:
# "oewn:2025+" -> english-wordnet-2025-plus.xml.gz, and lexicon oewn:2025+.
#
# Every edition declares the lexicon id `oewn`, so if two of them reach the
# synthesis stage Cygnet merges `oewn` twice and dies with "Duplicate concept id:
# oewn.i1". That happens to anyone whose work directory was built against a
# different edition, and it has to be cleaned in *two* places: the input files in
# raw_wns/, and the converted intermediates in cygnets_presynth/, which stage 6
# reads wholesale. Cleaning only the first leaves the build failing later with the
# same error.
english_version="${ENGLISH#oewn:}"
english_file="english-wordnet-${english_version/+/-plus}.xml.gz"
find "$WORK_DIR/bin/raw_wns" -maxdepth 1 -name 'english-wordnet-*.xml.gz' \
    ! -name "$english_file" -delete
if [[ -d "$WORK_DIR/bin/cygnets_presynth" ]]; then
    find "$WORK_DIR/bin/cygnets_presynth" -maxdepth 1 -name 'oewn-*' \
        ! -name "oewn-${english_version}.xml" \
        ! -name "oewn-${english_version}_log.json" -delete
fi
if [[ ! -f "$WORK_DIR/bin/raw_wns/$english_file" ]]; then
    if [[ -f "$CYGNET_DIR/bin/raw_wns/$english_file" ]]; then
        cp "$CYGNET_DIR/bin/raw_wns/$english_file" "$WORK_DIR/bin/raw_wns/"
    else
        echo "note: $english_file is not in $CYGNET_DIR/bin/raw_wns;" >&2
        echo "      Cygnet will download it." >&2
    fi
fi
[[ -f "$WORK_DIR/bin/cili.tsv" ]] || { [[ -f "$CYGNET_DIR/bin/cili.tsv" ]] && \
    cp "$CYGNET_DIR/bin/cili.tsv" "$WORK_DIR/bin/cili.tsv"; } || true

# Cygnet's build.sh runs `uv run playwright install chromium` as part of setting up
# its Python environment, and `set -e` makes that fatal. Playwright is only needed
# for Cygnet's own browser tests, so on a platform Playwright does not support --
# Ubuntu 26.04 among them -- a test-only dependency stops the databases being built
# at all. The one-line fix belongs upstream:
#
#     uv run playwright install chromium || true
#
# Until it lands, fall back to driving the pipeline stages directly. They are the
# same stages in the same order; only the environment setup is different, and the
# `uv sync` that matters has already run by the time the playwright step fails.
if ! bash "$CYGNET_DIR/build.sh" --work-dir "$WORK_DIR" ${DOWNLOAD:+$DOWNLOAD}; then
    echo
    echo "=== Cygnet's build.sh failed; running its pipeline stages directly ===" >&2
    ( cd "$CYGNET_DIR" && uv sync )
    for stage in 1_extract_cili 2_batch_convert_lmfs 6_synthesise 9_lang_codes \
                 11_add_arasaac; do
        echo "=== $stage ==="
        ( cd "$WORK_DIR" && uv run --project "$CYGNET_DIR" \
            python "$CYGNET_DIR/conversion_scripts/$stage.py" )
    done
    gzip -k -9 -f "$WORK_DIR/web/cygnet.db"
    gzip -k -9 -f "$WORK_DIR/web/provenance.db"
fi

# --- 3. credit the wordnets, and recompute the figures -------------------
# Both are generated from what was actually loaded, so neither the citations nor
# the figures can drift from the build they describe.
if [[ -f "$PIN_FILE" ]]; then
    uv run "$PROJECT_DIR/cite_wordnets.py" \
        --data-directory "$WN_DATA" --pin-file "$PIN_FILE" \
        --out "$PROJECT_DIR/wordnets-cited.tsv" \
        ${PAPER_DIR:+--latex "$PAPER_DIR/wordnets.tex"}
fi

# --- 4. publish into docs/ -----------------------------------------------
cp "$WORK_DIR/web/cygnet.db.gz"     "$PROJECT_DIR/docs/hmong.db.gz"
cp "$WORK_DIR/web/provenance.db.gz" "$PROJECT_DIR/docs/hmong-provenance.db.gz"
echo
echo "built docs/hmong.db.gz and docs/hmong-provenance.db.gz"
echo "preview with ./run.sh"
