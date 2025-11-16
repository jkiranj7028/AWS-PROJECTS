from flask import Flask, request, render_template, abort, redirect, url_for
import shortuuid
import os
from pygments import highlight
from pygments.lexers import get_lexer_by_name, get_all_lexers
from pygments.formatters import HtmlFormatter

app = Flask(__name__)

# Directory to store paste files
PASTE_DIR = 'pastes'
if not os.path.exists(PASTE_DIR):
    os.makedirs(PASTE_DIR)

# Function to get available programming languages for syntax highlighting
def get_language_options():
    return sorted([(lexer[1][0], lexer[0]) for lexer in get_all_lexers() if lexer[1]])

# Route for the main page to create a paste
@app.route('/', methods=['GET'])
def index():
    # Render the form with available languages
    return render_template('index.html', languages=get_language_options())

@app.route('/create', methods=['POST'])
def create_paste():
    content = request.form.get('content')
    language = request.form.get('language', 'text') # Default to plain text

    if not content:
        return "Content cannot be empty!", 400

    paste_id = shortuuid.uuid()
    file_path = os.path.join(PASTE_DIR, paste_id)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"{language}\n{content}")

    # Redirect to the new paste's view page
    return redirect(url_for('view_paste', paste_id=paste_id))

# Route to view a specific paste by its ID
@app.route('/<paste_id>')
def view_paste(paste_id):
    file_path = os.path.join(PASTE_DIR, paste_id)
    if not os.path.exists(file_path):
        abort(404)  # Return a 404 error if the paste does not exist

    with open(file_path, 'r', encoding='utf-8') as f:
        language = f.readline().strip()  # First line is the language
        content = f.read()  # Remaining content is the paste

    lexer = get_lexer_by_name(language, stripall=True)
    # Use a dark theme for the formatter
    formatter = HtmlFormatter(linenos=True, cssclass="source", style="monokai")
    highlighted_content = highlight(content, lexer, formatter)
    highlight_css = formatter.get_style_defs('.source')

    return render_template('view.html', paste_content=highlighted_content, highlight_css=highlight_css)

if __name__ == '__main__':
    app.run(debug=True)
 