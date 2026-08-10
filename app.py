from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Flask is running!"})

@app.route('/api/transform', methods=['POST'])
def transform():
    return jsonify({"success": True, "message": "API works!"})
