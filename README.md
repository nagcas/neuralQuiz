# AI Quiz Web App 🧠🎮

![Screenshot](./assets/images/screenshot.png)

Questa è una **web app interattiva di quiz** rivolta a un pubblico di adolescenti, sviluppata con **Flask** e **SQLite3**. L’app combina funzionalità di quiz dinamico con previsioni meteo integrate, gestione utenti e classifiche aggiornate.

[Guarda il video](https://drive.google.com/file/d/1iwYGQT_rjD4xQ1qcAeNjuxcU1dhObnIV/view?usp=sharing)

---

## 🛠 Tecnologie utilizzate

- **Backend:** Python, Flask
- **Frontend:** HTML5, Bootstrap 5, Jinja2
- **Database:** SQLite3
- **API Meteo:** [OpenWeather](https://openweathermap.org/)
- **Gestione ambiente:** python-dotenv per SECRET_KEY e API_KEY
- **Distribuzione:** PythonAnywhere

---

## ⚡ Funzionalità principali

### Home Page

- Campo di input per inserire la città
- Tabella meteo per **3 giorni** (oggi, domani, dopodomani) con:
  - Nome giorno (Lunedì, Martedì…)
  - Temperatura diurna e notturna
  - Icona meteo rappresentativa
- Informazioni aggiuntive sul meteo locale

### Registrazione

- Username unico
- Password e conferma password
- Nickname unico
- Messaggi di alert dinamici con **Bootstrap 5**

### Login

- Login e password
- Validazione con messaggi di errore

### Quiz

- Domande infinite e casuali sugli argomenti:
  - Intelligenza artificiale in Python
  - Visione computerizzata
  - NLP (Elaborazione del Linguaggio Naturale)
  - Applicazioni di modelli AI in Python
- Ogni domanda ha 4 opzioni di risposta
- Punteggio totale collegato all’account utente

### Classifica

- Visualizza **nome utente e punteggio**
- Aggiornata ogni volta che un utente completa il quiz

### Navigazione

- Menu di navigazione presente in ogni pagina:
  - Home
  - Registrazione (visibile solo se non loggato)
  - Login (visibile solo se non loggato)
  - Logout (visibile se loggato)
  - Quiz (visibile se loggato)
- Piè di pagina con il nome dello sviluppatore

---

## 💾 Setup locale

1. Clona il repository:

```bash
git clone https://github.com/tuo-username/ai-quiz-app.git
cd ai-quiz-app
```

2. Crea e attiva un virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

3. Installa le dipendenze:

```bash
pip install -r requirements.txt
```

4. Crea un file .env con le chiavi:

```bash
SECRET_KEY=tuo_secret_key
OPENWEATHER_API_KEY=la_tua_api_key
```

5. Avvio l'app
   python app.py
   Apri il browser su http://127.0.0.1:5000
