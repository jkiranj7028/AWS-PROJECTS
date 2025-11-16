from flask import Flask, render_template, request, redirect, url_for, abort
import os

app = Flask(__name__)

# Configuration
PASTES_DIR = "pastes"

# Ensure the 'pastes' directory exists
if not os.path.exists(PASTES_DIR):
    os.makedirs(PASTES_DIR)

@app.route('/')
def index():
    """Renders the home page where users can create a new paste."""
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create_paste():
    """Handles the creation of a new paste."""
    content = request.form.get('content')
    if not content:
        return "Content cannot be empty!", 400

    # For simplicity, we'll use the content's hash as a unique ID
    paste_id = str(hash(content))
    with open(os.path.join(PASTES_DIR, paste_id), 'w') as f:
        f.write(content)
    return redirect(url_for('view_paste', paste_id=paste_id))

@app.route('/paste/<string:paste_id>')
def view_paste(paste_id):
    """Displays the content of a specific paste."""
    try:
        with open(os.path.join(PASTES_DIR, paste_id), 'r') as f:
            content = f.read()
        return f"<pre>{content}</pre>"
    except FileNotFoundError:
        abort(404)