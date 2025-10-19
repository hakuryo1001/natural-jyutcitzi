# Jyutping Character Lookup Tool

A Python tool for finding Chinese characters based on their Cantonese pronunciation using Jyutping romanization. The tool provides comprehensive lookup results including exact matches, characters with the same initial, and characters with the same final.

## Features

- **Comprehensive Lookup**: Returns three types of results for any query
- **Tone-Agnostic**: Automatically handles Jyutping with or without tone numbers
- **Pre-populated Database**: All 1,121 possible Cantonese combinations included
- **JSON Storage**: Easy character management through `characters.json`
- **Command Line Interface**: Simple terminal usage
- **Python API**: Programmatic access for integration

## Installation

No installation required! Just ensure you have Python 3.6+ installed.

## Quick Start

### Command Line Usage

```bash
# Navigate to the project directory
cd /Users/hongjan/Documents/natural-jyutcitzi

# Look up characters by full combination
python3 jyutping_lookup.py fi

# Look up characters by initial
python3 jyutping_lookup.py f

# Look up characters by final
python3 jyutping_lookup.py aa

# Look up with tone (automatically handled)
python3 jyutping_lookup.py faa1
```

### Example Output

```bash
$ python3 jyutping_lookup.py fi
Results for 'fi':
  Exact match: ['𩇫']
  Same initial: ['花', '𩇫']
  Same final: ['𩇫']

Total unique characters found: 2
```

## Python API Usage

```python
from jyutping_lookup import JyutpingLookup

# Create lookup instance
lookup = JyutpingLookup()

# Get comprehensive results
results = lookup.lookup('fi')
print(results['exact'])    # ['𩇫']
print(results['initial'])  # ['花', '𩇫']
print(results['final'])    # ['𩇫']

# Different query types
results = lookup.lookup('f')    # Initial only
results = lookup.lookup('aa')   # Final only
results = lookup.lookup('faa1') # With tone
```

## Understanding the Results

The lookup function returns a dictionary with three lists:

- **`exact`**: Characters matching the exact Jyutping combination
- **`initial`**: Characters starting with the same initial sound
- **`final`**: Characters ending with the same final sound

## Adding Characters

Edit `characters.json` directly to add characters:

```json
{
  "baa": ["巴", "爸", "把"],
  "maa": ["媽", "馬"],
  "faa": ["花", "化"]
}
```

### Example: Adding Characters

1. Open `characters.json` in a text editor
2. Find the combination you want (e.g., `"baa": []`)
3. Add characters: `"baa": ["巴", "爸", "把"]`
4. Save the file
5. Use the tool immediately - no restart needed

## Available Combinations

The database includes all 1,121 possible Cantonese combinations:

- **19 Initials**: b, p, m, f, d, t, n, l, g, k, ng, h, gw, kw, w, z, c, s, j
- **59 Finals**: aa, aai, aau, aam, aan, aang, aap, aat, aak, a, ai, au, am, an, ang, ap, at, ak, e, ei, eu, em, eng, ep, et, ek, i, iu, im, in, ing, ip, it, ik, o, oi, ou, on, ong, ot, ok, u, ui, un, ung, ut, uk, eoi, eon, eot, oe, oeng, oet, oek, yu, yun, yut, m, ng

## File Structure

```
natural-jyutcitzi/
├── jyutping_lookup.py    # Main lookup tool
├── characters.json       # Character database (1,121 combinations)
├── example_usage.py      # Usage examples
└── README.md            # This file
```

## Examples

### Full Combination Lookup

```bash
$ python3 jyutping_lookup.py faa
Results for 'faa':
  Exact match: ['花']
  Same initial: ['花', '𩇫']
  Same final: ['巴', '怕', '媽', '花']

Total unique characters found: 4
```

### Initial Lookup

```bash
$ python3 jyutping_lookup.py f
Results for 'f':
  Exact match: None
  Same initial: ['花', '𩇫']
  Same final: None

Total unique characters found: 2
```

### Final Lookup

```bash
$ python3 jyutping_lookup.py aa
Results for 'aa':
  Exact match: None
  Same initial: None
  Same final: ['巴', '怕', '媽', '花']

Total unique characters found: 4
```

## Advanced Usage

### Programmatic Character Addition

While the tool is designed for JSON editing, you can also add characters programmatically:

```python
from jyutping_lookup import JyutpingLookup
import json

# Load the JSON file
with open('characters.json', 'r', encoding='utf-8') as f:
    characters = json.load(f)

# Add characters
characters['baa'].extend(['把', '霸'])
characters['maa'].extend(['麻', '馬'])

# Save back to JSON
with open('characters.json', 'w', encoding='utf-8') as f:
    json.dump(characters, f, ensure_ascii=False, indent=2)
```

### Batch Processing

```python
from jyutping_lookup import JyutpingLookup

lookup = JyutpingLookup()

# Process multiple queries
queries = ['fi', 'faa', 'maa', 'baa']
for query in queries:
    results = lookup.lookup(query)
    print(f"{query}: {len(results['exact'])} exact, {len(results['initial'])} initial, {len(results['final'])} final")
```

## Troubleshooting

### Common Issues

1. **No characters found**: The combination might not exist in the database yet
2. **Empty results**: Check if the combination is valid Jyutping
3. **JSON errors**: Ensure proper JSON formatting when editing `characters.json`

### Validating Input

The tool accepts:

- Full combinations: `fi`, `faa`, `maa`
- Initials only: `f`, `m`, `b`
- Finals only: `i`, `aa`, `ai`
- With tones: `faa1`, `maa2` (tones are automatically removed)

## Contributing

To add new characters:

1. Edit `characters.json`
2. Add characters to the appropriate combination arrays
3. Test with the lookup tool
4. Characters are immediately available

## License

This tool is provided as-is for educational and research purposes.
