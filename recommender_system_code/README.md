# Simple SPARQL Wrapper

Very small Python helper for running SPARQL against `kg_code/dance_kg_with_data.ttl`.

## Files
- `simple_sparql_wrapper.py`: wrapper class (`SimpleDanceKG`)
- `demo_simple_sparql.py`: tiny runnable example

## Quick Start
```bash
pip install -r requirements.txt
python recommender_system_code/demo_simple_sparql.py
```

The demo prints a few styles, then asks you to enter a dance style name and returns matching KG records.

## Usage
```python
from recommender_system_code.simple_sparql_wrapper import SimpleDanceKG

kg = SimpleDanceKG()
rows = kg.top_dance_styles(limit=5)
print(rows)
```
