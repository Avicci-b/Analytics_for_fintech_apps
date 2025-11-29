# Analytics for Fintech Apps

## Project overview
This repository collects, preprocesses and analyzes Google Play reviews for several Ethiopian banking apps to produce cleaned datasets and exploratory visualizations.

## Methodology

### 1) Data collection (scraper)
- Source: Google Play Store (google_play_scraper).
- Target: ~400+ reviews per bank (3 banks).
- Collected fields: review text, rating, date, user name/id, app id, version, thumbs up count, and metadata.
- Scraper implementation: `scripts/scraper.py` — exposes `main()` that returns a DataFrame and writes raw CSV(s) using canonical DATA_PATHS.

### 2) Storage conventions
- Canonical data folders at repository root:
  - `data/raw/` — raw CSV exports from scrapers
  - `data/processed/` — cleaned datasets used for modeling/visualization
- Notebook runs should resolve paths relative to the repository root to avoid creating `notebooks/data/`.

### 3) Preprocessing pipeline
Implemented in `scripts/preprocessing.py` (class `ReviewPreprocessor`):
- Load raw CSV(s) from DATA_PATHS
- Remove duplicates and malformed rows
- Normalize dates and validate ratings
- Map app IDs to bank codes/names
- Clean text (strip, lower, basic punctuation handling). Language filtering optional.
- Add derived features (e.g., `text_length`, rating buckets)
- Save cleaned output to `data/processed/`

### 4) Exploratory analysis & visualization
- Notebook: `notebooks/pre_processing_eda.ipynb`
- Visuals include rating distributions, reviews per bank, and review length histograms.
- Notebook config cell adds repo root to `sys.path` so `scripts` modules import reliably.
