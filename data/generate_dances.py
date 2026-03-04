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
print(f"Using GPT-4o-mini model via OpenRouter")

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)
# Load allowed pairs
pairs = pd.read_csv("allowed_pairs.csv")

# LIMIT TO FIRST 50 PAIRS FOR TESTING
pairs = pairs.head(50)
print(f"Processing first {len(pairs)} dance pairs")

# Load JSON schema
with open("schema.json") as f:
    schema = json.load(f)

def generate_batch(batch_pairs, max_retries=5):
    pairs_text = "\n".join(
        [f"{row['dance_type']} | {row['dance_style']}" for _, row in batch_pairs.iterrows()]
    )

    prompt = f"""Generate dance data as JSON (one object per line). ALL 18 fields required.

FIELDS & CONSTRAINTS:
dance_type, dance_style (from pairs), origin (country/region 1-3 words), time_period (e.g. "1920s", "19th century"), cultural_significance (1-3 sentences, no fake citations), notable_characteristics (1-3 sentences), instruments (list of 1-10 typical instruments/sounds - e.g. "Piano", "Drums", "Guitar", "Electronic synthesizer", "Voice", use "Acapella" or "Body percussion" if no instruments), hardness_ratio (0.0-1.0: difficulty/intensity), dance_formation (pick ONE: Solo, Partner, Group, Circle, Line, Square, Freestyle, Processional, or Mixed), costume (1-2 sentences), tempo_bpm (object with "min" and "max" keys, both integers 40-220 - e.g. {{"min":110,"max":140}}), famous_practitioners (list of 1-5 ONLY if you are 100% certain they are famous for THIS specific dance style - otherwise use generic terms like "Traditional dancers", "Professional dancers", "Community performers"), events_and_festivals (list of 1-5 contexts/events - use generic terms like "Local festivals", "Community celebrations" if unsure), modern_adaptations (1-2 sentences on current use), associated_music_genre (list of 1-5 genre labels - can include multiple if dance spans genres), learning_difficulty (pick ONE: Beginner, Intermediate, or Advanced), health_benefits (list of 1-5), age_group (pick ONE: Kids, Teens, Adults, Seniors, or All ages)

CRITICAL: For famous_practitioners - DO NOT hallucinate or guess. Only include names if you are absolutely certain they are widely recognized for that specific dance style. If unsure, use generic terms like "Professional tap dancers", "Traditional performers", "Contemporary dance artists".

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

            return content.strip().split("\n")

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
    valid = []
    invalid = []

    for row in rows:
        try:
            obj = json.loads(row)
            validate(instance=obj, schema=schema)
            valid.append(obj)
        except (json.JSONDecodeError, ValidationError):
            invalid.append(row)

    return valid, invalid


# Batch processing - reduced size to avoid rate limits
BATCH_SIZE = 10
all_valid = []
all_invalid = []
for i in range(0, len(pairs), BATCH_SIZE):
    batch = pairs.iloc[i:i+BATCH_SIZE]
    batch_num = i // BATCH_SIZE + 1
    total_batches = (len(pairs) + BATCH_SIZE - 1) // BATCH_SIZE

    print(f"\nGenerating batch {batch_num}/{total_batches} (rows {i} to {i+len(batch)-1})...")

    raw_rows = generate_batch(batch)
    valid, invalid = validate_rows(raw_rows)

    print(f"Valid: {len(valid)}, Invalid: {len(invalid)}")

    all_valid.extend(valid)
    all_invalid.extend(invalid)
    # Add delay between batches to avoid rate limiting
    if i + BATCH_SIZE < len(pairs):  # Don't wait after last batch
        print("Waiting 3 seconds before next batch...")
        time.sleep(3)

# Save
with open("dance_dataset.jsonl", "w") as f:
    for row in all_valid:
        f.write(json.dumps(row) + "\n")

# Save
with open("dance_dataset_invalid.jsonl", "w") as f:
    for row in all_invalid:
        f.write(json.dumps(row) + "\n")
print("Done.")