"""
Google Play Store Review Scraper
Task 1: Data Collection

This script scrapes user reviews from Google Play Store for three Ethiopian banks.
Target: 400+ reviews per bank (1200 total minimum)
"""

import sys
import os
import pathlib
import time
from datetime import datetime

# Allow flexible imports of the project config whether this script is run from repo root
# or from inside the scripts/ folder.
root = pathlib.Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# Try importing config from package-style or top-level module
try:
    from scripts.config import APP_IDS, BANK_NAMES, SCRAPING_CONFIG, DATA_PATHS, ensure_data_dirs
except Exception:
    try:
        from config import APP_IDS, BANK_NAMES, SCRAPING_CONFIG, DATA_PATHS, ensure_data_dirs
    except Exception:
        raise

from google_play_scraper import Sort, reviews, app
import pandas as pd
from tqdm import tqdm


class PlayStoreScraper:
    """Scraper class for Google Play Store reviews"""

    def __init__(self):
        # Load configuration variables from the config file
        self.app_ids = APP_IDS
        self.bank_names = BANK_NAMES
        self.reviews_per_bank = SCRAPING_CONFIG.get('reviews_per_bank', 400)
        self.lang = SCRAPING_CONFIG.get('lang', 'en')
        self.country = SCRAPING_CONFIG.get('country', 'et')
        self.max_retries = SCRAPING_CONFIG.get('max_retries', 3)
        # ensure data directories exist
        try:
            ensure_data_dirs()
        except Exception:
            os.makedirs(DATA_PATHS.get('raw', 'data/raw'), exist_ok=True)
            os.makedirs(DATA_PATHS.get('processed', 'data/processed'), exist_ok=True)

    def get_app_info(self, app_id):
        """
        Get basic information about the app (rating, total reviews, etc.)
        """
        try:
            result = app(app_id, lang=self.lang, country=self.country)
            return {
                'app_id': app_id,
                'title': result.get('title', 'N/A'),
                'score': result.get('score', 0),
                'ratings': result.get('ratings', 0),
                'reviews': result.get('reviews', 0),
                'installs': result.get('installs', 'N/A')
            }
        except Exception as e:
            print(f"Error getting app info for {app_id}: {str(e)}")
            return None

    def scrape_reviews(self, app_id, count=450):
        """
        Scrape reviews for a specific app.
        Attempts to fetch 'count' number of reviews, sorted by newest first.
        Includes a retry mechanism for stability.
        """
        if count is None:
            count = self.reviews_per_bank

        print(f"\nScraping reviews for {app_id} (target={count})...")

        for attempt in range(self.max_retries):
            try:
                result, _ = reviews(
                    app_id,
                    lang=self.lang,
                    country=self.country,
                    sort=Sort.NEWEST,
                    count=count,
                    filter_score_with=None
                )

                print(f"Successfully scraped {len(result)} reviews")
                return result

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    print("Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    print(f"Failed to scrape reviews after {self.max_retries} attempts")
                    return []

        return []

    def process_reviews(self, reviews_data, bank_code):
        """
        Process raw review data from the scraper into a clean dictionary format.
        Extracts only the relevant fields we need for analysis.
        """
        processed = []

        for review in reviews_data:
            processed.append({
                'review_id': review.get('reviewId', ''),
                'review_text': review.get('content', ''),
                'rating': review.get('score', 0),
                'review_date': review.get('at', datetime.now()),
                'bank_code': bank_code,
                'bank_name': self.bank_names.get(bank_code, bank_code),
                'source': 'Google Play'
            })

        return processed

    def scrape_all_banks(self):
        """
        Main orchestration method:
        1. Iterates through all configured banks
        2. Fetches app metadata
        3. Scrapes reviews for each bank
        4. Combines all data into a single DataFrame
        5. Saves the raw data to CSV
        """
        all_reviews = []
        app_info_list = []

        print("=" * 60)
        print("Starting Google Play Store Review Scraper")
        print("=" * 60)

        # --- Phase 1: Fetch App Info ---
        print("\n[1/2] Fetching app information...")
        for bank_code, app_id in self.app_ids.items():
            print(f"\n{bank_code}: {self.bank_names.get(bank_code, bank_code)}")
            print(f"App ID: {app_id}")

            info = self.get_app_info(app_id)
            if info:
                info['bank_code'] = bank_code
                info['bank_name'] = self.bank_names.get(bank_code, bank_code)
                app_info_list.append(info)
                print(f"Current Rating: {info['score']}")
                print(f"Total Ratings: {info['ratings']}")
                print(f"Total Reviews: {info['reviews']}")

        # Save the gathered app info to a CSV file
        if app_info_list:
            app_info_df = pd.DataFrame(app_info_list)
            os.makedirs(DATA_PATHS['raw'], exist_ok=True)
            app_info_df.to_csv(os.path.join(DATA_PATHS['raw'], "app_info.csv"), index=False)
            print(f"\nApp information saved to {os.path.join(DATA_PATHS['raw'], 'app_info.csv')}")

        # --- Phase 2: Scrape Reviews ---
        print("\n[2/2] Scraping reviews...")
        for bank_code, app_id in tqdm(self.app_ids.items(), desc="Banks"):
            reviews_data = self.scrape_reviews(app_id, self.reviews_per_bank)

            if reviews_data:
                processed = self.process_reviews(reviews_data, bank_code)
                all_reviews.extend(processed)
                print(f"Collected {len(processed)} reviews for {self.bank_names.get(bank_code, bank_code)}")
            else:
                print(f"WARNING: No reviews collected for {self.bank_names.get(bank_code, bank_code)}")

            time.sleep(SCRAPING_CONFIG.get('sleep_between_requests', 2))

        # --- Phase 3: Save Data ---
        if all_reviews:
            df = pd.DataFrame(all_reviews)

            # Save raw data to CSV
            
            os.makedirs(DATA_PATHS['raw'], exist_ok=True)
            df.to_csv(DATA_PATHS['raw_reviews'], index=False)

            print("\n" + "=" * 60)
            print("Scraping Complete!")
            print("=" * 60)
            print(f"\nTotal reviews collected: {len(df)}")

            print(f"Reviews per bank:")
            for bank_code in self.bank_names.keys():
                count = len(df[df['bank_code'] == bank_code])
                print(f"  {self.bank_names[bank_code]}: {count}")

            print(f"\nData saved to: {DATA_PATHS['raw_reviews']}")

            return df
        else:
            print("\nERROR: No reviews were collected!")
            return pd.DataFrame()

    def display_sample_reviews(self, df, n=3):
        """
        Display sample reviews from each bank to verify data quality.
        """
        print("\n" + "=" * 60)
        print("Sample Reviews")
        print("=" * 60)

        for bank_code in self.bank_names.keys():
            bank_df = df[df['bank_code'] == bank_code]
            if not bank_df.empty:
                print(f"\n{self.bank_names[bank_code]}:")
                print("-" * 60)
                samples = bank_df.head(n)
                for idx, row in samples.iterrows():
                    print(f"\nRating: {'⭐' * int(row['rating'])}")
                    print(f"Review: {str(row['review_text'])[:200]}...")
                    print(f"Date: {row['review_date']}")

def main():
    """Main execution function"""
    scraper = PlayStoreScraper()
    df = scraper.scrape_all_banks()
    if not df.empty:
        scraper.display_sample_reviews(df)
    return df

if __name__ == "__main__":
    reviews_df = main()
