from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__, static_folder='static')
CORS(app)
DATABASE = 'guestbook.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    return conn

def create_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- unique ID for each entry
            name TEXT,                             -- name of the person
            message TEXT NOT NULL,    -- their message (required)
            createdAt TEXT NOT NULL   -- time the entry was added
        )
    ''')
    conn.commit()   # Save changes
    conn.close()    # Close the connection

@app.route('/api/entries', methods=['GET'])

def get_entries():
    conn = get_db_connection()     # Connect to the database

    # Check for name query parameter
    name_filter = request.args.get('name')

    if name_filter:
        # Filter entries by name (case-insensitive partial match)
        rows = conn.execute('SELECT * FROM entries WHERE name LIKE ? ORDER BY id DESC', ('%' + name_filter + '%',)).fetchall()
    else:
        # Retrieve all rows from the entries table, newest first
        rows = conn.execute('SELECT * FROM entries ORDER BY id DESC').fetchall()

    conn.close()

    # Convert each row (SQLite Row object) into a Python dictionary
    entries = [dict(row) for row in rows]

    # Return all entries as JSON (so frontend can display them easily)
    return jsonify(entries)

@app.route('/api/entries', methods=['POST'])

def add_entry():
    # Get the data sent by the frontend (in JSON format)
    data = request.get_json()

    # Get the name and message from the data; default name is 'Anonymous'
    name = data.get('name', 'Anonymous').strip()
    message = data.get('message', '').strip()

    # If the message is empty, return an error (HTTP 400 = Bad Request)
    if not message:
        return jsonify({'error': 'Message is required'}), 400

        # Get the current date and time in ISO format (e.g. 2025-11-03T12:34:56)
    createdAt = datetime.now().isoformat()

    # Insert the new entry into the database
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO entries (name, message, createdAt) VALUES (?, ?, ?)',
        (name, message, createdAt)
    )
    conn.commit()   # Save the new entry
    conn.close()    # Close the database connection

    # Return the new entry as JSON with status code 201 (Created)
    return jsonify({'name': name, 'message': message, 'createdAt': createdAt}), 201






@app.route('/api/entries/<int:id>', methods=['PUT'])
def update_entry(id):
    # Get the data sent by the frontend (in JSON format)
    data = request.get_json()

    # Get the new message from the data
    message = data.get('message', '').strip()

    # If the message is empty, return an error (HTTP 400 = Bad Request)
    if not message:
        return jsonify({'error': 'Message is required'}), 400

    # Connect to the database
    conn = get_db_connection()

    # Execute UPDATE query for the specified ID
    conn.execute('UPDATE entries SET message = ? WHERE id = ?', (message, id))
    conn.commit()   # Save the changes

    # Check if any row was updated
    if conn.total_changes > 0:
        conn.close()
        return jsonify({'message': f'Entry with ID {id} updated successfully'}), 200
    else:
        conn.close()
        return jsonify({'error': f'Entry with ID {id} not found'}), 404


@app.route('/api/entries/<int:id>', methods=['DELETE'])
def delete_entry(id):
    # Connect to the database
    conn = get_db_connection()

    # Execute DELETE query for the specified ID
    conn.execute('DELETE FROM entries WHERE id = ?', (id,))
    conn.commit()   # Save the changes

    # Check if any row was deleted
    if conn.total_changes > 0:
        conn.close()
        return jsonify({'message': f'Entry with ID {id} deleted successfully'}), 200
    else:
        conn.close()
        return jsonify({'error': f'Entry with ID {id} not found'}), 404
    





@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static_file(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    # Ensure the database table exists before starting the app
    create_table()

    # Start the Flask development server
    app.run(debug=True, port=5000)




