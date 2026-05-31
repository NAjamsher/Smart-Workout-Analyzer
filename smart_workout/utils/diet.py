"""
utils/diet.py
Diet recommendation engine based on user profile.
Calculates TDEE (Total Daily Energy Expenditure) and macro targets.
"""

# Meal plans for each goal
MEAL_PLANS = {
    'weight_loss': {
        'breakfast': ['Oatmeal with berries & protein powder', 'Egg white omelette with spinach', 'Greek yogurt with almonds'],
        'lunch':     ['Grilled chicken salad with olive oil', 'Tuna wrap with lettuce', 'Lentil soup with whole grain bread'],
        'dinner':    ['Baked salmon with steamed broccoli', 'Turkey stir-fry with vegetables', 'Chicken breast with quinoa'],
        'snacks':    ['Apple with peanut butter', 'Mixed nuts (30g)', 'Protein shake'],
        'tip':       '🔥 Create a 300–500 calorie deficit daily for healthy weight loss.'
    },
    'muscle_gain': {
        'breakfast': ['Scrambled eggs (4) with toast & avocado', 'Protein pancakes with banana', 'Overnight oats with protein powder'],
        'lunch':     ['Beef steak with rice and vegetables', 'Chicken breast with pasta', 'Salmon with sweet potato'],
        'dinner':    ['Ground beef with rice and beans', 'Chicken thighs with mashed potatoes', 'Tuna casserole with pasta'],
        'snacks':    ['Mass gainer shake', 'Cottage cheese with pineapple', 'Peanut butter sandwich'],
        'tip':       '💪 Eat 200–300 calories above maintenance. Prioritize protein post-workout.'
    },
    'endurance': {
        'breakfast': ['Whole grain toast with banana and honey', 'Oatmeal with dried fruits', 'Smoothie with oats, banana, milk'],
        'lunch':     ['Pasta with chicken and tomato sauce', 'Brown rice with tofu and vegetables', 'Whole wheat wrap with turkey'],
        'dinner':    ['Salmon with sweet potato and green beans', 'Chicken with quinoa and vegetables', 'Bean and vegetable stew'],
        'snacks':    ['Energy bar', 'Banana with almond butter', 'Rice cakes with hummus'],
        'tip':       '🚴 Carbs are your fuel! Time meals 2–3 hours before long workouts.'
    },
    'flexibility': {
        'breakfast': ['Smoothie bowl with seeds and fruits', 'Avocado toast with poached eggs', 'Chia pudding with berries'],
        'lunch':     ['Quinoa bowl with roasted vegetables', 'Mixed greens salad with salmon', 'Vegetable soup with legumes'],
        'dinner':    ['Baked chicken with turmeric and vegetables', 'Tofu with stir-fried vegetables', 'Lentil curry with rice'],
        'snacks':    ['Anti-inflammatory turmeric milk', 'Walnuts and dark chocolate', 'Celery with almond butter'],
        'tip':       '🧘 Anti-inflammatory foods (berries, turmeric, omega-3s) improve flexibility.'
    },
    'general_fitness': {
        'breakfast': ['Balanced omelette with vegetables and toast', 'Yogurt parfait with granola', 'Whole grain cereal with milk'],
        'lunch':     ['Mixed protein bowl with rice', 'Sandwich with lean protein and salad', 'Soup with whole grain crackers'],
        'dinner':    ['Grilled protein with vegetables and starch', 'Stir-fry with mixed proteins', 'Balanced plate with 3 food groups'],
        'snacks':    ['Mixed fruit', 'Nuts and seeds', 'Low-fat cheese with crackers'],
        'tip':       '⚡ Eat a balanced plate: 40% carbs, 30% protein, 30% healthy fats.'
    }
}


def calculate_tdee(age, weight_kg, height_cm, goal, gender='male', activity='moderate'):
    """
    Calculate TDEE using Mifflin-St Jeor equation + activity multiplier.
    
    TDEE = BMR × Activity Factor
    BMR (Basal Metabolic Rate) = calories your body burns at rest
    """
    # BMR
    if gender == 'male':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    
    # Activity multipliers
    activity_factors = {
        'sedentary':   1.2,
        'light':       1.375,
        'moderate':    1.55,
        'active':      1.725,
        'very_active': 1.9
    }
    tdee = bmr * activity_factors.get(activity, 1.55)
    
    # Adjust for goal
    goal_adjustment = {
        'weight_loss':     -400,
        'muscle_gain':     +300,
        'endurance':       +200,
        'flexibility':     +0,
        'general_fitness': +0
    }
    
    target_calories = tdee + goal_adjustment.get(goal, 0)
    
    # Macro split (grams)
    protein_g = round(weight_kg * 1.8, 0)   # 1.8g per kg bodyweight
    
    if goal == 'muscle_gain':
        carb_pct, fat_pct = 0.45, 0.25
    elif goal == 'weight_loss':
        carb_pct, fat_pct = 0.35, 0.35
    else:
        carb_pct, fat_pct = 0.45, 0.30
    
    remaining_cals = target_calories - (protein_g * 4)
    carbs_g  = round((target_calories * carb_pct) / 4, 0)
    fat_g    = round((target_calories * fat_pct) / 9, 0)
    
    bmi = round(weight_kg / ((height_cm / 100) ** 2), 1)
    
    return {
        'bmr':             round(bmr),
        'tdee':            round(tdee),
        'target_calories': round(target_calories),
        'protein_g':       int(protein_g),
        'carbs_g':         int(carbs_g),
        'fat_g':           int(fat_g),
        'bmi':             bmi,
        'water_liters':    round(weight_kg * 0.033, 1)   # Hydration recommendation
    }


def get_diet_plan(age, weight_kg, height_cm, goal, gender='male'):
    """Get full diet recommendation."""
    macros    = calculate_tdee(age, weight_kg, height_cm, goal, gender)
    meal_plan = MEAL_PLANS.get(goal, MEAL_PLANS['general_fitness'])
    
    return {**macros, **meal_plan, 'goal': goal.replace('_', ' ').title()}
