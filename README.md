# KG Personal Project

## Quick run order

0. **Setup once**
   - Install dependencies from `requirements.txt`.
   - Add your keys:
     - YouTube API key in `yt_code/yt_key.txt`
     - LLM key in `data/GPT4oKEY.txt` (or `data/LLM_key.txt` if your notebook uses that file)

1. Run `kg_code/create_KG/base_ontology_KG_03_03.ipynb`
2. Run `data/generate_dances.py` (create synthetic dance data)
3. Run `kg_code/create_KG/KG_base_04_03.ipynb`
4. Run `yt_code/scrape_yt_data.ipynb`
5. Run `yt_code/Sentiment_analysis.ipynb`
6. Run `yt_code/filter_videos.ipynb`
7. Run `yt_code/add_yt_data.ipynb`
8. Run `kg_code/create_KG/KG_yt_data_05_03.ipynb` (merge base KG + YouTube data)
9. Run `simple_ui/ui.py` to test/query the final KG
