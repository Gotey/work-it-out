import openai
import json
import os
from dotenv import load_dotenv
from .exercise_db import exercise_db

# Modern API client (this is required now)
load_dotenv()  # Load environment variables from .env file
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_workouts(user):
    prompt = build_prompt(user)

    # Corrected API call for openai>=1.x
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a personal trainer who creates beginner-friendly workout plans."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )

    content = response.choices[0].message.content

    # Handle code block wrapping if GPT returns ```json ... ```
    if content.startswith("```"):
        content = content.strip().strip("```json").strip("```")

    try:
        plan = json.loads(content)
    except json.JSONDecodeError:
        raise Exception("GPT did not return valid JSON.")

    # Build the Flask app-friendly structure
    schedule = [{"day": f"Day {i+1}", "workout_id": i+1} for i in range(len(plan))]
    workouts = [{"id": i+1, "name": w["day_name"], "exercises": w["exercises"]} for i, w in enumerate(plan)]

    return schedule, workouts


def build_prompt(user):
    # Serialize exercise_db nicely for the prompt
    exercise_text = json.dumps(exercise_db, indent=2)

    return f"""
You are to create a personalized, beginner-friendly workout plan using ONLY the following exercises:

{exercise_text}

The user is:
- Age: {user['age']}
- Gender: {user['gender']}
- Goal: {user['goal']}
- Days per week: {user['days_per_week']}

Rules:
1. Create exactly {user['days_per_week']} workouts.
2. Use classic muscle splits like Push / Pull / Legs.
3. Each workout day must have 3 to 5 exercises.
4. For each exercise provide:
    - name (must exactly match the name from the provided exercise list)
    - sets
    - reps

Output the entire workout plan strictly as valid JSON ONLY, like this:

[
    {{
        "day_name": "Push Day",
        "exercises": [
            {{"name": "Bench Press", "sets": 3, "reps": 10}},
            ...
        ]
    }},
    ...
]

Do not include any explanations, notes, or comments. Only output valid JSON.
    """.strip()
