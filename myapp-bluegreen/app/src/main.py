# Placeholder for main.py

## 🐍 **app/src/main.py**

```python
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    version = os.getenv("APP_VERSION", "blue")
    return jsonify(message=f"Hello from {version} environment!")

@app.route('/healthz')
def health():
    return jsonify(status="ok"), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)