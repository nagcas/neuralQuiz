import os
import requests
import sqlite3 as sq
import hashlib
import json
import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, g

app = Flask(__name__)

API_KEY_WEATHER = os.getenv('API_KEY_WEATHER')
DATABASE = 'users.db'
app.secret_key = os.getenv('SECRET_KEY')

# url weather 
BASE_URL = 'https://api.openweathermap.org/data/2.5/forecast'


# init database 
def init_db():
    conn = sq.connect(DATABASE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            score INT NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()


# connect database
@app.before_request
def before_request():
    db = sq.connect(DATABASE)
    g.db = db


# close connect database
@app.after_request
def after_request(response):
    g.db.close()
    return response


# check password
def check_password(db, username, hashed_password):
    cur = db.cursor()
    cur.execute("SELECT password, score FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    
    if user is None:
        return False, 0
    
    db_password = user[0]
    db_score = user[1]

    if db_password == hashed_password:
        return True, db_score
    else:
        return False, 0


# register new user
def register_user(db, username, hashed_password):
    cur = db.cursor()
    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    db.commit()
    return True
  

# search city weather
def get_weather(city):
    params = {
        'q': city,
        'appid': API_KEY_WEATHER,
        'units': 'metric',
        'lang': 'it'
    }

    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        return None

    data = response.json()
    city_name = data['city']['name']

    grouped = {}
    # manual grouping by date
    for item in data['list']:
        date = item['dt_txt'].split(' ')[0]
        if date not in grouped:
            grouped[date] = []
        grouped[date].append(item)

    forecast = []
    count = 0

    for date in grouped:
        if count == 3:
            break

        items = grouped[date]

        temps = [x['main']['temp'] for x in items]
        temp_max = max(temps)
        temp_min = min(temps)

        # we are looking for the 12:00 time
        midday = next((x for x in items if '12:00:00' in x['dt_txt']), items[0])
        icon = midday['weather'][0]['icon']

        forecast.append({
            'date': date,
            'temp_day': temp_max,
            'temp_night': temp_min,
            'icon': icon
        })

        count += 1

    return {
        'city': city_name,
        'forecast': forecast
    }


# route home page
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        city = request.form.get('city')
        if not city:
            flash('Devi inserire una città!', 'warning')
            return redirect(url_for('home'))
    else:
        city = 'Roma,it'
  
    weather = get_weather(city)
  
    # check if the city exists
    if weather is None:
        flash('Città non trovata. Controlla il nome.', 'warning')
        return redirect(url_for('home'))
  
    username, score = controlSession()
    if username:
        return render_template('home.html', weather=weather, username=username, score=score)
    return render_template('home.html', weather=weather)


# route user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    username, _ = controlSession()
    
    if username:
        return redirect(url_for('home'))
    
    if request.method == 'GET':
        return render_template('login.html')
  
    username = request.form['username'].lower()
    password = request.form['password'].lower()
  
    if not username or not password:
        flash('Inserisci tutti i campi', 'warning')
        return redirect(url_for('login'))
  
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
      
    db = g.db
    valid, score = check_password(db, username, hashed_password)
    if valid:
        session['username'] = username
        session['score'] = score
        return redirect(url_for('ranking'))
    else:
        flash('Username o password non corretti!', 'warning')
        return redirect(url_for('login'))


# route user register
@app.route('/register', methods=['GET', 'POST'])
def register():
    username, _ = controlSession()
    
    if username:
        return redirect(url_for('home'))
    
    if request.method == 'GET':
        return render_template('register.html')
  
    username = request.form['username'].lower()
    password = request.form['password'].lower()
    confirm_password = request.form['confirm_password']
    
    if not username or not password or not confirm_password:
        flash('Compila tutti i campi!', 'warning')
        return redirect(url_for('register'))
    elif password != confirm_password:
        flash('Le password non coincidono!', 'danger')
        return redirect(url_for('register'))
    else:
        hashed_password = hashlib.sha256(confirm_password.encode('utf-8')).hexdigest()
        try:
            db = g.db
            if register_user(db, username, hashed_password):
                flash('Registrazione avvenuta con successo. Vai al login!', 'success')
                return redirect(url_for('register'))
        except sq.IntegrityError:
            flash('Username già esistente', 'info')
            return redirect(url_for('register'))


# route logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('score', None)
    return redirect(url_for('home'))


# load questions json
def load_questions():
    with open("questions.json", "r") as f:
        return json.load(f)


# route quiz page protected
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    username, db_score = controlSession()
    
    if not username:
        return redirect(url_for('login'))

    questions = load_questions()

    # initialize quiz if it doesn't exist in session
    if 'quiz_questions' not in session:
        random.shuffle(questions)
        session['quiz_questions'] = questions
        session['current'] = 0
        session['quiz_score'] = 0

    current = session['current']
    total_questions = len(session['quiz_questions'])

    # end quiz
    if current >= total_questions:
        final_quiz_score = session['quiz_score']
        db = g.db
        update_score(db, username, final_quiz_score)
        session['score'] = db_score + final_quiz_score

        session.pop('quiz_questions')
        session.pop('current')
        session.pop('quiz_score')

        flash(f'Hai completato il quiz! + {final_quiz_score} punti', 'success')
        return redirect(url_for('ranking'))

    question = session['quiz_questions'][current]

    # if I send a reply
    if request.method == 'POST':
        selected = request.form.get('answer')
        if selected == question['answer']:
            session['quiz_score'] += 1
        session['current'] += 1
        return redirect(url_for('quiz'))

    progress = int((current / total_questions) * 100)

    return render_template(
        'quiz.html',
        username=username,
        score=db_score + session['quiz_score'],
        question=question,
        current_question=current + 1,
        total_questions=total_questions,
        progress=progress,
    )


# update score
def update_score(db, username, score):
    cur = db.cursor()
    cur.execute("""
        UPDATE users
        SET score = score + ?
        WHERE username = ?
    """, (score, username))
    db.commit()


# ranking
@app.route('/ranking')
def ranking():
    username, score = controlSession()
    
    if not username:
        return redirect(url_for('login'))
      
    db = g.db
    cur = db.cursor()
    cur.execute("""
        SELECT username, score
        FROM users
        ORDER BY score DESC
    """)
    users = cur.fetchall()

    # first 3 classified
    top_three = users[:3]

    # everyone else
    others = users[3:]

    return render_template(
        "ranking.html",
        username=username,
        score=score,
        top_three=top_three,
        others=others
    )
  

# control session user
def controlSession():
    username = session.get('username')
    score = session.get('score')
    return username, score


if __name__ == '__main__':
    app.run(debug=True)

  