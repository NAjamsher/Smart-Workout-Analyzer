"""
pipeline/generate_dataset.py
Generates a synthetic workout dataset for training the ML model.
This simulates real-world gym data with realistic values.
"""

import pandas as pd
import numpy as np
import os

# Set random seed so results are reproducible every time
np.random.seed(42)

def generate_workout_dataset(n_samples=2000):
    """
    Generate a synthetic dataset of user profiles and workout recommendations.
    
    Parameters:
        n_samples (int): Number of data rows to generate
    
    Returns:
        pd.DataFrame: Complete dataset
    """
    
    print(f"[INFO] Generating dataset with {n_samples} samples...")
    
    # ── User Physical Attributes ──────────────────────────────────────────────
    ages         = np.random.randint(16, 65, n_samples)
    weights_kg   = np.round(np.random.uniform(45, 130, n_samples), 1)   # kg
    heights_cm   = np.round(np.random.uniform(150, 200, n_samples), 1)  # cm
    
    # BMI calculation
    heights_m    = heights_cm / 100
    bmi          = np.round(weights_kg / (heights_m ** 2), 2)
    
    # ── Categorical Features ──────────────────────────────────────────────────
    goals        = np.random.choice(
        ['weight_loss', 'muscle_gain', 'endurance', 'flexibility', 'general_fitness'],
        n_samples,
        p=[0.30, 0.25, 0.20, 0.10, 0.15]   # Realistic distribution
    )
    
    experience   = np.random.choice(
        ['beginner', 'intermediate', 'advanced'],
        n_samples,
        p=[0.40, 0.35, 0.25]
    )
    
    genders      = np.random.choice(['male', 'female'], n_samples, p=[0.55, 0.45])
    
    # ── Workout Duration (minutes) based on experience ────────────────────────
    duration_map = {'beginner': 30, 'intermediate': 45, 'advanced': 60}
    durations    = np.array([duration_map[e] + np.random.randint(-5, 16) for e in experience])
    
    # ── Calories Burned (realistic formula based on MET values) ───────────────
    # MET (Metabolic Equivalent of Task) varies by goal and intensity
    met_map = {
        'weight_loss':     6.0,
        'muscle_gain':     5.0,
        'endurance':       7.5,
        'flexibility':     3.0,
        'general_fitness': 5.5
    }
    
    calories_burned = np.array([
        round(met_map[g] * weights_kg[i] * (durations[i] / 60) * (1 + (ages[i] - 30) * -0.005), 1)
        for i, g in enumerate(goals)
    ])
    calories_burned = np.clip(calories_burned, 80, 800)  # Realistic range
    
    # ── Workout Type Recommendation ───────────────────────────────────────────
    workout_map = {
        'weight_loss':     'Cardio + HIIT',
        'muscle_gain':     'Strength Training',
        'endurance':       'Running + Cycling',
        'flexibility':     'Yoga + Stretching',
        'general_fitness': 'Mixed Training'
    }
    workout_types = [workout_map[g] for g in goals]
    
    # ── Weekly Frequency Recommendation ──────────────────────────────────────
    freq_map = {'beginner': 3, 'intermediate': 4, 'advanced': 5}
    frequencies = [freq_map[e] + np.random.randint(0, 2) for e in experience]
    
    # ── Assemble DataFrame ────────────────────────────────────────────────────
    df = pd.DataFrame({
        'age':             ages,
        'weight_kg':       weights_kg,
        'height_cm':       heights_cm,
        'bmi':             bmi,
        'gender':          genders,
        'goal':            goals,
        'experience':      experience,
        'workout_type':    workout_types,
        'duration_min':    durations,
        'calories_burned': calories_burned,
        'weekly_frequency': frequencies
    })
    
    print(f"[SUCCESS] Dataset generated: {df.shape[0]} rows × {df.shape[1]} columns")
    return df


def save_dataset(df):
    """Save dataset to raw data folder."""
    os.makedirs('data/raw', exist_ok=True)
    path = 'data/raw/workout_data.csv'
    df.to_csv(path, index=False)
    print(f"[SAVED] Raw dataset → {path}")
    return path


if __name__ == '__main__':
    df = generate_workout_dataset()
    save_dataset(df)
    print("\nDataset Preview:")
    print(df.head())
    print("\nDataset Info:")
    print(df.describe())
