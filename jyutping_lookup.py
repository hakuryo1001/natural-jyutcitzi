#!/usr/bin/env python3
"""
Jyutping Character Lookup Tool

This program finds characters that have the same pronunciation as a given
Jyutping combination, initial, or final.
"""

import re
import json
import os
from typing import List, Dict, Set, Optional


class JyutpingLookup:
    def __init__(self, characters_file="characters.json"):
        # Initialize the pronunciation database
        self.initials = {}
        self.finals = {}
        self.characters = {}  # Will store pronunciation -> characters mappings
        self.characters_file = characters_file

        # Parse the natural initials and finals from the provided data
        self._parse_pronunciation_data()

        # Load characters from JSON file
        self.load_characters()

    def _parse_pronunciation_data(self):
        """Parse the initials and finals data from the provided format."""

        # Cantonese initials
        initials = [
            "b",
            "p",
            "m",
            "f",
            "d",
            "t",
            "n",
            "l",
            "g",
            "k",
            "ng",
            "h",
            "gw",
            "kw",
            "w",
            "z",
            "c",
            "s",
            "j",
        ]

        # Cantonese finals
        finals = [
            "aa",
            "aai",
            "aau",
            "aam",
            "aan",
            "aang",
            "aap",
            "aat",
            "aak",
            "a",
            "ai",
            "au",
            "am",
            "an",
            "ang",
            "ap",
            "at",
            "ak",
            "e",
            "ei",
            "eu",
            "em",
            "eng",
            "ep",
            "et",
            "ek",
            "i",
            "iu",
            "im",
            "in",
            "ing",
            "ip",
            "it",
            "ik",
            "o",
            "oi",
            "ou",
            "on",
            "ong",
            "ot",
            "ok",
            "u",
            "ui",
            "un",
            "ung",
            "ut",
            "uk",
            "eoi",
            "eon",
            "eot",
            "oe",
            "oeng",
            "oet",
            "oek",
            "yu",
            "yun",
            "yut",
            "m",
            "ng",
        ]

        # Initialize the dictionaries with the clean lists
        for initial in initials:
            self.initials[initial] = {"ipa": "", "example": ""}

        for final in finals:
            self.finals[final] = {"ipa": "", "example": ""}

    def _remove_tone(self, jyutping: str) -> str:
        """Remove tone numbers from Jyutping (1-6) to get base pronunciation."""
        # Remove tone numbers 1-6 from the end
        return re.sub(r"[1-6]$", "", jyutping)

    def load_characters(self):
        """Load characters from JSON file."""
        if os.path.exists(self.characters_file):
            try:
                with open(self.characters_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.characters = data
            except (json.JSONDecodeError, FileNotFoundError):
                self.characters = {}
        else:
            self.characters = {}

    def find_by_full_combination(self, jyutping: str) -> List[str]:
        """Find characters that match the full Jyutping combination."""
        # Remove tone for lookup
        base_jyutping = self._remove_tone(jyutping)
        if base_jyutping in self.characters:
            return self.characters[base_jyutping].copy()
        return []

    def find_by_initial(self, initial: str) -> List[str]:
        """Find characters that have the same initial."""
        if initial not in self.initials:
            return []

        # Find all characters that start with this initial
        matching_chars = []
        for jyutping, chars in self.characters.items():
            if jyutping.startswith(initial):
                matching_chars.extend(chars)
        return matching_chars

    def find_by_final(self, final: str) -> List[str]:
        """Find characters that have the same final."""
        if final not in self.finals:
            return []

        # Find all characters that end with this final
        matching_chars = []
        for jyutping, chars in self.characters.items():
            if jyutping.endswith(final):
                matching_chars.extend(chars)
        return matching_chars

    def lookup(self, query: str) -> Dict[str, List[str]]:
        """
        Main lookup function that returns comprehensive results for any query.

        Args:
            query: Jyutping combination, initial, or final

        Returns:
            Dictionary with three lists:
            - 'exact': Characters matching the exact combination
            - 'initial': Characters with the same initial
            - 'final': Characters with the same final
        """
        query = query.strip().lower()

        # Get exact combination match (with tone removal)
        exact_result = self.find_by_full_combination(query)

        # Determine if query is an initial or final
        is_initial = query in self.initials
        is_final = query in self.finals

        # Get initial matches
        if is_initial:
            initial_result = self.find_by_initial(query)
        else:
            # Try to extract initial from the query
            initial_result = []
            for initial in self.initials.keys():
                if query.startswith(initial):
                    initial_result.extend(self.find_by_initial(initial))

        # Get final matches
        if is_final:
            final_result = self.find_by_final(query)
        else:
            # Try to extract final from the query
            final_result = []
            for final in self.finals.keys():
                if query.endswith(final):
                    final_result.extend(self.find_by_final(final))

        return {"exact": exact_result, "initial": initial_result, "final": final_result}

    def get_available_initials(self) -> List[str]:
        """Get list of available initials."""
        return list(self.initials.keys())

    def get_available_finals(self) -> List[str]:
        """Get list of available finals."""
        return list(self.finals.keys())

    def get_available_combinations(self) -> List[str]:
        """Get list of available full combinations."""
        return list(self.characters.keys())


def main():
    """Main function for command line usage."""
    import sys

    lookup = JyutpingLookup()

    if len(sys.argv) != 2:
        print("Usage: python jyutping_lookup.py <jyutping_query>")
        print("Examples:")
        print("  python jyutping_lookup.py fi")
        print("  python jyutping_lookup.py f")
        print("  python jyutping_lookup.py i")
        print("\nNote: Characters are stored in characters.json")
        print("Edit characters.json directly to add characters")
        sys.exit(1)

    query = sys.argv[1]
    results = lookup.lookup(query)

    print(f"Results for '{query}':")
    print(f"  Exact match: {results['exact'] if results['exact'] else 'None'}")
    print(f"  Same initial: {results['initial'] if results['initial'] else 'None'}")
    print(f"  Same final: {results['final'] if results['final'] else 'None'}")

    # Show total counts
    total_chars = len(set(results["exact"] + results["initial"] + results["final"]))
    if total_chars > 0:
        print(f"\nTotal unique characters found: {total_chars}")
    else:
        print(f"\nNo characters found for '{query}'")


if __name__ == "__main__":
    main()
