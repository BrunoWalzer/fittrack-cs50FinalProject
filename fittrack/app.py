from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_in_production'

DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        muscle_group TEXT,
        FOREIGN KEY (workout_id) REFERENCES workouts (id)
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        sets INTEGER,
        reps INTEGER,
        weight REAL,
        FOREIGN KEY (exercise_id) REFERENCES exercises (id)
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS training_days (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        workout_id INTEGER,
        completed INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (workout_id) REFERENCES workouts (id)
    )''')

    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        try:
            conn.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                        (name, email, generate_password_hash(password)))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error='Email already registered')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('dashboard'))

        return render_template('login.html', error='Invalid email or password')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    user_id = session['user_id']

    # User workouts
    workouts = conn.execute('SELECT * FROM workouts WHERE user_id = ?', (user_id,)).fetchall()

    # Training days this month
    current_month = datetime.now().strftime('%Y-%m')
    training_count = conn.execute(
        'SELECT COUNT(*) as count FROM training_days WHERE user_id = ? AND date LIKE ?',
        (user_id, f'{current_month}%')
    ).fetchone()['count']

    # Get all training dates for calendar (last 6 months for better coverage)
    from datetime import timedelta
    six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    training_dates = conn.execute('''
        SELECT DISTINCT date
        FROM training_days td
        WHERE td.user_id = ? AND td.date >= ?
        ORDER BY td.date DESC
    ''', (user_id, six_months_ago)).fetchall()

    # Convert to simple list of dates
    training_days_list = [td['date'] for td in training_dates]

    # Recent trainings with details
    recent_trainings = conn.execute('''
        SELECT td.date, w.name as workout_name, td.workout_id
        FROM training_days td
        JOIN workouts w ON td.workout_id = w.id
        WHERE td.user_id = ?
        ORDER BY td.date DESC
        LIMIT 3
    ''', (user_id,)).fetchall()

    # Get exercises count for each recent training
    recent_with_details = []
    for training in recent_trainings:
        exercise_count = conn.execute('''
            SELECT COUNT(DISTINCT r.exercise_id) as count
            FROM records r
            JOIN exercises e ON r.exercise_id = e.id
            WHERE e.workout_id = ? AND r.date = ?
        ''', (training['workout_id'], training['date'])).fetchone()['count']

        recent_with_details.append({
            'date': training['date'],
            'workout_name': training['workout_name'],
            'exercise_count': exercise_count
        })

    conn.close()

    return render_template('dashboard.html',
                         workouts=workouts,
                         training_count=training_count,
                         recent_trainings=recent_with_details,
                         training_days=training_days_list)

@app.route('/api/workout-details/<date>')
def get_workout_details(date):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db()

    # Get workout info for this date
    workout_info = conn.execute('''
        SELECT w.name as workout_name, w.id as workout_id
        FROM training_days td
        JOIN workouts w ON td.workout_id = w.id
        WHERE td.user_id = ? AND td.date = ?
    ''', (session['user_id'], date)).fetchone()

    if not workout_info:
        conn.close()
        return jsonify({'error': 'No workout found'}), 404

    # Get all exercises performed on that date
    exercises = conn.execute('''
        SELECT e.name as exercise_name, e.muscle_group, r.sets, r.reps, r.weight
        FROM records r
        JOIN exercises e ON r.exercise_id = e.id
        JOIN workouts w ON e.workout_id = w.id
        WHERE w.id = ? AND r.date = ?
        ORDER BY e.id
    ''', (workout_info['workout_id'], date)).fetchall()

    conn.close()

    result = {
        'workout_name': workout_info['workout_name'],
        'exercises': [
            {
                'name': ex['exercise_name'],
                'muscle_group': ex['muscle_group'],
                'sets': ex['sets'],
                'reps': ex['reps'],
                'weight': ex['weight']
            }
            for ex in exercises
        ]
    }

    return jsonify(result)

@app.route('/workout/new', methods=['GET', 'POST'])
def new_workout():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        conn = get_db()
        conn.execute('INSERT INTO workouts (user_id, name) VALUES (?, ?)',
                    (session['user_id'], name))
        conn.commit()
        workout_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()
        return redirect(url_for('workout_detail', workout_id=workout_id))

    return render_template('workout_new.html')

@app.route('/workout/<int:workout_id>')
def workout_detail(workout_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    workout = conn.execute('SELECT * FROM workouts WHERE id = ? AND user_id = ?',
                          (workout_id, session['user_id'])).fetchone()

    if not workout:
        conn.close()
        return redirect(url_for('dashboard'))

    exercises = conn.execute('SELECT * FROM exercises WHERE workout_id = ?',
                           (workout_id,)).fetchall()
    conn.close()

    return render_template('workout_detail.html', workout=workout, exercises=exercises)

@app.route('/workout/<int:workout_id>/exercise/new', methods=['POST'])
def add_exercise(workout_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    name = request.form['name']
    muscle_group = request.form['muscle_group']

    conn = get_db()
    conn.execute('INSERT INTO exercises (workout_id, name, muscle_group) VALUES (?, ?, ?)',
                (workout_id, name, muscle_group))
    conn.commit()
    conn.close()

    return redirect(url_for('workout_detail', workout_id=workout_id))

@app.route('/exercise/<int:exercise_id>/delete', methods=['POST'])
def delete_exercise(exercise_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()

    # Get exercise and verify ownership
    exercise = conn.execute('''
        SELECT e.*, w.user_id, e.workout_id
        FROM exercises e
        JOIN workouts w ON e.workout_id = w.id
        WHERE e.id = ?
    ''', (exercise_id,)).fetchone()

    if not exercise or exercise['user_id'] != session['user_id']:
        conn.close()
        return redirect(url_for('dashboard'))

    workout_id = exercise['workout_id']

    # Delete associated records first (foreign key constraint)
    conn.execute('DELETE FROM records WHERE exercise_id = ?', (exercise_id,))

    # Delete the exercise
    conn.execute('DELETE FROM exercises WHERE id = ?', (exercise_id,))

    conn.commit()
    conn.close()

    return redirect(url_for('workout_detail', workout_id=workout_id))

@app.route('/workout/<int:workout_id>/delete', methods=['POST'])
def delete_workout(workout_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()

    # Verify ownership
    workout = conn.execute('SELECT * FROM workouts WHERE id = ? AND user_id = ?',
                          (workout_id, session['user_id'])).fetchone()

    if not workout:
        conn.close()
        return redirect(url_for('dashboard'))

    # Get all exercises in this workout
    exercises = conn.execute('SELECT id FROM exercises WHERE workout_id = ?',
                            (workout_id,)).fetchall()

    # Delete all records for these exercises
    for exercise in exercises:
        conn.execute('DELETE FROM records WHERE exercise_id = ?', (exercise['id'],))

    # Delete training days
    conn.execute('DELETE FROM training_days WHERE workout_id = ?', (workout_id,))

    # Delete all exercises
    conn.execute('DELETE FROM exercises WHERE workout_id = ?', (workout_id,))

    # Delete the workout
    conn.execute('DELETE FROM workouts WHERE id = ?', (workout_id,))

    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

@app.route('/train/<int:workout_id>')
def train_workout(workout_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    workout = conn.execute('SELECT * FROM workouts WHERE id = ? AND user_id = ?',
                          (workout_id, session['user_id'])).fetchone()

    exercises = conn.execute('SELECT * FROM exercises WHERE workout_id = ?',
                           (workout_id,)).fetchall()

    # Get last 3 records for each exercise
    exercise_history = {}
    for exercise in exercises:
        history = conn.execute('''
            SELECT date, sets, reps, weight
            FROM records
            WHERE exercise_id = ?
            ORDER BY date DESC
            LIMIT 3
        ''', (exercise['id'],)).fetchall()
        exercise_history[exercise['id']] = history

    conn.close()

    return render_template('train.html', workout=workout, exercises=exercises, exercise_history=exercise_history)

@app.route('/train/<int:workout_id>/complete', methods=['POST'])
def complete_training(workout_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    conn = get_db()

    # Register training day
    today = datetime.now().strftime('%Y-%m-%d')
    conn.execute('INSERT INTO training_days (user_id, date, workout_id) VALUES (?, ?, ?)',
                (session['user_id'], today, workout_id))

    # Register exercises performed
    for exercise in data.get('exercises', []):
        conn.execute('''INSERT INTO records (exercise_id, date, sets, reps, weight)
                       VALUES (?, ?, ?, ?, ?)''',
                    (exercise['id'], today, exercise['sets'],
                     exercise['reps'], exercise['weight']))

    conn.commit()
    conn.close()

    return jsonify({'success': True})

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()

    # Get all training days with workout details
    training_days = conn.execute('''
        SELECT td.id, td.date, w.name as workout_name, td.workout_id
        FROM training_days td
        JOIN workouts w ON td.workout_id = w.id
        WHERE td.user_id = ?
        ORDER BY td.date DESC
    ''', (session['user_id'],)).fetchall()

    # Get exercises and records for each training day
    history_data = []
    for day in training_days:
        # Get all records from that date for exercises in that workout
        records = conn.execute('''
            SELECT e.name as exercise_name, e.muscle_group, r.sets, r.reps, r.weight
            FROM records r
            JOIN exercises e ON r.exercise_id = e.id
            JOIN workouts w ON e.workout_id = w.id
            WHERE w.id = ? AND r.date = ?
            ORDER BY e.id
        ''', (day['workout_id'], day['date'])).fetchall()

        history_data.append({
            'date': day['date'],
            'workout_name': day['workout_name'],
            'workout_id': day['workout_id'],
            'records': records if records else []
        })

    conn.close()

    print(f"DEBUG: Found {len(history_data)} training days")  # Debug
    for item in history_data:
        print(f"DEBUG: {item['date']} - {item['workout_name']} - {len(item['records'])} exercises")

    return render_template('history.html', history_data=history_data)

@app.route('/exercise/<int:exercise_id>/history')
def exercise_history(exercise_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()

    # Get exercise details
    exercise = conn.execute('''
        SELECT e.*, w.name as workout_name, w.user_id
        FROM exercises e
        JOIN workouts w ON e.workout_id = w.id
        WHERE e.id = ?
    ''', (exercise_id,)).fetchone()

    # Check if user owns this exercise
    if not exercise or exercise['user_id'] != session['user_id']:
        conn.close()
        return redirect(url_for('dashboard'))

    # Get all records for this exercise
    records = conn.execute('''
        SELECT date, sets, reps, weight
        FROM records
        WHERE exercise_id = ?
        ORDER BY date DESC
    ''', (exercise_id,)).fetchall()

    conn.close()

    return render_template('exercise_history.html', exercise=exercise, records=records)

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)

# Debug route to check database
@app.route('/debug/db')
def debug_db():
    if 'user_id' not in session:
        return 'Not logged in'

    conn = get_db()

    training_days = conn.execute('SELECT * FROM training_days WHERE user_id = ?',
                                (session['user_id'],)).fetchall()
    records = conn.execute('''
        SELECT r.*, e.name as exercise_name
        FROM records r
        JOIN exercises e ON r.exercise_id = e.id
    ''').fetchall()

    conn.close()

    output = '<h1>Debug Database</h1>'
    output += f'<h2>Training Days ({len(training_days)})</h2>'
    for td in training_days:
        output += f'<p>ID: {td["id"]}, Date: {td["date"]}, Workout ID: {td["workout_id"]}</p>'

    output += f'<h2>Records ({len(records)})</h2>'
    for r in records:
        output += f'<p>Exercise: {r["exercise_name"]}, Date: {r["date"]}, Sets: {r["sets"]}, Reps: {r["reps"]}, Weight: {r["weight"]}</p>'

    return output
