"""
run_pipeline.py
Master script — Run this ONCE before starting the app.

What it does:
  Step 1: Generate synthetic dataset (2000 user profiles)
  Step 2: Run ETL pipeline (Extract → Transform → Load)
  Step 3: Train ML models (Classifier + Regressor)
  Step 4: Save models to disk

After running this, start the app with: python app.py
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 60)
    print("  SMART WORKOUT ANALYTICS — SETUP PIPELINE")
    print("=" * 60)
    print()
    
    # ── Step 1: Generate Dataset ─────────────────────────────────────────────
    print("📊 STEP 1: Generating Dataset...")
    from pipeline.generate_dataset import generate_workout_dataset, save_dataset
    df = generate_workout_dataset()
    save_dataset(df)
    print("✅ Dataset generated!\n")
    
    # ── Step 2: Run ETL Pipeline ─────────────────────────────────────────────
    print("🔄 STEP 2: Running ETL Pipeline...")
    from pipeline.etl_pipeline import run_etl_pipeline
    processed_df = run_etl_pipeline()
    print("✅ ETL Pipeline complete!\n")
    
    # ── Step 3: Train ML Models ──────────────────────────────────────────────
    print("🤖 STEP 3: Training Machine Learning Models...")
    from models.train_model import run_training
    run_training()
    print("✅ Models trained and saved!\n")
    
    # ── Done ─────────────────────────────────────────────────────────────────
    print("=" * 60)
    print("  ✅ ALL SETUP COMPLETE!")
    print()
    print("  ▶ Start the web app with:")
    print("       python app.py")
    print()
    print("  ▶ Then open your browser at:")
    print("       http://127.0.0.1:5000")
    print("=" * 60)


if __name__ == '__main__':
    main()
