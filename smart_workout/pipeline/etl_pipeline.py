"""
pipeline/etl_pipeline.py
ETL (Extract → Transform → Load) Pipeline

This is a core Data Engineering component.
It reads raw data, cleans it, validates it, and saves processed data ready for ML.
"""

import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime

# ── Setup Logger ──────────────────────────────────────────────────────────────
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(f'logs/etl_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()   # Also print to console
    ]
)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — EXTRACT
# ══════════════════════════════════════════════════════════════════════════════
def extract(filepath='data/raw/workout_data.csv'):
    """Read raw data from CSV file."""
    logger.info(f"[EXTRACT] Reading raw data from: {filepath}")
    
    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        raise FileNotFoundError(f"Raw data not found at {filepath}")
    
    df = pd.read_csv(filepath)
    logger.info(f"[EXTRACT] Loaded {df.shape[0]} rows and {df.shape[1]} columns")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — VALIDATE
# ══════════════════════════════════════════════════════════════════════════════
def validate(df):
    """Check data quality and log issues."""
    logger.info("[VALIDATE] Running data validation checks...")
    
    issues = []
    
    # Check for missing values
    null_counts = df.isnull().sum()
    if null_counts.any():
        issues.append(f"Missing values found: {null_counts[null_counts > 0].to_dict()}")
    
    # Check for valid age range
    invalid_ages = df[(df['age'] < 10) | (df['age'] > 100)]
    if len(invalid_ages) > 0:
        issues.append(f"{len(invalid_ages)} rows with invalid age values")
    
    # Check for valid weight range
    invalid_weight = df[(df['weight_kg'] < 20) | (df['weight_kg'] > 300)]
    if len(invalid_weight) > 0:
        issues.append(f"{len(invalid_weight)} rows with invalid weight values")
    
    # Check for valid BMI range
    invalid_bmi = df[(df['bmi'] < 10) | (df['bmi'] > 60)]
    if len(invalid_bmi) > 0:
        issues.append(f"{len(invalid_bmi)} rows with invalid BMI values")
    
    # Check required columns exist
    required_cols = ['age', 'weight_kg', 'height_cm', 'bmi', 'gender',
                     'goal', 'experience', 'workout_type', 'calories_burned']
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        issues.append(f"Missing columns: {missing_cols}")
    
    if issues:
        for issue in issues:
            logger.warning(f"[VALIDATE] ⚠️  {issue}")
    else:
        logger.info("[VALIDATE] ✅ All validation checks passed!")
    
    return df, issues


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — TRANSFORM
# ══════════════════════════════════════════════════════════════════════════════
def transform(df):
    """Clean and enrich the data."""
    logger.info("[TRANSFORM] Cleaning and transforming data...")
    
    # ── Drop duplicate rows ───────────────────────────────────────────────────
    before = len(df)
    df = df.drop_duplicates()
    logger.info(f"[TRANSFORM] Removed {before - len(df)} duplicate rows")
    
    # ── Handle missing values ─────────────────────────────────────────────────
    df['age'].fillna(df['age'].median(), inplace=True)
    df['weight_kg'].fillna(df['weight_kg'].median(), inplace=True)
    df['height_cm'].fillna(df['height_cm'].median(), inplace=True)
    df['calories_burned'].fillna(df['calories_burned'].mean(), inplace=True)
    
    # ── Add derived features ──────────────────────────────────────────────────
    # BMI Category
    def bmi_category(bmi):
        if bmi < 18.5:   return 'Underweight'
        elif bmi < 25:   return 'Normal'
        elif bmi < 30:   return 'Overweight'
        else:            return 'Obese'
    
    df['bmi_category']     = df['bmi'].apply(bmi_category)
    
    # Age Group
    def age_group(age):
        if age < 25:     return 'Young'
        elif age < 40:   return 'Adult'
        elif age < 55:   return 'Middle-aged'
        else:            return 'Senior'
    
    df['age_group']        = df['age'].apply(age_group)
    
    # Fitness Score (composite metric)
    exp_score = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
    df['fitness_score']    = df['experience'].map(exp_score) * 33 + \
                             np.clip((df['calories_burned'] / 10), 0, 33) + \
                             np.clip((df['duration_min'] / 2), 0, 34)
    df['fitness_score']    = df['fitness_score'].round(1)
    
    # Save cleaned version
    os.makedirs('data/cleaned', exist_ok=True)
    df.to_csv('data/cleaned/workout_cleaned.csv', index=False)
    logger.info("[TRANSFORM] Saved cleaned data → data/cleaned/workout_cleaned.csv")
    
    return df


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — LOAD
# ══════════════════════════════════════════════════════════════════════════════
def load(df):
    """Save final processed dataset for ML model training."""
    logger.info("[LOAD] Saving processed data...")
    
    os.makedirs('data/processed', exist_ok=True)
    
    # Save processed data
    df.to_csv('data/processed/workout_processed.csv', index=False)
    
    # Save summary statistics
    stats = df.describe()
    stats.to_csv('data/processed/data_summary.csv')
    
    logger.info(f"[LOAD] ✅ Processed data saved → data/processed/workout_processed.csv")
    logger.info(f"[LOAD] Final dataset: {df.shape[0]} rows × {df.shape[1]} columns")
    
    return df


# ══════════════════════════════════════════════════════════════════════════════
# RUN FULL PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
def run_etl_pipeline():
    """Execute the full ETL pipeline."""
    logger.info("=" * 60)
    logger.info("  STARTING ETL PIPELINE")
    logger.info("=" * 60)
    
    start_time = datetime.now()
    
    # Run each stage
    raw_df        = extract()
    validated_df, issues = validate(raw_df)
    transformed_df = transform(validated_df)
    final_df      = load(transformed_df)
    
    elapsed = (datetime.now() - start_time).seconds
    logger.info(f"[PIPELINE] ✅ ETL completed in {elapsed} seconds")
    logger.info("=" * 60)
    
    return final_df


if __name__ == '__main__':
    df = run_etl_pipeline()
    print("\n✅ ETL Pipeline Complete!")
    print(f"Shape: {df.shape}")
    print(df.head(3))
