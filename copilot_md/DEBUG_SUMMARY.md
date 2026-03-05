# Dance Dataset Generator - Debug Summary

## Problem Fixed
The script was trying to use the model `deepseek/deepseek-r1:free` which doesn't exist on OpenRouter, resulting in a 404 error.

## Solution
Changed to `meta-llama/llama-3.2-3b-instruct:free` which is a working free model on OpenRouter.

## Changes Made

### 1. Model Update
- **Old:** `deepseek/deepseek-r1:free` (404 - doesn't exist)
- **New:** `meta-llama/llama-3.2-3b-instruct:free` (works, but rate limited)

### 2. Added Rate Limit Handling
The free model has strict rate limits. Added exponential backoff retry logic:
- Retry up to 5 times on 429 (rate limit) errors
- Wait times: 2, 4, 8, 16, 32 seconds
- Immediate failure on other errors

### 3. Reduced Batch Size
- **Old:** 30 rows per batch
- **New:** 10 rows per batch
- Reduces API load and rate limit hits

### 4. Added Inter-Batch Delays
- 3-second wait between batches
- Helps avoid hitting rate limits

### 5. Better Progress Tracking
- Shows batch number (e.g., "Generating batch 3/42")
- Shows row range being processed
- Clear validation feedback

## API Key Requirements
Your API key should:
- Start with `sk-or-v1-` (OpenRouter format)
- Be stored in `LLM_key.txt`
- Have access to free models

## Expected Behavior
With 420 dance pairs and batch size of 10:
- **Total batches:** 42
- **Time per batch:** 5-35 seconds (depending on rate limits)
- **Total time:** 4-25 minutes (with retries and delays)

## Running the Script
```bash
cd /Users/hannes/Documents/GitHub/KG_Personal_Project/data
python generate_dances.py
```

## Output
- Creates `dance_dataset.jsonl` with validated dance data
- Each line is a JSON object matching the schema
- Shows progress and validation stats for each batch

## Troubleshooting

### If you still get 404 errors:
The model name might have changed. Check OpenRouter's model list or try:
- `nousresearch/hermes-3-llama-3.1-405b:free`
- Any other model from: https://openrouter.ai/models?order=newest

### If you get 429 (rate limit) errors:
- The script already handles this with retries
- Wait times increase exponentially
- If it keeps failing, the free tier might be exhausted temporarily
- Try again in 1 hour or use a paid model

### If you get 403 (limit exceeded):
- Your OpenRouter account has hit its free tier limit
- Add credits at: https://openrouter.ai/credits
- Or wait for the limit to reset

## Test Files Created
- `test_api.py` - Tests API connection
- `test_models.py` - Tests which models work
- `test_generation.py` - Tests generation with 2 dance pairs

