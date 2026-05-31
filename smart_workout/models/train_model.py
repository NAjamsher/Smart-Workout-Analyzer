"""
models/train_model.py
Machine Learning Model Training

Trains two models:
  1. Workout Type Classifier  → recommends workout type (classification)
  2. Calorie Predictor        → predicts calories burned (regression)
"""

import pandas as pd
import numpy as np
import os
import joblib
import logging
from datetime import datetime

from sklearn.model_selection   import train_test_split, cross_val_score
from sklearn.ensemble          import RandomForestClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing     import LabelEncoder, StandardScaler
from sklearn.pipeline          import Pipeline
from sklearn.metrics           import (
    accuracy_score, classification_report,
    mean_absolute_error, mean_squared_error, r2_score
)

# ── Logger ────────────────────────────────────────────────────────────────────
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(f'logs/training_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ── Feature Columns used for training ─────────────────────────────────────────
FEATURE_COLS = ['age', 'weight_kg', 'height_cm', 'bmi', 'gender_enc', 'experience_enc', 'goal_enc']


def load_data():
    """Load processed dataset."""
    path = 'data/processed/workout_processed.csv'
    logger.info(f"Loading data from {path}")
    df = pd.read_csv(path)
    logger.info(f"Loaded {len(df)} rows")
    return df


def encode_features(df):
    """Convert text columns into numbers for ML."""
    logger.info("Encoding categorical features...")
    
    encoders = {}
    
    # Encode: gender, experience, goal
    for col in ['gender', 'experience', 'goal', 'workout_type']:
        le = LabelEncoder()
        df[f'{col}_enc'] = le.fit_transform(df[col])
        encoders[col] = le
        logger.info(f"  Encoded '{col}': {list(le.classes_)}")
    
    return df, encoders


def train_workout_classifier(X_train, X_test, y_train, y_test):
    """
    Train a Random Forest to CLASSIFY (recommend) workout type.
    Classification = predicting a CATEGORY (Cardio, Strength, Yoga, etc.)
    """
    logger.info("\n── Training Workout Type Classifier ──────────────────")
    
    # Build pipeline: scale features → train model
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model',  RandomForestClassifier(
            n_estimators=100,    # 100 decision trees
            max_depth=10,        # Limit tree depth to prevent overfitting
            random_state=42,
            n_jobs=-1            # Use all CPU cores
        ))
    ])
    
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    logger.info(f"  Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    logger.info(f"  Report:\n{classification_report(y_test, y_pred)}")
    
    # Cross-validation (more robust evaluation)
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5)
    logger.info(f"  Cross-validation (5-fold): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    
    return pipeline, accuracy


def train_calorie_predictor(X_train, X_test, y_train, y_test):
    """
    Train a Gradient Boosting model to PREDICT calories burned.
    Regression = predicting a NUMBER (calories).
    """
    logger.info("\n── Training Calorie Predictor ────────────────────────")
    
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model',  GradientBoostingRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            random_state=42
        ))
    ])
    
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    
    # Metrics
    mae  = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2   = r2_score(y_test, y_pred)
    
    logger.info(f"  MAE  (Mean Absolute Error): {mae:.2f} calories")
    logger.info(f"  RMSE (Root Mean Sq Error):  {rmse:.2f} calories")
    logger.info(f"  R²   (Explained Variance):  {r2:.4f}")
    
    return pipeline, {'mae': mae, 'rmse': rmse, 'r2': r2}


def save_artifacts(classifier, regressor, encoders):
    """Save trained models and encoders to disk."""
    os.makedirs('models', exist_ok=True)
    
    joblib.dump(classifier, 'models/workout_classifier.pkl')
    joblib.dump(regressor,  'models/calorie_predictor.pkl')
    joblib.dump(encoders,   'models/encoders.pkl')
    
    logger.info("\n── Models Saved ──────────────────────────────────────")
    logger.info("  models/workout_classifier.pkl")
    logger.info("  models/calorie_predictor.pkl")
    logger.info("  models/encoders.pkl")


def run_training():
    """Main training function — runs the full ML pipeline."""
    logger.info("=" * 60)
    logger.info("  STARTING MODEL TRAINING")
    logger.info("=" * 60)
    
    # 1. Load data
    df = load_data()
    
    # 2. Encode categorical features
    df, encoders = encode_features(df)
    
    # 3. Prepare features (X) and targets (y)
    X = df[FEATURE_COLS]
    y_class  = df['workout_type_enc']   # for classifier
    y_regress = df['calories_burned']   # for regressor
    
    # 4. Split data (80% train, 20% test)
    X_train, X_test, yc_train, yc_test = train_test_split(
        X, y_class, test_size=0.2, random_state=42, stratify=y_class
    )
    _, _, yr_train, yr_test = train_test_split(
        X, y_regress, test_size=0.2, random_state=42
    )
    
    logger.info(f"Train size: {len(X_train)} | Test size: {len(X_test)}")
    
    # 5. Train models
    classifier,  cls_acc     = train_workout_classifier(X_train, X_test, yc_train, yc_test)
    regressor,   reg_metrics = train_calorie_predictor(X_train, X_test, yr_train, yr_test)
    
    # 6. Save everything
    save_artifacts(classifier, regressor, encoders)
    
    logger.info("\n✅ Training Complete!")
    logger.info(f"   Classifier Accuracy: {cls_acc*100:.2f}%")
    logger.info(f"   Calorie MAE: {reg_metrics['mae']:.2f} | R²: {reg_metrics['r2']:.4f}")
    
    return classifier, regressor, encoders


if __name__ == '__main__':
    run_training()
