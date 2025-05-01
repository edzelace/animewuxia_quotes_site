from flask import Flask, jsonify, request, render_template
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

DB_PATH = 'anime_quotes.db'

# ---------- DATABASE HELPERS ----------

def query_db(query, args=(), one=False):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, args)
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv

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



@app.route('/')
def home():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    with sqlite3.connect(DB_PATH) as conn:
        # Add unique IP
        conn.execute("INSERT OR IGNORE INTO visitors (ip) VALUES (?)", (ip,))
        conn.commit()

        # Get unique visitor count
        cursor = conn.execute("SELECT COUNT(*) FROM visitors")
        unique_visits = cursor.fetchone()[0]

    return render_template('index.html', unique_visits=unique_visits, now=datetime.utcnow())

@app.route('/quotes/random')
def random_quote():
    result = query_db("SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1", one=True)
    return jsonify(dict(result))

@app.route('/quotes')
def get_quotes():
    anime = request.args.get('anime')
    character = request.args.get('character')
    keyword = request.args.get('keyword')

    query = "SELECT * FROM quotes WHERE 1=1"
    params = []

    if anime:
        query += " AND anime LIKE ?"
        params.append(f"%{anime}%")
    if character:
        query += " AND character LIKE ?"
        params.append(f"%{character}%")
    if keyword:
        query += " AND quote LIKE ?"
        params.append(f"%{keyword}%")

    results = query_db(query, params)
    return jsonify([dict(row) for row in results])

# ---------- STARTUP ----------

if __name__ == '__main__':
    initialize_views_table()
    initialize_visitors_table()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
