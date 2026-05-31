"""
utils/predictor.py
Handles predictions using trained ML models.
Called by Flask routes to get recommendations.
"""

import joblib
import numpy as np
import os

# Map encoded indices back to readable workout names
WORKOUT_LABELS = {
    0: 'Cardio + HIIT',
    1: 'Mixed Training',
    2: 'Running + Cycling',
    3: 'Strength Training',
    4: 'Yoga + Stretching'
}

# Workout details for each type
WORKOUT_DETAILS = {
    'Cardio + HIIT': {
        'exercises': ['Jumping Jacks (3×30)', 'Burpees (3×15)', 'Mountain Climbers (3×20)',
                      'High Knees (3×30)', 'Box Jumps (3×12)', 'Sprint Intervals (8×30sec)'],
        'rest': '60 seconds between sets',
        'icon': '🏃'
    },
    'Strength Training': {
        'exercises': ['Bench Press (4×8)', 'Squats (4×10)', 'Deadlift (3×6)',
                      'Pull-ups (3×8)', 'Shoulder Press (3×10)', 'Barbell Rows (3×10)'],
        'rest': '90–120 seconds between sets',
        'icon': '💪'
    },
    'Running + Cycling': {
        'exercises': ['Warm-up jog (5 min)', 'Steady run (20 min)', 'Interval sprints (5×2 min)',
                      'Cycling (15 min)', 'Cool-down walk (5 min)'],
        'rest': 'Minimal — keep heart rate elevated',
        'icon': '🚴'
    },
    'Yoga + Stretching': {
        'exercises': ['Sun Salutation (5 rounds)', 'Warrior I & II (hold 30sec each)',
                      'Downward Dog (hold 45sec)', 'Child\'s Pose (hold 1min)',
                      'Pigeon Pose (hold 1min)', 'Savasana (5 min)'],
        'rest': 'Breathe through each pose',
        'icon': '🧘'
    },
    'Mixed Training': {
        'exercises': ['Warm-up cardio (5 min)', 'Push-ups (3×15)', 'Dumbbell Squats (3×12)',
                      'Resistance Band Rows (3×12)', 'Plank (3×45sec)', 'Stretching (10 min)'],
        'rest': '60 seconds between sets',
        'icon': '⚡'
    }
}

def load_models():
    """Load trained models from disk."""
    try:
        classifier = joblib.load('models/workout_classifier.pkl')
        regressor  = joblib.load('models/calorie_predictor.pkl')
        encoders   = joblib.load('models/encoders.pkl')
        return classifier, regressor, encoders
    except FileNotFoundError:
        raise FileNotFoundError(
            "Models not found! Run 'python run_pipeline.py' first to train the models."
        )

def predict(age, weight_kg, height_cm, goal, experience, gender='male'):
    """
    Make workout recommendation and calorie prediction.
    
    Returns a dict with:
        - workout_type: recommended workout category
        - calories: predicted calories burned
        - details: exercises, rest times, etc.
        - bmi: calculated BMI
        - fitness_score: composite score
    """
    classifier, regressor, encoders = load_models()
    
    # Calculate BMI
    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m ** 2), 2)
    
    # Encode inputs using the same encoders used during training
    gender_enc     = encoders['gender'].transform([gender])[0]
    experience_enc = encoders['experience'].transform([experience])[0]
    goal_enc       = encoders['goal'].transform([goal])[0]
    
    # Build feature vector (must match training order!)
    features = np.array([[age, weight_kg, height_cm, bmi, gender_enc, experience_enc, goal_enc]])
    
    # Predict
    workout_enc = classifier.predict(features)[0]
    calories    = round(regressor.predict(features)[0], 1)
    
    # Decode workout type
    workout_type = encoders['workout_type'].inverse_transform([workout_enc])[0]
    details      = WORKOUT_DETAILS.get(workout_type, {})
    
    # Fitness score
    exp_scores = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
    fitness_score = round(exp_scores[experience] * 33 + min(calories / 10, 33), 1)
    
    return {
        'workout_type':  workout_type,
        'calories':      max(50, calories),   # Minimum 50 calories
        'exercises':     details.get('exercises', []),
        'rest':          details.get('rest', '60 seconds'),
        'icon':          details.get('icon', '💪'),
        'bmi':           bmi,
        'fitness_score': fitness_score,
        'goal':          goal.replace('_', ' ').title(),
        'experience':    experience.title()
    }
