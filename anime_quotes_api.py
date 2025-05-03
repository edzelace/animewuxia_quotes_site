from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

DB_PATH = 'anime_quotes.db'

# ---------- DATABASE HELPERS ----------

def query_db(query, args=(), one=False):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(query, args)
            rv = cur.fetchall()
            return (rv[0] if rv else None) if one else rv
    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        return None  # Or you could return a more specific error response

def initialize_views_table():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS views (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                count INTEGER DEFAULT 0
            )
        """)
        conn.execute("INSERT OR IGNORE INTO views (id, count) VALUES (1, 0)")
        conn.commit()

def initialize_visitors_table():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS visitors (
                ip TEXT PRIMARY KEY
            )
        """)
        conn.commit()

# ---------- ROUTES ----------

@app.route('/about')
def about():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM visitors")
        unique_visits = cursor.fetchone()[0]
    return render_template('about.html', unique_visits=unique_visits)

@app.route('/submit', methods=['GET', 'POST'])
def
