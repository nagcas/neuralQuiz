import os
import requests
import sqlite3
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)

USERNAME = 'admin'
PASSWORD = 'admin'

API_KEY_WEATHER = os.getenv('API_KEY_WEATHER')
app.secret_key = os.getenv('SECRET_KEY')

# url weather 
BASE_URL = 'https://api.openweathermap.org/data/2.5/forecast'

# init database 
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()


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

    # manual grouping by data
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

        temps = []
        for x in items:
            temps.append(x['main']['temp'])

        temp_max = max(temps)
        temp_min = min(temps)

        # we are looking for the 12:00 time
        midday = None
        for x in items:
            if '12:00:00' in x['dt_txt']:
                midday = x
                break

        if not midday:
            midday = items[0]

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
  else:
    city = 'Roma,it'
  
  weather = get_weather(city)
  
  username = controlSession()
  if username:
    return render_template('home.html', weather=weather, username=username)
  return render_template('home.html', weather=weather)


# route user login
@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'GET':
    return render_template('login.html')
  else:
    username = request.form['username']
    password = request.form['password']
    if username == USERNAME and password == PASSWORD:
      session['username'] = username
      return redirect(url_for('quiz'))
    else:
      return '<h1>Wrong username or password</h1>'


# route user register
@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'GET':
    return render_template('register.html')
  else:
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    if not username or not password or not confirm_password:
      flash('Inserisci username o password!', 'warning')
      return redirect(url_for('register'))
    elif username and password == confirm_password:
      flash('Registrazione avvenuta con successo. Vai al login!', 'success')
      return redirect(url_for('register'))
    else:
      flash('Le password non coindidono. Riprova!', 'danger')
      return redirect(url_for('register'))
    # return redirect(url_for('login'))


# route logout
@app.route('/logout')
def logout():
  session.pop('username', None)
  return redirect(url_for('home'))


# route about
@app.route('/about')
def about():
  username = controlSession()
  if username:
    return render_template('about.html', username=username)
  return render_template('about.html')


# route quiz page protected
@app.route('/quiz')
def quiz():
  username = controlSession()
  if username:
    return render_template('quiz.html', username=username)
  else:
    return redirect(url_for('login'))
  
# control session user
def controlSession():
  if 'username' in session:
    username = session['username']
    return username
  
if __name__ == '__main__':
  app.run(debug=True)
  