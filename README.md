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

---

## Metadata

Dataset metadata (title, description, license, provenance, vocabularies, distribution info, and citation) is available in:
- **[`metadata.json`](./metadata.json)** – full metadata in JSON format (DCAT / VoID / DCTerms)
- **[`kg_code/graphs/final_kg.ttl`](./kg_code/graphs/final_kg.ttl)** – metadata also embedded directly in the KG as a VoID/DCAT dataset description block

---

## License

This project is licensed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license.  
You are free to share and adapt the material for any purpose, provided appropriate credit is given.  
See the full license at: https://creativecommons.org/licenses/by/4.0/

---

## Citation

If you use this knowledge graph or any part of this project, please cite it as:

```
Friese, H. (2026). KG on Dance Styles – A Knowledge Graph of Dance Genres and Styles.
GitHub. https://github.com/Hannesolo1/KG_Personal_Project
```

**Authority reference (cito:citesAsAuthority):**  
https://github.com/Hannesolo1/KG_Personal_Project/blob/main/README.md

Further references used in this project:
- [Wikidata](https://www.wikidata.org/) – linked entity data
- [Schema.org](https://schema.org/) – vocabulary for structured data
- [YouTube Data API](https://developers.google.com/youtube/v3) – video metadata and comments

