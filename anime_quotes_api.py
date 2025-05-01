from flask import Flask, jsonify, request, render_template
import sqlite3

app = Flask(__name__, static_folder='.', template_folder='.')

DB_PATH = 'anime_quotes.db'

def query_db(query, args=(), one=False):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, args)
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv

@app.route('/')
def home():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True)
