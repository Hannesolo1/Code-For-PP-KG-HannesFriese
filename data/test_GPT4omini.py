import json
import pandas as pd
from jsonschema import validate, ValidationError
from openai import OpenAI
import time

# --- Load API key from file ---
with open("GPT4oKEY.txt", "r") as f:
    api_key = f.read().strip()

if not api_key:
    raise ValueError("API key is empty. Check GPT4oKEY.txt")

print(f"API Key loaded: {len(api_key)} characters")

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)

# Load allowed pairs
pairs = pd.read_csv("allowed_pairs.csv")

# Load JSON schema for validation
with open("schema.json") as f:
    schema = json.load(f)

def generate_batch(batch_pairs, max_retries=5):
    pairs_text = "\n".join(
        [f"{row['dance_type']} | {row['dance_style']}" for _, row in batch_pairs.iterrows()]
    )

    prompt = f"""Generate dance data as JSON (one object per line). ALL 18 fields required.

FIELDS & CONSTRAINTS:
dance_type (from pairs), dance_style (from pairs), origin (country/region 1-3 words), time_period (e.g. "1920s", "19th century"), cultural_significance (1-3 sentences, no fake citations), notable_characteristics (1-3 sentences), instruments (list of 1-10 typical instruments/sounds - e.g. "Piano", "Drums", "Guitar", "Electronic synthesizer", "Voice", use "Acapella" or "Body percussion" if no instruments), hardness_ratio (0.0-1.0: difficulty/intensity), dance_formation (pick ONE: Solo, Partner, Group, Circle, Line, Square, Freestyle, Processional, or Mixed), costume (1-2 sentences), tempo_bpm (object with "min" and "max" keys, both integers 40-220 - e.g. {{"min":110,"max":140}}), famous_practitioners (list of 1-5 ONLY if you are 100% certain they are famous for THIS specific dance style - otherwise use generic terms like "Traditional dancers", "Professional dancers", "Community performers"), events_and_festivals (list of 1-5 contexts/events - use generic terms like "Local festivals", "Community celebrations" if unsure), modern_adaptations (1-2 sentences on current use), associated_music_genre (list of 1-5 genre labels - can include multiple if dance spans genres), learning_difficulty (pick ONE: Beginner, Intermediate, or Advanced), health_benefits (list of 1-5), age_group (pick ONE: Kids, Teens, Adults, Seniors, or All ages)

CRITICAL: For famous_practitioners - DO NOT hallucinate or guess. Only include names if you are absolutely certain they are widely recognized for that specific dance style. If unsure, use generic terms like "Professional tap dancers", "Traditional belly dancers", "Contemporary dance artists".

EXAMPLE:
{{"dance_type":"American","dance_style":"Tap dancing","origin":"United States","time_period":"19th-20th century","cultural_significance":"Popular theatrical and entertainment dance form","notable_characteristics":"Rhythmic footwork with metal taps on shoes","instruments":["Piano","Drums","Double bass","Saxophone"],"hardness_ratio":0.6,"dance_formation":"Solo","costume":"Dress shoes with taps","tempo_bpm":{{"min":110,"max":140}},"famous_practitioners":["Fred Astaire","Gregory Hines","Savion Glover"],"events_and_festivals":["Tap Dance Day","American Tap Festival"],"modern_adaptations":"Modern tap incorporates hip-hop and contemporary styles","associated_music_genre":["Jazz","Swing"],"learning_difficulty":"Intermediate","health_benefits":["Improved cardiovascular health","Stress relief","Improved coordination"],"age_group":"All ages"}}

Pairs: {pairs_text}
Output {len(batch_pairs)} complete JSON objects.
"""

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )

            content = response.choices[0].message.content
            if not content:
                print("Warning: Empty response from API")
                return []

            # Clean up response - remove markdown, code blocks, and extra formatting
            lines = content.strip().split("\n")
            cleaned_lines = []

            for line in lines:
                line = line.strip()
                # Skip empty lines, markdown code blocks, and thinking/explanation text
                if not line or line.startswith("```") or line.startswith("#") or line.startswith("//"):
                    continue
                # Only keep lines that look like JSON objects
                if line.startswith("{") and line.endswith("}"):
                    cleaned_lines.append(line)

            return cleaned_lines

        except Exception as e:
            error_str = str(e)

            # Check if it's a rate limit error (429)
            if '429' in error_str or 'Rate limit' in error_str:
                wait_time = (2 ** attempt) * 2  # Exponential backoff: 2, 4, 8, 16, 32 seconds
                print(f"Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            else:
                # For other errors, raise immediately
                print(f"Error calling API: {e}")
                raise

    # If we exhausted all retries
    raise Exception(f"Failed after {max_retries} retries due to rate limiting")


def validate_rows(rows):
    """Validate parsed JSON objects against the schema"""
    valid = []
    invalid = []

    for row in rows:
        try:
            obj = json.loads(row)
            validate(instance=obj, schema=schema)
            valid.append(obj)
        except json.JSONDecodeError as e:
            invalid.append({"row": row, "error": f"JSON parse error: {str(e)}"})
        except ValidationError as e:
            invalid.append({"row": row, "error": f"Schema validation error: {e.message}", "field": e.path})

    return valid, invalid


# TEST: Just process first 5 pairs
BATCH_SIZE = 5
test_batch = pairs.iloc[0:BATCH_SIZE]

print(f"\n{'='*60}")
print(f"GPT-4o-mini TEST: Processing {len(test_batch)} dance pairs")
print(f"{'='*60}\n")

print("Dance pairs to generate:")
for idx, row in test_batch.iterrows():
    print(f"  - {row['dance_type']} | {row['dance_style']}")

print(f"\nGenerating batch...")

raw_rows = generate_batch(test_batch)

print(f"\n{'='*60}")
print(f"VALIDATION RESULTS:")
print(f"{'='*60}")
print(f"Received {len(raw_rows)} JSON objects from API\n")

# Validate all rows
valid_rows, invalid_rows = validate_rows(raw_rows)

print(f"✓ Valid rows: {len(valid_rows)}")
print(f"✗ Invalid rows: {len(invalid_rows)}\n")

# Display valid rows
if valid_rows:
    print("Valid dance entries:")
    for i, dance in enumerate(valid_rows, 1):
        print(f"  {i}. {dance['dance_type']} - {dance['dance_style']}")
        print(f"     Origin: {dance['origin']}, BPM: {dance['tempo_bpm']}, Difficulty: {dance['learning_difficulty']}")
        print(f"     Age Group: {dance['age_group']}, Formation: {dance['dance_formation']}")
    print()

# Display invalid rows with details
if invalid_rows:
    print("⚠️  Invalid entries:")
    for i, item in enumerate(invalid_rows, 1):
        print(f"  {i}. Error: {item['error'][:120]}")
        if 'field' in item:
            print(f"     Field path: {list(item['field'])}")
        print(f"     Row preview: {item['row'][:100]}...")
        print()

# Save everything
output_file = "test_batch_gpt4omini_validated.json"
with open(output_file, "w") as f:
    json.dump({
        "model": "openai/gpt-4o-mini",
        "total_received": len(raw_rows),
        "valid_count": len(valid_rows),
        "invalid_count": len(invalid_rows),
        "valid_data": valid_rows,
        "invalid_data": invalid_rows
    }, f, indent=2)

print(f"{'='*60}")
print(f"SUMMARY:")
print(f"{'='*60}")
print(f"Total objects received: {len(raw_rows)}")
print(f"Valid (passed schema): {len(valid_rows)}")
print(f"Invalid (failed schema): {len(invalid_rows)}")
print(f"Success rate: {len(valid_rows)/len(raw_rows)*100:.1f}%" if raw_rows else "N/A")
print(f"\nSaved to: {output_file}")
print(f"{'='*60}")

