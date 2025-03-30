import random
from .exercise_db import exercise_db

def generate_weekly_schedule(days_per_week):
    if days_per_week == 3:
        return ["Push", "Pull", "Legs"]
    elif days_per_week == 4:
        return ["Upper", "Lower", "Push", "Pull"]
    elif days_per_week >= 5:
        return ["Push", "Pull", "Legs", "Upper", "Full Body"]
    else:
        return ["Full Body"] * days_per_week

def generate_workouts(user):
    split = generate_weekly_schedule(user['days_per_week'])
    workouts = []

    for i, day_type in enumerate(split):
        workout = {"id": i + 1, "name": f"{day_type} Day", "exercises": []}

        if day_type == "Push":
            workout["exercises"] += random.sample(exercise_db["chest"], 1)
            workout["exercises"] += random.sample(exercise_db["shoulders"], 1)
            workout["exercises"] += random.sample(exercise_db["triceps"], 1)

        elif day_type == "Pull":
            workout["exercises"] += random.sample(exercise_db["back"], 1)
            workout["exercises"] += random.sample(exercise_db["biceps"], 1)
            workout["exercises"] += random.sample(exercise_db["core"], 1)

        elif day_type == "Lower":
            workout["exercises"] += random.sample(exercise_db["legs"], 2)
            workout["exercises"] += random.sample(exercise_db["core"], 1)

        elif day_type == "Upper":
            workout["exercises"] += random.sample(exercise_db["chest"], 1)
            workout["exercises"] += random.sample(exercise_db["back"], 1)
            workout["exercises"] += random.sample(exercise_db["shoulders"], 1)

        elif day_type == "Full Body":
            workout["exercises"] += random.sample(exercise_db["legs"], 1)
            workout["exercises"] += random.sample(exercise_db["chest"], 1)
            workout["exercises"] += random.sample(exercise_db["back"], 1)
            workout["exercises"] += random.sample(exercise_db["core"], 1)
        
        elif day_type == "Cardio":
            workout["exercises"] += random.sample(exercise_db["cardio"], 1)

        # Add default sets and reps
        for ex in workout["exercises"]:
            ex["sets"] = 3
            ex["reps"] = 10

        workouts.append(workout)

    schedule = [{"day": f"Day {i+1}", "workout_id": w["id"]} for i, w in enumerate(workouts)]
    return schedule, workouts
