🏋️ Smart Workout & Progress Analytics System
An AI-powered fitness web application that provides personalized workout recommendations, calorie predictions, progress tracking, and diet suggestions using Machine Learning.

🚀 Live Demo

Run locally at http://127.0.0.1:5000


📌 Project Overview
The Smart Workout and Progress Analytics System (SmartFit AI) is a full-stack web application built using Python and Flask. It uses a Random Forest Classifier trained on 2,000 user profiles to recommend personalized workout plans with 98.5% accuracy, and a Gradient Boosting Regressor to predict calories burned per session.

✨ Features
FeatureDescription🤖 AI Workout AnalyzerPersonalized workout recommendations using ML🔥 Calorie PredictionPredicts calories burned using Gradient Boosting📝 Workout TrackerLog and manage workout sessions (SQLite)📊 Analytics Dashboard4 real-time Matplotlib charts🥗 Diet SuggestionsTDEE-based personalized nutrition planning🔄 ETL PipelineData validation and feature engineering

🧠 Machine Learning Models
ModelTaskAccuracyRandom Forest ClassifierPredict workout type98.5%Gradient Boosting RegressorPredict calories burnedMAE: 140 cal
Input Features Used:

Age, Weight (kg), Height (cm), BMI
Gender, Fitness Goal, Experience Level

Workout Types Predicted:

Cardio + HIIT
Strength Training
Running + Cycling
Yoga + Stretching
Mixed Training


🛠️ Tech Stack
Backend     : Python 3.10+, Flask 2.x
ML          : Scikit-learn (Random Forest, Gradient Boosting)
Data        : Pandas, NumPy
Visualization : Matplotlib
Database    : SQLite3
Serialization : Joblib (.pkl files)
Frontend    : HTML5, CSS3, JavaScript (ES6)
Templating  : Jinja2
IDE         : Visual Studio Code

📁 Project Structure
smart_workout/
│
├── app.py                    # Flask application - all routes
├── run_pipeline.py           # Master setup script
├── requirements.txt          # Dependencies
│
├── pipeline/
│   ├── generate_dataset.py   # Generates 2000 synthetic profiles
│   └── etl_pipeline.py       # Extract, Validate, Transform, Load
│
├── models/
│   ├── train_model.py        # Model training script
│   ├── workout_classifier.pkl
│   ├── calorie_predictor.pkl
│   └── encoders.pkl
│
├── utils/
│   ├── predictor.py          # ML inference engine
│   ├── database.py           # SQLite CRUD operations
│   ├── diet.py               # TDEE calculation (Mifflin-St Jeor)
│   └── analytics.py          # Matplotlib chart generators
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── analyzer.html
│   ├── tracker.html
│   ├── dashboard.html
│   └── diet.html
│
├── data/
│   ├── raw/
│   ├── cleaned/
│   └── processed/
│
└── logs/

⚙️ Installation & Setup
1. Clone the repository
bashgit clone https://github.com/YOUR_USERNAME/Smart-Workout-Analyzer.git
cd Smart-Workout-Analyzer
2. Create virtual environment
bashpython -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate      # Mac/Linux
3. Install dependencies
bashpip install -r requirements.txt
4. Run the pipeline (first time only)
bashcd smart_workout
python run_pipeline.py
5. Start the application
bashpython app.py
6. Open in browser
http://127.0.0.1:5000

📊 Model Performance
Random Forest Classifier:
  ✅ Test Accuracy         : 98.50%
  ✅ Cross-Validation (5x) : 99.63%

Gradient Boosting Regressor:
  ✅ MAE                   : 140.06 calories
  ✅ RMSE                  : 175.19 calories
  ✅ R² Score              : 0.87

🔄 ETL Pipeline
RAW DATA (2000 profiles)
      ↓
   EXTRACT  →  Read CSV from data/raw/
      ↓
  VALIDATE  →  Check ranges, missing values
      ↓
 TRANSFORM  →  Add bmi_category, age_group, fitness_score
      ↓
    LOAD    →  Save to data/processed/
      ↓
  TRAIN ML  →  RandomForest + GradientBoosting

📸 Screenshots

<img width="1891" height="909" alt="image" src="https://github.com/user-attachments/assets/4003fdc5-1ce8-4ba7-8133-90537ec7128b" />
<img width="1871" height="901" alt="image" src="https://github.com/user-attachments/assets/20a306c2-5cc5-4f0b-beaf-4cd5218363fc" />
<img width="1891" height="901" alt="image" src="https://github.com/user-attachments/assets/ff2638a6-94e3-48d0-a3cc-85fce4bf1111" />




🔮 Future Enhancements

📱 Mobile application (Flutter)
⌚ Wearable device integration (Fitbit, Apple Watch)
☁️ Cloud deployment (AWS / GCP)
🧠 Deep Learning models (LSTM)
🥗 Food database API integration


👤 Author
Jamsher N A

Roll No: 24MCS026
II M.Sc. Computer Science — Semester IV
Sri Krishna Arts and Science College (SKASC), Coimbatore
Guided by: Dr. M. Raju M.Sc., Ph.D.


📄 License
This project is developed for academic purposes at SKASC — 2026.
