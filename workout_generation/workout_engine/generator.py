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

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a strict JSON generator for a workout planner app."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3  # Lower temperature for more deterministic JSON output
    )

    content = response.choices[0].message.content.strip()

    # Hardened: Remove any accidental code block wrappers
    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    # Debug raw GPT response
    print("Raw GPT output:\n", content)

    try:
        plan = json.loads(content)
    except json.JSONDecodeError:
        raise Exception("GPT did not return valid JSON")

    # Inject GIFs
    for workout in plan:
        for exercise in workout["exercises"]:
            ex_name = exercise["name"]
            if ex_name in exercise_db:
                exercise["gif"] = exercise_db[ex_name].get("gif", "")

    schedule = [{"day": f"Day {i+1}", "workout_id": i+1} for i in range(len(plan))]
    workouts = [{"id": i+1, "name": w["day_name"], "exercises": w["exercises"]} for i, w in enumerate(plan)]

    return schedule, workouts


def build_prompt(user):
    exercise_text = json.dumps(exercise_db, indent=2)

    return f"""
You are a JSON-only generator. 
Do not include ```json, ``` or any other markdown. 
Do not write ANY explanation.

The user is:
- Date of Birth: {user.get('dob')}
- Gender: {user.get('sex')}
- Weight: {user.get('weight')} {user.get('weightUnit')}
- Goal: {user.get('goal')}
- Days per week: {user.get('daysPerWeek')}

You must create a JSON array of exactly {user.get('daysPerWeek')} workout days.
Each day MUST be an object like this:
{{
    "day_name": "Push Day",
    "exercises": [
        {{"name": "Bench Press", "sets": 3, "reps": 10}},
        ...
    ]
}}

Use ONLY the following list of exercises:

{exercise_text}

Rules:
- Do NOT output code fences.
- Do NOT explain.
- Only output the JSON array.
    """.strip()
