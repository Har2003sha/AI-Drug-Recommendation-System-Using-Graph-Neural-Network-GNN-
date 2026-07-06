import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "drugs.db")


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine TEXT,
        uses TEXT,
        result TEXT,
        confidence INTEGER
    )
    """)

    conn.commit()
    conn.close()


def save_prediction(medicine, uses, result, confidence):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO predictions
    (medicine, uses, result, confidence)
    VALUES (?, ?, ?, ?)
    """, (medicine, uses, result, confidence))

    conn.commit()
    conn.close()


def get_all_predictions():

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT * FROM predictions ORDER BY id DESC")

    rows = cur.fetchall()

    conn.close()

    return rows


if __name__ == "__main__":
    init_db()
    print("Database Created Successfully")