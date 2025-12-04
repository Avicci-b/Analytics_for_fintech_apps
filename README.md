# Analytics for Fintech Apps

## Project overview
This repository collects, preprocesses and analyzes Google Play reviews for several Ethiopian banking apps to produce cleaned datasets and exploratory visualizations.

## Methodology

### 1) Data collection (scraper)
- Source: Google Play Store (google_play_scraper).
- Target: ~400+ reviews per bank (3 banks).
- Collected fields: review text, rating, date, app id.
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

### 5) PostgreSQL Database Implementation (Task 3)
Implemented persistent storage for processed review data using PostgreSQL.

#### Database Setup
- **Database**: `bank_reviews`
- **User**: `bank_user`
- **Tables**: `banks` and `reviews`

#### Schema Design
```sql
-- banks table
CREATE TABLE banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL,
    app_name VARCHAR(200)
);

-- reviews table  
CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
    bank_id INTEGER REFERENCES banks(bank_id),
    review_text TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_date DATE NOT NULL,
    source VARCHAR(50) DEFAULT 'Google Play Store'
);

Data Insertion (via Python notebook notebooks/task3_postgresql.ipynb):

Connected to PostgreSQL using psycopg2

Loaded processed CSV: data/processed/reviews_processed.csv

Inserted 1,313 reviews (exceeding 400 minimum requirement)

Success rate: 97.3%

Verification Queries executed to ensure data integrity.

Results
Total Reviews Inserted: 1,313

Reviews per Bank:

Bank of Abyssinia: 441 reviews

Dashen Bank: 438 reviews

Commercial Bank of Ethiopia: 434 reviews

Data Quality: All validation checks passed

Schema Documentation: database/schema.sql

Files Created
database/schema.sql - Complete database schema

notebooks/task3_postgresql.ipynb - Database implementation notebook

data/processed/task3_summary.json - Database summary statistics

Task 3 Completion Status
✅ KPIs Met: Working database connection, >1,000 reviews inserted, schema file created
✅ Minimum Requirements Met: Database with both tables, >400 reviews inserted, schema documented

text

## **TO UPDATE YOUR README.md:**

Run this command:

```bash
# Add Task 3 section to your README.md
cat >> README.md << 'EOF'

### 5) PostgreSQL Database Implementation (Task 3)
Implemented persistent storage for processed review data using PostgreSQL.

#### Database Setup
- **Database**: `bank_reviews`
- **User**: `bank_user`
- **Tables**: `banks` and `reviews`

#### Schema Design
```sql
-- banks table
CREATE TABLE banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL,
    app_name VARCHAR(200)
);

-- reviews table  
CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
    bank_id INTEGER REFERENCES banks(bank_id),
    review_text TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_date DATE NOT NULL,
    source VARCHAR(50) DEFAULT 'Google Play Store'
);
Implementation Steps
Database Creation (via terminal):

bash
sudo -u postgres psql
CREATE DATABASE bank_reviews;
CREATE USER bank_user WITH PASSWORD 'bank123';
GRANT ALL PRIVILEGES ON DATABASE bank_reviews TO bank_user;
Data Insertion (via Python notebook notebooks/task3_postgresql.ipynb):

Connected to PostgreSQL using psycopg2

Loaded processed CSV: ../data/processed/reviews_processed.csv

Inserted 1,313 reviews (exceeding 400 minimum requirement)

Success rate: 97.3%

Verification Queries executed to ensure data integrity.

Results
Total Reviews Inserted: 1,313

Reviews per Bank:

Bank of Abyssinia: 441 reviews

Dashen Bank: 438 reviews

Commercial Bank of Ethiopia: 434 reviews

Data Quality: All validation checks passed

Schema Documentation: database/schema.sql

Files Created
database/schema.sql - Complete database schema

notebooks/task3_postgresql.ipynb - Database implementation notebook

data/processed/task3_summary.json - Database summary statistics

Task 3 Completion Status
✅ KPIs Met: Working database connection, >1,000 reviews inserted, schema file created
✅ Minimum Requirements Met: Database with both tables, >400 reviews inserted, schema documented

### 6) Task 4: Insights and Recommendations
Derived actionable insights from analysis of 1,313 bank app reviews.

Key Insights
- **Drivers of Satisfaction**: Identified 2+ positive aspects per bank
- **Pain Points**: Discovered 2+ issues per bank requiring attention  
- **Bank Comparisons**: Comparative analysis of CBE vs BOA vs Dashen

Visualizations Created
1. Rating Distribution by Bank
2. Sentiment Analysis Comparison
3. Word Clouds for Positive/Negative Reviews
4. Performance Metrics Dashboard

 Recommendations
Provided 2+ actionable recommendations per bank for app improvement.

 Ethical Considerations
Noted potential biases in review data and limitations of analysis.

 Files Created
- `notebooks/task4_insights_analysis.ipynb` - Complete analysis notebook
- `reports/task4_final_report.md` - 10-page final report
- Visualizations saved in notebook outputs

 Task 4 Completion Status
✅ KPIs Met: 2+ drivers/pain points per bank, clear visualizations, practical recommendations  
✅ Minimum Requirements Met: 1 driver & pain point per bank, 2+ plots, 10-page report