"""
app.py
Main Flask Application — Smart Workout & Progress Analytics System

Routes:
    /               → Home page
    /analyzer       → ML Workout Recommender
    /tracker        → Add/View/Delete workouts
    /dashboard      → Analytics charts
    /diet           → Diet & nutrition suggestions
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import logging
from datetime import datetime

# Import our custom modules
from utils.predictor import predict
from utils.database  import add_workout, get_all_workouts, delete_workout, get_summary_stats
from utils.diet      import get_diet_plan
from utils.analytics import calories_chart, workout_frequency_chart, duration_chart, weekly_progress_chart

# ── App Setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'smartworkout_secret_2024'   # Required for flash messages

# ── Logger ────────────────────────────────────────────────────────────────────
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename=f'logs/app_{datetime.now().strftime("%Y%m%d")}.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/')
def home():
    stats = get_summary_stats()
    logger.info("Home page visited")
    return render_template('home.html', stats=stats)


# ══════════════════════════════════════════════════════════════════════════════
# WORKOUT ANALYZER (ML Predictions)
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/analyzer', methods=['GET', 'POST'])
def analyzer():
    result = None
    error  = None
    
    if request.method == 'POST':
        try:
            # Collect form data
            age        = int(request.form['age'])
            weight     = float(request.form['weight'])
            height     = float(request.form['height'])
            goal       = request.form['goal']
            experience = request.form['experience']
            gender     = request.form.get('gender', 'male')
            
            # Validate inputs
            if not (10 <= age <= 100):
                raise ValueError("Age must be between 10 and 100")
            if not (30 <= weight <= 300):
                raise ValueError("Weight must be between 30 and 300 kg")
            if not (100 <= height <= 250):
                raise ValueError("Height must be between 100 and 250 cm")
            
            # Run ML prediction
            result = predict(age, weight, height, goal, experience, gender)
            logger.info(f"Prediction: age={age}, goal={goal}, exp={experience} → {result['workout_type']}")
            
        except FileNotFoundError as e:
            error = str(e)
            logger.error(f"Model not found: {e}")
        except ValueError as e:
            error = str(e)
            logger.warning(f"Validation error: {e}")
        except Exception as e:
            error = f"Prediction failed: {str(e)}"
            logger.error(f"Prediction error: {e}")
    
    return render_template('analyzer.html', result=result, error=error)


# ══════════════════════════════════════════════════════════════════════════════
# WORKOUT TRACKER
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    if request.method == 'POST':
        try:
            date         = request.form['date']
            workout_type = request.form['workout_type']
            duration     = int(request.form['duration'])
            calories     = float(request.form['calories'])
            notes        = request.form.get('notes', '')
            
            add_workout(date, workout_type, duration, calories, notes)
            flash('✅ Workout added successfully!', 'success')
            logger.info(f"Workout added: {workout_type} on {date}")
            
        except Exception as e:
            flash(f'❌ Error adding workout: {str(e)}', 'error')
            logger.error(f"Error adding workout: {e}")
        
        return redirect(url_for('tracker'))
    
    workouts = get_all_workouts()
    return render_template('tracker.html', workouts=workouts)


@app.route('/delete_workout/<int:workout_id>', methods=['POST'])
def delete_workout_route(workout_id):
    """Delete a workout by ID."""
    try:
        delete_workout(workout_id)
        flash('🗑️ Workout deleted!', 'success')
        logger.info(f"Workout deleted: ID={workout_id}")
    except Exception as e:
        flash(f'❌ Error deleting: {str(e)}', 'error')
    return redirect(url_for('tracker'))


# ══════════════════════════════════════════════════════════════════════════════
# ANALYTICS DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/dashboard')
def dashboard():
    workouts = get_all_workouts()
    stats    = get_summary_stats()
    
    # Generate charts
    charts = {
        'calories':   calories_chart(workouts),
        'frequency':  workout_frequency_chart(workouts),
        'duration':   duration_chart(workouts),
        'weekly':     weekly_progress_chart(workouts)
    }
    
    # Workout tips based on activity
    tips = get_smart_tips(stats)
    
    logger.info(f"Dashboard loaded: {len(workouts)} workouts")
    return render_template('dashboard.html', charts=charts, stats=stats, tips=tips)


# ══════════════════════════════════════════════════════════════════════════════
# DIET SUGGESTIONS
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/diet', methods=['GET', 'POST'])
def diet():
    result = None
    
    if request.method == 'POST':
        try:
            age       = int(request.form['age'])
            weight    = float(request.form['weight'])
            height    = float(request.form['height'])
            goal      = request.form['goal']
            gender    = request.form.get('gender', 'male')
            
            result    = get_diet_plan(age, weight, height, goal, gender)
            logger.info(f"Diet plan generated: goal={goal}")
            
        except Exception as e:
            flash(f'❌ Error: {str(e)}', 'error')
    
    return render_template('diet.html', result=result)


# ══════════════════════════════════════════════════════════════════════════════
# SMART TIPS HELPER
# ══════════════════════════════════════════════════════════════════════════════
def get_smart_tips(stats):
    tips = []
    
    if stats['total_workouts'] == 0:
        tips.append({'icon': '🚀', 'text': 'Start your fitness journey! Add your first workout.'})
    elif stats['total_workouts'] < 5:
        tips.append({'icon': '🔥', 'text': f"Great start! You have {stats['total_workouts']} workouts logged. Keep it up!"})
    else:
        tips.append({'icon': '🏆', 'text': f"Amazing! {stats['total_workouts']} workouts completed. You're building a habit!"})
    
    if stats['total_calories'] > 1000:
        tips.append({'icon': '💪', 'text': f"You've burned {stats['total_calories']} total calories. Outstanding effort!"})
    
    if stats['avg_duration'] > 0:
        if stats['avg_duration'] < 30:
            tips.append({'icon': '⏱️', 'text': 'Try extending workouts to 30–45 minutes for better results.'})
        elif stats['avg_duration'] > 60:
            tips.append({'icon': '😴', 'text': 'Your sessions are intense! Make sure to rest and recover properly.'})
        else:
            tips.append({'icon': '✅', 'text': f"Perfect workout duration! {stats['avg_duration']:.0f} min average is ideal."})
    
    tips.append({'icon': '💧', 'text': 'Stay hydrated! Drink 2–3 liters of water daily for optimal performance.'})
    
    return tips


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("╔══════════════════════════════════════════╗")
    print("║  Smart Workout Analytics System          ║")
    print("║  Running at: http://127.0.0.1:5000       ║")
    print("╚══════════════════════════════════════════╝")
    app.run(debug=True, host='0.0.0.0', port=5000)
