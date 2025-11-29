"""
Data Preprocessing Script
Task 1: Data Preprocessing

This updated script is aligned to the project config (CBE, BOA, Dashen).
It expects the raw CSV produced by scripts/Scraper.py and produces a cleaned
CSV with a stable set of columns for downstream analysis.
"""
import sys
import os
import re
from datetime import datetime
import pandas as pd
import numpy as np


# Ensure project root is on sys.path (so package imports resolve)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.config import DATA_PATHS, BANK_NAMES, APP_IDS  # config created earlier
# ...existing code...


class ReviewPreprocessor:
    """Preprocessor class for review data (CBE, BOA, Dashen)"""

    def __init__(self, input_path=None, output_path=None):
        self.input_path = input_path or DATA_PATHS.get('raw_reviews', 'data/raw/reviews_raw.csv')
        self.output_path = output_path or DATA_PATHS.get('processed_reviews', 'data/processed/reviews_processed.csv')
        self.df = None
        self.stats = {}

        # canonical bank codes we care about (from config)
        self.allowed_bank_codes = set(APP_IDS.keys()) if APP_IDS else set(BANK_NAMES.keys())

    def load_data(self):
        print("Loading raw data...")
        try:
            self.df = pd.read_csv(self.input_path)
            print(f"Loaded {len(self.df)} reviews from {self.input_path}")
            self.stats['original_count'] = len(self.df)
            return True
        except FileNotFoundError:
            print(f"ERROR: File not found: {self.input_path}")
            return False
        except Exception as e:
            print(f"ERROR: Failed to load data: {e}")
            return False

    def check_missing_data(self):
        print("\n[1/6] Checking for missing data...")
        missing = self.df.isnull().sum()
        missing_pct = (missing / len(self.df)) * 100
        for col in missing.index:
            if missing[col] > 0:
                print(f"  {col}: {missing[col]} ({missing_pct[col]:.2f}%)")
        self.stats['missing_before'] = missing.to_dict()

        critical_cols = ['review_text', 'rating', 'bank_code']
        missing_critical = self.df[critical_cols].isnull().sum() if set(critical_cols).issubset(self.df.columns) else None
        if missing_critical is not None and missing_critical.sum() > 0:
            print("\nWARNING: Missing values in critical columns:")
            print(missing_critical[missing_critical > 0])

    def handle_missing_values(self):
        print("\n[2/6] Handling missing values...")
        # Ensure bank_code exists; if only bank_name present, try to map back to code
        if 'bank_code' not in self.df.columns and 'bank_name' in self.df.columns:
            inverse = {v: k for k, v in BANK_NAMES.items()}
            self.df['bank_code'] = self.df['bank_name'].map(inverse).fillna(self.df.get('bank_code', np.nan))

        critical_cols = [c for c in ['review_text', 'rating', 'bank_code'] if c in self.df.columns]
        before_count = len(self.df)
        if critical_cols:
            self.df = self.df.dropna(subset=critical_cols)
        removed = before_count - len(self.df)
        if removed > 0:
            print(f"Removed {removed} rows with missing critical values")
        # Fill optional columns
        if 'user_name' in self.df.columns:
            self.df['user_name'] = self.df['user_name'].fillna('Anonymous')
        else:
            self.df['user_name'] = 'Anonymous'
        if 'thumbs_up' in self.df.columns:
            self.df['thumbs_up'] = self.df['thumbs_up'].fillna(0)
        else:
            self.df['thumbs_up'] = 0
        if 'reply_content' in self.df.columns:
            self.df['reply_content'] = self.df['reply_content'].fillna('')
        else:
            self.df['reply_content'] = ''
        self.stats['rows_removed_missing'] = removed
        self.stats['count_after_missing'] = len(self.df)

    def normalize_dates(self):
        print("\n[3/6] Normalizing dates...")
        if 'review_date' not in self.df.columns:
            # nothing to do
            print("No review_date column found; skipping normalization")
            return
        try:
            self.df['review_date'] = pd.to_datetime(self.df['review_date'], errors='coerce')
            self.df = self.df.dropna(subset=['review_date'])
            self.df['review_date'] = self.df['review_date'].dt.date
            self.df['review_year'] = pd.to_datetime(self.df['review_date']).dt.year
            self.df['review_month'] = pd.to_datetime(self.df['review_date']).dt.month
            print(f"Date range: {self.df['review_date'].min()} to {self.df['review_date'].max()}")
        except Exception as e:
            print(f"WARNING: Error normalizing dates: {e}")

    def clean_text(self):
        print("\n[4/6] Cleaning text...")
        def clean_review_text(text):
            if pd.isna(text) or text == '':
                return ''
            s = str(text)
            s = re.sub(r'\s+', ' ', s).strip()
            return s
        self.df['review_text'] = self.df['review_text'].apply(clean_review_text)
        before_count = len(self.df)
        self.df = self.df[self.df['review_text'].str.len() > 0]
        removed = before_count - len(self.df)
        if removed > 0:
            print(f"Removed {removed} reviews with empty text")
        self.df['text_length'] = self.df['review_text'].str.len()
        self.stats['empty_reviews_removed'] = removed
        self.stats['count_after_cleaning'] = len(self.df)

    def validate_ratings(self):
        print("\n[5/6] Validating ratings...")
        if 'rating' not in self.df.columns:
            print("No rating column; skipping validation")
            return
        # coerce to numeric and enforce 1-5
        self.df['rating'] = pd.to_numeric(self.df['rating'], errors='coerce').fillna(0).astype(int)
        invalid = self.df[(self.df['rating'] < 1) | (self.df['rating'] > 5)]
        if len(invalid) > 0:
            print(f"WARNING: Found {len(invalid)} reviews with invalid ratings; removing")
            self.df = self.df[(self.df['rating'] >= 1) & (self.df['rating'] <= 5)]
        else:
            print("All ratings are valid (1-5)")
        self.stats['invalid_ratings_removed'] = len(invalid)

    def prepare_final_output(self):
        print("\n[6/6] Preparing final output...")
        # Desired minimal 7 columns (ensure exist)
        desired = ['review_id', 'review_text', 'rating', 'review_date', 'bank_code', 'bank_name', 'source']
        # Add optional useful columns if present
        extras = [c for c in ['user_name', 'thumbs_up', 'text_length', 'review_year', 'review_month'] if c in self.df.columns]
        output_columns = [c for c in desired + extras if c in self.df.columns]
        # If bank_name missing, derive from bank_code
        if 'bank_name' not in self.df.columns and 'bank_code' in self.df.columns:
            self.df['bank_name'] = self.df['bank_code'].map(BANK_NAMES).fillna(self.df['bank_code'])
            if 'bank_name' not in output_columns:
                output_columns.insert(6, 'bank_name')
        # Keep only allowed banks (CBE, BOA, Dashen)
        if 'bank_code' in self.df.columns:
            self.df = self.df[self.df['bank_code'].isin(self.allowed_bank_codes)]
        # Ensure columns exist, fill missing with nulls
        for col in output_columns:
            if col not in self.df.columns:
                self.df[col] = None
        self.df = self.df.loc[:, output_columns]
        # Sort and reset index
        sort_cols = [c for c in ['bank_code', 'review_date'] if c in self.df.columns]
        if sort_cols:
            self.df = self.df.sort_values(sort_cols, ascending=[True, False] if sort_cols == ['bank_code','review_date'] else True)
        self.df = self.df.reset_index(drop=True)
        print(f"Final dataset: {len(self.df)} reviews")

    def save_data(self):
        print("\nSaving processed data...")
        try:
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            self.df.to_csv(self.output_path, index=False)
            print(f"Data saved to: {self.output_path}")
            self.stats['final_count'] = len(self.df)
            return True
        except Exception as e:
            print(f"ERROR: Failed to save data: {e}")
            return False

    def generate_report(self):
        print("\n" + "=" * 60)
        print("PREPROCESSING REPORT")
        print("=" * 60)
        print(f"Original records: {self.stats.get('original_count', 0)}")
        print(f"Records with missing critical data: {self.stats.get('rows_removed_missing', 0)}")
        print(f"Empty reviews removed: {self.stats.get('empty_reviews_removed', 0)}")
        print(f"Invalid ratings removed: {self.stats.get('invalid_ratings_removed', 0)}")
        print(f"Final records: {self.stats.get('final_count', 0)}")
        if self.stats.get('original_count', 0) > 0:
            retention_rate = (self.stats.get('final_count', 0) / self.stats.get('original_count', 1)) * 100
            error_rate = 100 - retention_rate
            print(f"\nData retention rate: {retention_rate:.2f}%")
            print(f"Data error rate: {error_rate:.2f}%")
        if self.df is not None and 'bank_name' in self.df.columns:
            print("\nReviews per bank:")
            for bank, count in self.df['bank_name'].value_counts().items():
                print(f"  {bank}: {count}")
        if self.df is not None and 'rating' in self.df.columns:
            print("\nRating distribution:")
            for rating, count in self.df['rating'].value_counts().sort_index(ascending=False).items():
                pct = (count / len(self.df)) * 100
                print(f"  {'⭐' * int(rating)}: {count} ({pct:.1f}%)")
        if self.df is not None and 'text_length' in self.df.columns:
            print(f"\nText statistics: avg={self.df['text_length'].mean():.0f}, median={self.df['text_length'].median():.0f}")

    def process(self):
        print("=" * 60)
        print("STARTING DATA PREPROCESSING")
        print("=" * 60)
        if not self.load_data():
            return False
        self.check_missing_data()
        self.handle_missing_values()
        self.normalize_dates()
        self.clean_text()
        self.validate_ratings()
        self.prepare_final_output()
        if self.save_data():
            self.generate_report()
            return True
        return False


def main():
    preprocessor = ReviewPreprocessor()
    success = preprocessor.process()
    if success:
        print("\n✓ Preprocessing completed successfully!")
        return preprocessor.df
    else:
        print("\n✗ Preprocessing failed!")
        return None


if __name__ == "__main__":
    processed_df = main()
