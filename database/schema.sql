-- database/schema.sql
-- Task 3: PostgreSQL Database Schema for Bank Reviews Analytics
-- Project: Analytics for Fintech Apps - KAIM Academy
-- Created for: Commercial Bank of Ethiopia, Bank of Abyssinia, Dashen Bank

-- ============================================
-- DATABASE: bank_reviews
-- USER: bank_user
-- ============================================

-- ============================================
-- BANKS TABLE
-- Stores information about each banking app
-- ============================================
CREATE TABLE IF NOT EXISTS banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL,
    app_name VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE banks IS 'Stores bank information for CBE, BOA, and Dashen Bank';
COMMENT ON COLUMN banks.bank_id IS 'Unique identifier for each bank';
COMMENT ON COLUMN banks.bank_name IS 'Full name of the bank';
COMMENT ON COLUMN banks.app_name IS 'Name of the mobile banking application';
COMMENT ON COLUMN banks.created_at IS 'Timestamp when the record was created';

-- ============================================
-- REVIEWS TABLE  
-- Stores user reviews from Google Play Store
-- ============================================
CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    bank_id INTEGER NOT NULL REFERENCES banks(bank_id),
    review_text TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_date DATE NOT NULL,
    sentiment_label VARCHAR(20),
    sentiment_score DECIMAL(5,4),
    source VARCHAR(50) DEFAULT 'Google Play Store',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE reviews IS 'Stores user reviews from Google Play Store with sentiment analysis';
COMMENT ON COLUMN reviews.review_id IS 'Unique identifier for each review';
COMMENT ON COLUMN reviews.bank_id IS 'Foreign key referencing banks table';
COMMENT ON COLUMN reviews.review_text IS 'Full text of the user review';
COMMENT ON COLUMN reviews.rating IS 'Star rating (1-5 stars)';
COMMENT ON COLUMN reviews.review_date IS 'Date when the review was posted';
COMMENT ON COLUMN reviews.sentiment_label IS 'Sentiment classification (POSITIVE/NEGATIVE/NEUTRAL)';
COMMENT ON COLUMN reviews.sentiment_score IS 'Sentiment confidence score (0-1)';
COMMENT ON COLUMN reviews.source IS 'Source of the review (default: Google Play Store)';
COMMENT ON COLUMN reviews.created_at IS 'Timestamp when the record was inserted into database';

-- ============================================
-- INDEXES for Performance Optimization
-- ============================================
CREATE INDEX IF NOT EXISTS idx_reviews_bank_id ON reviews(bank_id);
CREATE INDEX IF NOT EXISTS idx_reviews_date ON reviews(review_date);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_sentiment ON reviews(sentiment_score);

COMMENT ON INDEX idx_reviews_bank_id IS 'Speeds up queries filtering by bank_id';
COMMENT ON INDEX idx_reviews_date IS 'Speeds up date-based queries and trend analysis';
COMMENT ON INDEX idx_reviews_rating IS 'Optimizes rating-based filtering and aggregation';
COMMENT ON INDEX idx_reviews_sentiment IS 'Improves sentiment analysis queries';

-- ============================================
-- SAMPLE DATA: Banks
-- Pre-populated with the three Ethiopian banks
-- ============================================
INSERT INTO banks (bank_name, app_name) VALUES
('Commercial Bank of Ethiopia', 'CBE Mobile Banking'),
('Bank of Abyssinia', 'BOA Mobile Banking'),
('Dashen Bank', 'Dashen Mobile Banking')
ON CONFLICT DO NOTHING;

-- ============================================
-- VERIFICATION QUERIES
-- Use these to verify the database setup
-- ============================================

/*
-- Query 1: Verify tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Query 2: Check bank data
SELECT bank_id, bank_name, app_name 
FROM banks 
ORDER BY bank_id;

-- Query 3: Count reviews (after insertion)
SELECT COUNT(*) as total_reviews FROM reviews;

-- Query 4: Reviews per bank
SELECT b.bank_name, COUNT(r.review_id) as review_count
FROM banks b
LEFT JOIN reviews r ON b.bank_id = r.bank_id
GROUP BY b.bank_name
ORDER BY review_count DESC;
*/

-- ============================================
-- SCHEMA VERSION: 1.0
-- Created: December 2024
-- Purpose: Task 3 submission for KAIM Academy
-- ============================================
