#!/usr/bin/env python3
"""
Fun coverage checker for characters.json — see which syllable slots are empty.

  python character_coverage.py                  # stats, then ✓ filled, then ◇ gaps (truncated)
  python character_coverage.py --summarize-initials -I   # one line per onset (all initials)
  python character_coverage.py b-               # onset b…
  python character_coverage.py gw-               # onset gw…
  python character_coverage.py /aa               # slice rime …aa (slash avoids argparse eating -aa)
  python character_coverage.py j- /ing           # onset j + rime …ing

  Initial-only vs final-only — use a single filter (no subcommands):
    • Initial-only:  b- …  or  --initial b
    • Final-only :  /aa …  or  --rime aa   (/ avoids argparse eating tokens like -aa)

  python character_coverage.py --rime aa --initial gw    # BOTH onset + rime

  Leading-dash positional finals need argparse "--":
      python character_coverage.py -- -aa -yun

  NO_COLOR (no-color.org) disables ANSI colors. Pass --json for another characters file.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Tuple

from jyutping_lookup import JyutpingLookup


def ansi(code: str) -> Callable[[str], str]:
    def _wrap(s: str) -> str:
        if "NO_COLOR" in os.environ:
            return s
        if not sys.stdout.isatty():
            return s
        return f"{code}{s}\033[0m"

    return _wrap


green = ansi("\033[92m")
pink = ansi("\033[95m")
dim = ansi("\033[2m")
bold = ansi("\033[1m")


def syllable_parts(
    key: str, initials_desc: List[str], finals_set: set
) -> Optional[Tuple[str, str]]:
    for ini in initials_desc:
        if not key.startswith(ini):
            continue
        rime = key[len(ini) :]
        if rime in finals_set:
            return ini, rime
    return None


def is_filled(chars: List) -> bool:
    if not isinstance(chars, list) or not chars:
        return False
    return any(str(c).strip() for c in chars)


def parse_filters(ns: argparse.Namespace, finals_set: set) -> Tuple[Optional[str], Optional[str]]:
    onset_f: Optional[str] = ns.initial_explicit
    rime_f: Optional[str] = ns.rime_explicit
    for raw in ns.filters:
        if raw.endswith("-"):
            if onset_f is not None:
                sys.exit(f"multiple onset filters ({onset_f!r}, {raw!r}); keep one.")
            onset_f = raw[:-1]
        elif raw.startswith("/"):
            r = raw[1:] or ""
            if rime_f is not None:
                sys.exit(f"multiple final filters ({rime_f!r}, {raw!r}); combine with one slash token only.")
            if r not in finals_set:
                sys.exit(f"unknown final after /: {r!r} — not in jyutping_lookup finals list.")
            rime_f = r
        elif raw.startswith("-") and len(raw) > 1:
            r = raw[1:] or ""
            if rime_f is not None:
                sys.exit(f"multiple final filters ({rime_f!r}, {raw!r}); keep one.")
            if r not in finals_set:
                sys.exit(f"unknown final {r!r} (after -): not in jyutping_lookup finals list.")
            rime_f = r
        else:
            sys.exit(
                f"unknown token {raw!r}. Use onset b-/gw-/…, finals as /aa or /ing (--rime also works)."
            )

    return onset_f, rime_f


def summarize_initials(
    path: str,
    lookup: JyutpingLookup,
    initials_desc: List[str],
    finals_set: set,
) -> None:
    with open(path, encoding="utf-8") as f:
        chars_map: Dict[str, list] = json.load(f)

    grouped: Dict[str, List[Tuple[str, list]]] = defaultdict(list)
    skipped = 0
    for key, ch in chars_map.items():
        parts = syllable_parts(key, initials_desc, finals_set)
        if parts is None:
            skipped += 1
            continue
        ini, _ = parts
        grouped[ini].append((key, ch))

    print(bold("\nCoverage by initial") + f" ({path})")
    if skipped:
        print(dim(f"  ({skipped} keys not in initials×finals grid — skipped)"))
    print()
    hdr = f"  {'onset':<4}  {'filled':>5}  {'total':>5}  {'pct':>6}  {'empty':>5}"
    print(dim(hdr))
    print(dim("  " + "─" * 38))

    g_ok = g_tot = 0
    for ini in lookup.initials.keys():
        rows = grouped.get(ini, [])
        tot = len(rows)
        ok = sum(1 for _, ch in rows if is_filled(ch))
        g_ok += ok
        g_tot += tot
        miss = tot - ok
        pct = (100.0 * ok / tot) if tot else 0.0
        line = f"  {ini:<4}  {ok:5d}  {tot:5d}  {pct:5.1f}%  {miss:5d}"
        if tot == 0:
            print(dim(line + "  (no keys)"))
        elif miss == 0:
            print(green(line + "  ✓"))
        elif ok == 0:
            print(pink(line))
        else:
            print(line)

    print(dim("  " + "─" * 38))
    gpct = (100.0 * g_ok / g_tot) if g_tot else 0.0
    tail = f"  {'ALL':<4}  {g_ok:5d}  {g_tot:5d}  {gpct:5.1f}%  {g_tot - g_ok:5d}"
    print(bold(tail))
    print()
    print(dim("  drill down:  python character_coverage.py <onset>-   e.g.  python character_coverage.py b-"))
    print()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "filters",
        nargs="*",
        metavar="FILTER",
        help="onset tokens like b-/gw-, rime tokens like /aa; use `-- -aa` after -- for dashed finals only",
    )
    ap.add_argument("--json", default="characters.json", help="path to characters.json")
    ap.add_argument(
        "-I",
        "--summarize-initials",
        action="store_true",
        help="print a compact table for every onset (ignores other filters)",
    )
    ap.add_argument(
        "--all",
        action="store_true",
        help="no truncation — print every matching pink and green row",
    )
    ap.add_argument(
        "--no-filled",
        action="store_true",
        help="omit the green ✓ list (only show empty ◇ syllables)",
    )
    ap.add_argument(
        "--max-missing-print",
        type=int,
        default=40,
        help="without --all: max pink ◇ rows",
    )
    ap.add_argument(
        "--max-filled-print",
        type=int,
        default=80,
        help="without --all: max green ✓ rows",
    )
    ap.add_argument(
        "--initial",
        dest="initial_explicit",
        default=None,
        metavar="ONSET",
        help="onset slice without hyphen (example: gw) — avoids parsing issues",
    )
    ap.add_argument(
        "--rime",
        dest="rime_explicit",
        default=None,
        metavar="FINAL",
        help="rime slice — same as positional /FINAL form",
    )
    ns = ap.parse_args()
    ns.filters = ns.filters if ns.filters else []

    if ns.initial_explicit is not None and ns.initial_explicit.endswith("-"):
        ns.initial_explicit = ns.initial_explicit[:-1]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = ns.json
    if not os.path.isabs(path):
        path = os.path.join(script_dir, path)
    if not os.path.isfile(path):
        sys.exit(f"cannot read {path!r}")

    lookup = JyutpingLookup(path)
    initials_desc = sorted(lookup.initials.keys(), key=lambda s: (-len(s), s))
    finals_set = set(lookup.finals.keys())

    if ns.summarize_initials:
        if ns.filters or ns.initial_explicit is not None or ns.rime_explicit is not None:
            sys.exit("use --summarize-initials alone (omit b-, /aa, --initial, --rime, etc.).")
        summarize_initials(path, lookup, initials_desc, finals_set)
        return

    if ns.rime_explicit is not None and ns.rime_explicit not in finals_set:
        sys.exit(f"--rime value {ns.rime_explicit!r} is not a known final.")

    onset_filter, rime_filter = parse_filters(ns, finals_set)

    if onset_filter is not None and onset_filter not in lookup.initials:
        sys.exit(f"onset filter {onset_filter + '-'} is not a known initial (try b-, gw-, …).")

    with open(path, encoding="utf-8") as f:
        chars_map: Dict[str, list] = json.load(f)

    rows: List[Tuple[str, list]] = []
    for key in chars_map.keys():
        parts = syllable_parts(key, initials_desc, finals_set)
        if parts is None:
            continue
        ini, rime = parts
        if onset_filter is not None and ini != onset_filter:
            continue
        if rime_filter is not None and rime != rime_filter:
            continue
        rows.append((key, chars_map[key]))

    total = len(rows)
    filled = sum(1 for _, ch in rows if is_filled(ch))
    holes = [(k, ch) for k, ch in rows if not is_filled(ch)]

    desc_parts = []
    if onset_filter is not None:
        desc_parts.append(f"onset {bold(onset_filter + '*')}")
    if rime_filter is not None:
        desc_parts.append(f"rime *{bold(rime_filter)}")
    desc = bold("everything") if not desc_parts else " + ".join(desc_parts)

    pct = (100.0 * filled / total) if total else 0.0
    print(bold("\ncharacters.json coverage") + f" ({path})")
    print(f" slice: {desc}")
    print(
        green(f"  filled: {filled}")
        + "  "
        + pink(f"missing (empty arrays): {len(holes)}")
        + f"  of {total}  ({pct:.1f}% done)"
    )

    wins_sorted = sorted([(k, ch) for k, ch in rows if is_filled(ch)], key=lambda x: x[0])

    def line_for(key: str, ch: List) -> str:
        filled_here = is_filled(ch)
        label = bold(key)
        detail = "; ".join(c for c in ch if str(c).strip())
        if filled_here:
            preview = detail[:72] + ("…" if len(detail) > 72 else "")
            return green(f"  ✓ {label}") + (f"  {preview}" if preview else "")
        return pink(f"  ◇ {label}  …empty")

    print()

    if total == 0:
        print(pink("no syllables matched your filters.\n"))
        return

    all_green = not holes

    if not ns.no_filled and wins_sorted:
        show_all_green = ns.all or len(wins_sorted) <= ns.max_filled_print
        cap_w = len(wins_sorted) if show_all_green else ns.max_filled_print
        slice_w = wins_sorted[:cap_w]
        print(green(bold(f"Syllables with characters ✓ ({len(wins_sorted)}):")))
        for k, ch in slice_w:
            print(line_for(k, ch))
        if not show_all_green and cap_w < len(wins_sorted):
            over = len(wins_sorted) - cap_w
            print(
                green(
                    "  … "
                    + str(over)
                    + " more green rows (--all or raise --max-filled-print)"
                )
            )
        print()

    if all_green:
        print(green(bold("    ☀ Every syllable in this slice already has ≥1 glyph.")))
        print()

    if holes:
        show_all_missing = ns.all or len(holes) <= ns.max_missing_print
        print(pink(bold(f"still wants love ({len(holes)}):")))
        slice_holes = holes if show_all_missing else holes[: ns.max_missing_print]
        for k, ch in slice_holes:
            print(line_for(k, ch))
        if not show_all_missing:
            rest = len(holes) - len(slice_holes)
            if rest > 0:
                print(pink(f"  … plus {rest} more missing (--all prints them all)"))

    print()


if __name__ == "__main__":
    main()
