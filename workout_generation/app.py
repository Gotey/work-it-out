from flask import Flask, request, jsonify
from flask_cors import CORS
from workout_engine.generator import generate_workouts

app = Flask(__name__)
CORS(app)  # Allow Vercel frontend to call Flask

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    user_data = request.json
    if not user_data:
        return jsonify({"error": "Missing user data"}), 400

    # Generate workouts using AI-powered generator
    schedule, workouts = generate_workouts(user_data)
    return jsonify({"schedule": schedule, "workouts": workouts}), 200


@app.route('/api/health')
def health_check():
    return jsonify({"status": "online"}), 200


if __name__ == '__main__':
    app.run(debug=True)
