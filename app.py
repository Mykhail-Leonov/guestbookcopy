from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json, os
from datetime import datetime

app = Flask(__name__, static_folder='static')
CORS(app)

DATA_FILE = os.path.join('data', 'entries.json')



def read_entries():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def write_entries(entries):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2)


# API
@app.route('/api/entries', methods=['GET'])
def get_entries():
    entries = read_entries()
    return jsonify(entries)


@app.route('/api/entries', methods=['POST'])
def add_entry():
    data = request.get_json()
    name = data.get('name', 'Anonymous').strip()
    message = data.get('message', '').strip()

    if not message:
        return jsonify({'error': 'Message is required!'}), 400

    new_entry = {
        'id': int(datetime.now().timestamp() * 1000),
        'name': name,
        'message': message,
        'createdAt': datetime.now().isoformat()
    }

    entries = read_entries()
    entries.insert(0, new_entry)
    write_entries(entries)

    return jsonify(new_entry), 201


@app.route('/about', methods=['GET'])
def about():
    return jsonify({'Name': 'Sangeeta Bhettacharya', 'Module': 'Website development'})


# front-end
@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')


@app.route('/<path:path>')
def serve_static_file(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run(debug=True, port=5000)