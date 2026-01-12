from flask import Flask, send_from_directory
import os

app = Flask(__name__)

WEB_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'web')

@app.route('/')
def index():
    print(f"Serving from: {WEB_DIR}")
    print(f"File exists: {os.path.exists(os.path.join(WEB_DIR, 'index.html'))}")
    return send_from_directory(WEB_DIR, 'index.html')

if __name__ == '__main__':
    print(f"Web directory: {WEB_DIR}")
    print(f"Starting server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
