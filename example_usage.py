#!/usr/bin/env python3
"""
Example usage of the Jyutping Lookup Tool
"""

from jyutping_lookup import JyutpingLookup


def main():
    # Create a lookup instance
    lookup = JyutpingLookup()

    # Test different types of lookups
    print("=== Comprehensive Lookup Results ===")

    # Test with a full combination
    print("\n1. Query: 'fi' (full combination)")
    results = lookup.lookup("fi")
    print(f"   Exact match: {results['exact']}")
    print(f"   Same initial: {results['initial']}")
    print(f"   Same final: {results['final']}")

    # Test with an initial
    print("\n2. Query: 'f' (initial only)")
    results = lookup.lookup("f")
    print(f"   Exact match: {results['exact']}")
    print(f"   Same initial: {results['initial']}")
    print(f"   Same final: {results['final']}")

    # Test with a final
    print("\n3. Query: 'aa' (final only)")
    results = lookup.lookup("aa")
    print(f"   Exact match: {results['exact']}")
    print(f"   Same initial: {results['initial']}")
    print(f"   Same final: {results['final']}")

    # Test with tone
    print("\n4. Query: 'faa1' (with tone)")
    results = lookup.lookup("faa1")
    print(f"   Exact match: {results['exact']}")
    print(f"   Same initial: {results['initial']}")
    print(f"   Same final: {results['final']}")

    print("\n=== Available Data ===")
    print(f"Available initials: {lookup.get_available_initials()}")
    print(f"Available finals: {lookup.get_available_finals()}")
    print(f"Total combinations available: {len(lookup.get_available_combinations())}")

    print("\n=== JSON File ===")
    print("All 1,121 possible combinations are pre-populated in characters.json")
    print("Edit characters.json directly to add characters to any combination!")
    print("Example: Change 'baa': [] to 'baa': ['巴', '爸'] to add characters")


if __name__ == "__main__":
    main()
