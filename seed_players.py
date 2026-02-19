import sqlite3
import hashlib

DATABASE = "users.db"

players = [
    ("neural_master", 95),
    ("ai_wizard", 88),
    ("deep_learner", 76),
    ("data_hunter", 82),
    ("ml_engineer", 91),
    ("cv_expert", 67),
    ("nlp_guru", 99),
    ("python_brain", 73),
    ("tensor_pro", 85),
    ("vision_ai", 60),
    ("code_ninja", 78),
    ("smart_algo", 69),
    ("logic_master", 74),
    ("brain_byte", 92),
    ("future_dev", 64),
    ("data_mind", 87),
    ("net_runner", 58),
    ("ai_scout", 81),
    ("model_builder", 70),
    ("neuro_hacker", 83)
]

def insert_players():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    for username, score in players:
        # password fittizia: "password123"
        hashed_password = hashlib.sha256("password123".encode("utf-8")).hexdigest()

        try:
            cur.execute("""
                INSERT INTO users (username, password, score)
                VALUES (?, ?, ?)
            """, (username, hashed_password, score))
        except sqlite3.IntegrityError:
            print(f"{username} già presente")

    conn.commit()
    conn.close()
    print("Giocatori inseriti con successo!")

if __name__ == "__main__":
    insert_players()
