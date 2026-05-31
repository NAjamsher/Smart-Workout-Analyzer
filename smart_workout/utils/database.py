"""
utils/database.py
SQLite database for storing workout history.
Handles Add / Delete / View operations.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'data/workouts.db'

def get_connection():
    """Get a database connection."""
    os.makedirs('data', exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    """Create the workouts table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT NOT NULL,
            workout_type TEXT NOT NULL,
            duration_min INTEGER NOT NULL,
            calories    REAL NOT NULL,
            notes       TEXT,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_workout(date, workout_type, duration_min, calories, notes=''):
    """Insert a new workout record."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO workouts (date, workout_type, duration_min, calories, notes) VALUES (?, ?, ?, ?, ?)',
        (date, workout_type, int(duration_min), float(calories), notes)
    )
    conn.commit()
    conn.close()

def get_all_workouts():
    """Fetch all workouts ordered by most recent first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM workouts ORDER BY date DESC')
    rows = cursor.fetchall()
    conn.close()
    
    columns = ['id', 'date', 'workout_type', 'duration_min', 'calories', 'notes', 'created_at']
    return [dict(zip(columns, row)) for row in rows]

def delete_workout(workout_id):
    """Delete a workout by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM workouts WHERE id = ?', (workout_id,))
    conn.commit()
    conn.close()

def get_summary_stats():
    """Get summary statistics for the dashboard."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*), SUM(calories), AVG(duration_min), SUM(duration_min) FROM workouts')
    row = cursor.fetchone()
    conn.close()
    
    return {
        'total_workouts':  row[0] or 0,
        'total_calories':  round(row[1] or 0, 1),
        'avg_duration':    round(row[2] or 0, 1),
        'total_minutes':   round(row[3] or 0, 1)
    }

# Initialize DB when module is imported
init_db()
