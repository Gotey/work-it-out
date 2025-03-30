from flask import Flask, render_template, request, session, redirect, url_for
from workout_engine.generator import generate_workouts

app = Flask(__name__)
app.secret_key = "super_secret_key"  # In production, load this securely


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['user'] = {
            'age': request.form['age'],
            'height': request.form['height'],
            'weight': request.form['weight'],
            'gender': request.form['gender'],
            'goal': request.form['goal'],
            'days_per_week': int(request.form['days']),
        }

        session['schedule'], session['workouts'] = generate_workouts(session['user'])
        return redirect(url_for('dashboard'))

    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    schedule = session.get('schedule', [])
    return render_template('dashboard.html', schedule=schedule)


@app.route('/day/<int:day_id>')
def day_view(day_id):
    workouts = session.get('workouts', [])
    workout = next((w for w in workouts if w['id'] == day_id), None)
    return render_template('day_view.html', workout=workout)


@app.route('/exercise/<int:day_id>/<int:exercise_index>')
def exercise_session(day_id, exercise_index):
    workouts = session.get('workouts', [])
    workout = next((w for w in workouts if w['id'] == day_id), None)

    if not workout or exercise_index >= len(workout["exercises"]):
        return "Exercise not found", 404

    exercise = workout["exercises"][exercise_index]
    return render_template('exercise_session.html', exercise=exercise, day=workout['name'])


if __name__ == '__main__':
    app.run(debug=True)
