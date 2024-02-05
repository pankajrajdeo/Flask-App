from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/home/ubuntu/flaskapp/uploads'
app.config['USER_DATA_FILE'] = '/home/ubuntu/flaskapp/users.json'

print(os.getcwd())

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def save_user(username, password, first_name, last_name, email, filename=None):
    users = load_users()
    users[username] = {
        'password': password,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'filename': filename
    }
    with open(app.config['USER_DATA_FILE'], 'w') as file:
        json.dump(users, file)

def load_users():
    try:
        with open(app.config['USER_DATA_FILE'], 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        
        file = request.files['file']
        filename = None
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        
        save_user(username, password, first_name, last_name, email, filename)
        return redirect(url_for('user_details', username=username))
    
    return render_template('register.html')

@app.route('/user_details')
def user_details():
    username = request.args.get('username')
    users = load_users()
    user = users.get(username)
    if user:
        word_count = None
        if user['filename']:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], user['filename'])
            word_count = count_words_in_file(file_path)
        return render_template('user_details.html', user=user, word_count=word_count)
    return 'User not found'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Remember, in a real app, passwords should be hashed!
        
        users = load_users()
        user = users.get(username)
        
        if user and user['password'] == password:
            return redirect(url_for('user_details', username=username))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

def count_words_in_file(filepath):
    with open(filepath, 'r') as file:
        contents = file.read()
    return len(contents.split())

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
