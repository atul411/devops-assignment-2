PROGRAMS = {
    "FL": {
        "key": "FL",
        "name": "Fat Loss",
        "factor": 22,
        "color": "#e74c3c",
        "workout": (
            "Mon: 5x5 Back Squat + AMRAP\n"
            "Tue: EMOM 20min Assault Bike\n"
            "Wed: Bench Press + 21-15-9\n"
            "Thu: 10RFT Deadlifts/Box Jumps\n"
            "Fri: 30min Active Recovery"
        ),
        "diet": (
            "B: 3 Egg Whites + Oats Idli\n"
            "L: Grilled Chicken + Brown Rice\n"
            "D: Fish Curry + Millet Roti\n"
            "Target: 2,000 kcal"
        ),
    },
    "MG": {
        "key": "MG",
        "name": "Muscle Gain",
        "factor": 35,
        "color": "#2ecc71",
        "workout": (
            "Mon: Squat 5x5\n"
            "Tue: Bench 5x5\n"
            "Wed: Deadlift 4x6\n"
            "Thu: Front Squat 4x8\n"
            "Fri: Incline Press 4x10\n"
            "Sat: Barbell Rows 4x10"
        ),
        "diet": (
            "B: 4 Eggs + PB Oats\n"
            "L: Chicken Biryani (250g Chicken)\n"
            "D: Mutton Curry + Jeera Rice\n"
            "Target: 3,200 kcal"
        ),
    },
    "BG": {
        "key": "BG",
        "name": "Beginner",
        "factor": 26,
        "color": "#3498db",
        "workout": (
            "Circuit Training: Air Squats, Ring Rows, Push-ups.\n"
            "Focus: Technique Mastery & Form (90% Threshold)"
        ),
        "diet": (
            "Balanced Tamil Meals: Idli-Sambar, Rice-Dal, Chapati.\n"
            "Protein: 120g/day"
        ),
    },
}

SITE_METRICS = {
    "capacity": 150,
    "area_sqft": 10000,
    "break_even_members": 250,
}


def get_program(key):
    return PROGRAMS.get(key.upper())


def calorie_for(weight_kg, program_key):
    program = get_program(program_key)
    if program is None:
        raise ValueError(f"Unknown program: {program_key}")
    if weight_kg is None or weight_kg <= 0:
        raise ValueError("Weight must be a positive number")
    return int(round(weight_kg * program["factor"]))
