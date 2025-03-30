from flask import Flask, request, jsonify
from flask_cors import CORS
from workout_engine.generator import generate_workouts
import os
import subprocess

app = Flask(__name__)
CORS(app)  # Allow Vercel frontend to call Flask

# ✅ Lookup table to match exercise names to actual .py files
exercise_script_map = {
    "Push-ups": "push_ups.py",
    "Bench Press": "Bench_press.py",
    "Shoulder Press": "shoulder_press.py",
    "Tricep Pulldown": "tricep_pulldown.py",
    "Lateral Raises": "lat.py",
    "Squats": "squat_tracker.py",
    "Lunges": "lunges.py",
    "Crunches": "crunches_seated.py",
    "Bicep Curl": "bicep_curl.py",
    "Hammer Curl": "bicep_curl.py",  # Same script as Bicep Curl
    "Deadlift": "deadlift_tracker.py",
    "Leg Raises": "leg_raises.py",
    "Pullups": "Pull_up.py",
    "Pull-ups": "Pull_up.py",
    "Lat Pulldowns": "lat.py",
    "Incline Bench Press": "Bench_press.py"  # fallback
}

@app.route('/start-exercise', methods=['POST'])
def start_exercise():
    data = request.json
    exercise_name = data.get("exercise")

    if not exercise_name:
        return jsonify({"error": "No exercise name provided"}), 400

    script_name = exercise_script_map.get(exercise_name)
    if not script_name:
        return jsonify({"error": f"No script found for '{exercise_name}'"}), 404

    # Absolute path to the exercise_tracking directory
    script_path = os.path.abspath(
        os.path.join("..", "exercise_tracking", script_name)
    )

    # Launch the script in a new terminal window (Windows only)
    subprocess.Popen(["python", script_path], creationflags=subprocess.CREATE_NEW_CONSOLE)

    return jsonify({"status": f"Started {script_name}"}), 200

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    user_data = request.json
    if not user_data:
        return jsonify({"error": "Missing user data"}), 400

    schedule, workouts = generate_workouts(user_data)
    return jsonify({"schedule": schedule, "workouts": workouts}), 200

@app.route('/api/health')
def health_check():
    return jsonify({"status": "online"}), 200

if __name__ == '__main__':
    app.run(debug=True)
