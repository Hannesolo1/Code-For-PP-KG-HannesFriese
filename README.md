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

## Knowledge Graph Structure

### Classes

| Class | URI | Subclass of | Description |
|---|---|---|---|
| `DanceRecord` | `dance:DanceRecord` | `schema:CreativeWork` | Core entity – one dance style/genre |
| `DanceStyle` | `dance:DanceStyle` | `skos:Concept` | Style category of a dance |
| `DanceType` | `dance:DanceType` | `skos:Concept` | Type category of a dance |
| `DanceFormation` | `dance:DanceFormation` | `skos:Concept` | How dancers are arranged (e.g. Solo, Circle) |
| `AgeGroup` | `dance:AgeGroup` | `skos:Concept` | Target age group (e.g. Kids, Adults) |
| `LearningDifficulty` | `dance:LearningDifficulty` | `skos:Concept` | Skill level (Beginner, Intermediate, Advanced) |
| `TempoRange` | `dance:TempoRange` | `schema:Intangible` | BPM range associated with a dance |
| `TimePeriod` | `dance:TimePeriod` | `schema:Intangible` | Historical era of origin |
| `Origin` | `dance:Origin` | `schema:Place` | Geographic/cultural origin |
| `Practitioner` | `dance:Practitioner` | `schema:Person` | Famous dancer/practitioner |
| `HealthBenefit` | `dance:HealthBenefit` | `schema:MedicalEntity` | Health benefit associated with a dance |
| `MusicGenre` | `schema:MusicGenre` | – | Associated music genre |
| `MusicInstrument` | `schema:MusicInstrument` | – | Instrument used in the dance music |
| `Event` | `schema:Event` | – | Festival or event associated with the dance |
| `YouTubeVideo` | *(YouTube URL)* | `schema:VideoObject` | A linked YouTube video for the dance |

---

### Object Properties (Relations between entities)

| Property | Domain | Range | Description |
|---|---|---|---|
| `dance:hasOrigin` | `DanceRecord` | `Origin` | Geographic/cultural origin |
| `dance:hasDanceStyle` | `DanceRecord` | `DanceStyle` | Style of the dance |
| `dance:hasDanceType` | `DanceRecord` | `DanceType` | Type of the dance |
| `dance:hasDanceFormation` | `DanceRecord` | `DanceFormation` | Formation used |
| `dance:hasAgeGroup` | `DanceRecord` | `AgeGroup` | Target age group |
| `dance:hasLearningDifficulty` | `DanceRecord` | `LearningDifficulty` | Difficulty level |
| `dance:hasTempoRange` | `DanceRecord` | `TempoRange` | Tempo/BPM range |
| `dance:hasTimePeriod` | `DanceRecord` | `TimePeriod` | Historical period |
| `dance:hasFamousPractitioner` | `DanceRecord` | `Practitioner` | Notable practitioner |
| `dance:hasHealthBenefit` | `DanceRecord` | `HealthBenefit` | Health benefit |
| `dance:hasAssociatedMusicGenre` | `DanceRecord` | `MusicGenre` | Associated music genre |
| `dance:hasInstrument` | `DanceRecord` | `MusicInstrument` | Associated instrument |
| `dance:hasEventFestival` | `DanceRecord` | `Event` | Associated festival/event |
| `dance:hasYTLink` | `DanceRecord` | `YouTubeVideo` | Link to a YouTube video |

---

### Datatype Properties (Literal attributes)

**On `DanceRecord`:**

| Property | Range | Description |
|---|---|---|
| `dance:costume` | `xsd:string` | Traditional costume description |
| `dance:culturalSignificance` | `xsd:string` | Cultural significance of the dance |
| `dance:modernAdaptations` | `xsd:string` | Modern adaptations or evolutions |
| `dance:notableCharacteristics` | `xsd:string` | Key defining characteristics |
| `dance:hardnessRatio` | `xsd:decimal` | Numeric difficulty ratio |

**On `TempoRange`:**

| Property | Range | Description |
|---|---|---|
| `dance:minTempoBPM` | `xsd:integer` | Minimum tempo in BPM |
| `dance:maxTempoBPM` | `xsd:integer` | Maximum tempo in BPM |

**On `YouTubeVideo`:**

| Property | Range | Description |
|---|---|---|
| `schema:title` | `xsd:string` | Video title |
| `schema:description` | `xsd:string` | Video description |
| `schema:uploadDate` | `xsd:date` | Upload date |
| `schema:duration` | `xsd:duration` | Video duration |
| `schema:interactionCount` | `xsd:integer` | View count |
| `schema:UserLikes` | `xsd:integer` | Like count |
| `wd:Q28659447` | `xsd:string` | Sentiment of YouTube comments |

---

### Named Individuals (fixed enumeration values)

| Class | Instances |
|---|---|
| `AgeGroup` | Kids, Teens, Adults, Seniors, All ages |
| `LearningDifficulty` | Beginner, Intermediate, Advanced |
| `DanceFormation` | Solo, Partner, Line, Circle, Square, Group, Freestyle, Processional, Mixed |

---

### External Vocabularies Used

| Prefix | Namespace | Used for |
|---|---|---|
| `dance:` | `http://example.org/dance/` | All custom classes and properties |
| `schema:` | `http://schema.org/` | Person, Place, Event, MusicGenre, VideoObject, etc. |
| `wd:` | `http://www.wikidata.org/entity/` | Wikidata entity links + sentiment property |
| `skos:` | `http://www.w3.org/2004/02/skos/core#` | Concept hierarchy for enumeration classes |
| `owl:` | `http://www.w3.org/2002/07/owl#` | Class and property declarations |
| `rdfs:` | `http://www.w3.org/2000/01/rdf-schema#` | Labels, comments, subClassOf |
| `xsd:` | `http://www.w3.org/2001/XMLSchema#` | Literal datatypes |

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

