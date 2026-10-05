#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["wn>=1.1"]
# ///
"""Load the pivot wordnets into a project-local `wn` database, for triangulation.

Triangulation needs every pivot language's wordnet queryable by written form, so
they all have to be in one `wn` database, and which *versions* are in it changes
the links: the method counts languages, so a wordnet at a different release can
move a vote. The releases are therefore not whatever happens to be installed but
the ones pinned in `etc/pivots.toml`. This script reads those pins, loads the
matching WN-LMF files, checks that what landed is what was pinned, and writes the
result to `etc/pivots.lock` so that `hmong2lmf.py` can refuse to triangulate
against anything else.

It never touches the user's `~/.wn_data`: the default target is `.wn_data` beside
this script, and the script refuses to run against the user's home directory.

    uv run load_pivots.py --from ../cygnet/bin/raw_wns
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import tomllib
import wn

#: Where everything lives by default: the data directory, the pin file, and the
#: Cygnet checkout the pins are read from, all relative to this script rather than
#: to whatever directory it is run from.
PROJECT = Path(__file__).resolve().parent
DATA_DIR = PROJECT / ".wn_data"
LOCK = PROJECT / "etc" / "pivots.lock"
#: Our own copy, not a sibling checkout's. Reading the pins from another
#: repository made a build here depend on that repository's working state: a fresh
#: clone of Cygnet pins a different English edition from the one `etc/pivots.lock`
#: records, and the build then fails or, worse, quietly links against the wrong
#: release.
WORDNETS_TOML = PROJECT / "etc" / "pivots.toml"

#: the pivot lexicons triangulation uses, as fetch_dbnary.py names them. The
#: versions are not here: they come from `etc/pivots.toml`, so that there is one
#: place where a release is declared.
PIVOTS = [
    "omw-arb", "omw-bg", "omw-ca", "omw-cmn", "omw-da", "omw-el", "omw-es",
    "omw-eu", "omw-fi", "omw-fr", "omw-gl", "omw-he", "omw-hr", "omw-id",
    "omw-is", "omw-it", "omw-ja", "omw-lt", "omw-nb", "omw-nl", "omw-nn",
    "omw-pl", "omw-ro", "omw-sk", "omw-sq", "omw-sv", "omw-th", "omw-zsm",
]

#: Release archive basenames, mapped to the lexicon id and version `wn` will
#: report once the file is loaded. Two shapes cover everything we pin: the Open
#: Multilingual Wordnet's `omw-<code>-<version>.tar.xz`, and Open English
#: WordNet's `english-wordnet-<year>[-plus].xml.gz`, whose lexicon id is `oewn`.
#: The "plus" edition reports its version as `<year>+`, and it is a different
#: wordnet for our purposes: it carries some 13,000 proper-name synsets the plain
#: edition leaves out, among them the Moon and the Sun.
ARCHIVE_PATTERNS = (
    (re.compile(r"^(omw-[a-z]{2,3})-(\d[\w.]*)\.tar\.xz$"), lambda m: (m[1], m[2])),
    (re.compile(r"^english-wordnet-(\d{4})(-plus)?\.xml\.gz$"),
     lambda m: ("oewn", m[1] + ("+" if m[2] else ""))),
)


def pinned_lexicons(path: Path) -> dict[str, str]:
    """Lexicon id -> version, from the release URLs in a Cygnet-format TOML.

    The file maps language codes to lists of archive URLs, and the version is in
    the archive's filename. URLs whose filename matches neither shape in
    `ARCHIVE_PATTERNS` are skipped, so the same reader works on Cygnet's own
    file, which carries wordnets we do not pivot through.
    """
    with path.open("rb") as handle:
        config = tomllib.load(handle)
    pinned: dict[str, str] = {}
    for urls in config.values():
        for url in urls if isinstance(urls, list) else [urls]:
            basename = str(url).rsplit("/", 1)[-1]
            for pattern, extract in ARCHIVE_PATTERNS:
                found = pattern.match(basename)
                if found:
                    lexicon, version = extract(found)
                    pinned[lexicon] = version
                    break
    return pinned


def read_lock(path: Path) -> dict[str, str]:
    """Lexicon id -> version, from a pin file this script wrote."""
    if not path.exists():
        return {}
    pinned: dict[str, str] = {}
    for line in path.read_text(encoding="utf8").splitlines():
        if line.strip() and not line.startswith("#"):
            lexicon, _, version = line.partition("\t")
            pinned[lexicon.strip()] = version.strip()
    return pinned


def write_lock(path: Path, versions: dict[str, str], source: Path) -> None:
    """Record the lexicons and versions triangulation may use."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Wordnet releases triangulation is pinned to, written by load_pivots.py.",
        f"# Resolved from {source.name}, which is where a release is declared.",
        "# hmong2lmf.py refuses to triangulate against any other version.",
        "#",
        "# lexicon\tversion",
    ]
    lines += [f"{lexicon}\t{version}" for lexicon, version in sorted(versions.items())]
    path.write_text("\n".join(lines) + "\n", encoding="utf8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-directory", type=Path, default=DATA_DIR,
                        help=f"wn data directory to load into (default: {DATA_DIR})")
    parser.add_argument("--from", dest="source", type=Path, required=True,
                        help="directory of WN-LMF files, e.g. ../cygnet/bin/raw_wns")
    parser.add_argument("--wordnets", type=Path, default=WORDNETS_TOML,
                        help=f"the TOML declaring which release of each wordnet to "
                             f"use (default: {WORDNETS_TOML})")
    parser.add_argument("--lock", type=Path, default=LOCK,
                        help=f"where to write the resolved pins (default: {LOCK})")
    parser.add_argument("--english", default="oewn",
                        help="lexicon id of the English wordnet to load as well, or "
                             "the empty string to skip it")
    parser.add_argument("--only", action="append",
                        help="load just this lexicon; repeatable")
    args = parser.parse_args()

    if not args.wordnets.exists():
        raise SystemExit(
            f"{args.wordnets}: not found. It declares which release of each wordnet "
            f"this repository links against, and should be committed beside this "
            f"script; pass --wordnets to use another.")
    pinned = pinned_lexicons(args.wordnets)

    wanted = args.only or ([args.english] if args.english else []) + PIVOTS
    unpinned = [name for name in wanted if name not in pinned]
    if unpinned:
        raise SystemExit(
            f"{args.wordnets} pins no release for: {' '.join(unpinned)}. Add them "
            f"there rather than loading an unpinned version, since which release is "
            f"loaded changes which ILI triangulation chooses.")

    target = args.data_directory.expanduser().resolve()
    if target == (Path.home() / ".wn_data").resolve():
        raise SystemExit("refusing to load into the default ~/.wn_data")
    target.mkdir(parents=True, exist_ok=True)
    wn.config.data_directory = target

    present = {lexicon.id: lexicon.version for lexicon in wn.lexicons()}
    print(f"{len(present)} lexicons already in {target}", file=sys.stderr)
    print(f"{len(pinned)} releases pinned in {args.wordnets}", file=sys.stderr)

    loaded = skipped = failed = 0
    for name in wanted:
        if present.get(name) == pinned[name]:
            skipped += 1
            continue
        if name in present:
            print(f"  {name}: {present[name]} is loaded but {pinned[name]} is "
                  f"pinned; remove it and re-run", file=sys.stderr)
            failed += 1
            continue
        candidates = [Path(name)] if Path(name).exists() else [
            args.source / f"{name}{suffix}"
            for suffix in (".xml", ".xml.gz", ".xml.xz")
        ]
        # Open English WordNet's file is named after its release, not its lexicon,
        # and the "plus" edition's `+` is spelled `-plus` in the filename
        if name == "oewn":
            stem = pinned[name].replace("+", "-plus")
            candidates.insert(0, args.source / f"english-wordnet-{stem}.xml.gz")
        path = next((c for c in candidates if c.exists()), None)
        if path is None:
            print(f"  {name}: no file found in {args.source}", file=sys.stderr)
            failed += 1
            continue
        print(f"  loading {path.name} as {name}:{pinned[name]}", file=sys.stderr)
        try:
            wn.add(str(path), progress_handler=None)
            loaded += 1
        except Exception as error:
            print(f"  {name}: {type(error).__name__}: {error}", file=sys.stderr)
            failed += 1

    # verify, rather than trust: a release whose own metadata disagrees with the
    # filename it shipped under would otherwise pin a version that is not there
    present = {lexicon.id: lexicon.version for lexicon in wn.lexicons()}
    resolved: dict[str, str] = {}
    wrong: list[str] = []
    for name in wanted:
        version = present.get(name)
        if version is None:
            wrong.append(f"{name} is not loaded")
        elif version != pinned[name]:
            wrong.append(f"{name} is {version}, pinned {pinned[name]}")
        else:
            resolved[name] = version

    print(f"\nloaded {loaded}, already at the pinned version {skipped}, failed "
          f"{failed}", file=sys.stderr)
    for lexicon in sorted(wn.lexicons(), key=lambda x: x.id):
        mark = "" if resolved.get(lexicon.id) else "  (not pinned here)"
        print(f"  {lexicon.id:12} {lexicon.language:8} {lexicon.version}{mark}")

    if wrong:
        raise SystemExit("\nnot writing the pin file: " + "; ".join(wrong))
    write_lock(args.lock, resolved, args.wordnets)
    print(f"\nwrote {args.lock}: {len(resolved)} lexicons at their pinned versions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
