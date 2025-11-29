# ...existing code...
"""
Configuration file for Bank Reviews Analysis Project
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Play Store App IDs (defaults are placeholders; override via env vars)
APP_IDS = {
    'CBE': os.getenv('CBE_APP_ID', 'com.combanketh.mobilebanking'),
    'BOA': os.getenv('BOA_APP_ID', 'com.boa.boaMobileBanking'),
    'Dashen': os.getenv('DASHEN_APP_ID', 'com.dashen.dashensuperapp'),
}

# Human-readable bank names
BANK_NAMES = {
    'CBE': 'Commercial Bank of Ethiopia',
    'BOA': 'Bank of Abyssinia',
    'Dashen': 'Dashen Bank'
}

# Scraping Configuration
SCRAPING_CONFIG = {
    'reviews_per_bank': int(os.getenv('REVIEWS_PER_BANK', 450)),
    'max_retries': int(os.getenv('MAX_RETRIES', 3)),
    'lang': os.getenv('REVIEW_LANG', 'en'),
    'country': os.getenv('REVIEW_COUNTRY', 'et')  # Ethiopia
}

# File Paths
DATA_PATHS = {
    'raw': os.path.join(os.getenv('DATA_DIR', 'data'), 'raw'),
    'processed': os.path.join(os.getenv('DATA_DIR', 'data'), 'processed'),
    'raw_reviews': os.path.join(os.getenv('DATA_DIR', 'data'), 'raw', 'reviews_raw.csv'),
    'processed_reviews': os.path.join(os.getenv('DATA_DIR', 'data'), 'processed', 'reviews_processed.csv'),
    'sentiment_results': os.path.join(os.getenv('DATA_DIR', 'data'), 'processed', 'reviews_with_sentiment.csv'),
    'final_results': os.path.join(os.getenv('DATA_DIR', 'data'), 'processed', 'reviews_final.csv')
}

# Play Store URL template (useful for validation or manual checks)
PLAY_STORE_URL = "https://play.google.com/store/apps/details?id={app_id}&hl={lang}&gl={country}"

# Ensure data directories exist at runtime
def ensure_data_dirs():
    for p in (DATA_PATHS['raw'], DATA_PATHS['processed']):
        os.makedirs(p, exist_ok=True)

# Notes
NOTES = (
    "Verify the default APP_IDS above. Real Google Play package names can be set via "
    "environment variables: CBE_APP_ID, BOA_APP_ID, DASHEN_APP_ID."
)
