# KG Personal Project

## Quick run order

0. **Setup once**
   - Install dependencies: `pip install -r requirements.txt`
   - Add your keys:
     - YouTube API key in `yt_code/yt_key.txt`
     - LLM key in `data/GPT4oKEY.txt` (or `data/LLM_key.txt` if your notebook uses that file)

> **Note:** If `kg_code/graphs/final_kg.ttl` is already provided, steps 1–10 can be skipped. Go straight to step 11.

1. Run `kg_code/create_KG/base_ontology_KG_03_03.ipynb`
2. Run `data/generate_dances.py` (create synthetic dance data)
3. Run `kg_code/create_KG/KG_base_04_03.ipynb`
4. Run `kg_code/link_KG/merge_similar_instruments.ipynb` (merge similar properties in the KG)
5. Run `kg_code/link_KG/link_KG.ipynb` (link KG entities to Wikidata using embeddings)
6. Run `yt_code/scrape_yt_data.ipynb`
7. Run `yt_code/Sentiment_analysis.ipynb`
8. Run `yt_code/filter_videos.ipynb`
9. Run `yt_code/add_yt_data.ipynb`
10. Run `kg_code/create_KG/KG_yt_data_05_03.ipynb` (merge base KG + YouTube data)
11. Run `ui/ui.py` to explore the final KG
