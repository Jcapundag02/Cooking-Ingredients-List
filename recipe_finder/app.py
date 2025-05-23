from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
RECIPE_FILE = 'recipes.json'
USER_FILE = 'users.json'

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    ingredient = request.form['ingredient'].lower()
    if not os.path.exists(RECIPE_FILE):
        return render_template('results.html', recipes=[], ingredient=ingredient)
    
    with open(RECIPE_FILE) as f:
        recipes = json.load(f)

    matching = [r for r in recipes if any(ingredient in ing.lower() for ing in r['ingredients'])]
    return render_template('results.html', recipes=matching, ingredient=ingredient)

@app.route('/add_to_list', methods=['POST'])
def add_to_list():
    data = request.get_json()
    recipe = {
        "name": data['recipe_name'],
        "ingredients": data['ingredients'].split(', ')
    }

    if 'mylist' not in session:
        session['mylist'] = []

    if recipe not in session['mylist']:
        session['mylist'].append(recipe)
        session.modified = True
        return jsonify({'message': 'Added to list'}), 200
    else:
        return jsonify({'message': 'Already in list'}), 200

@app.route('/mylist')
def mylist():
    return render_template('mylist.html', mylist=session.get('mylist', []))

@app.route('/clear_list')
def clear_list():
    session.pop('mylist', None)
    return redirect(url_for('mylist'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']

        if username in users:
            return render_template('register.html', error="Username already exists")
        else:
            users[username] = password
            save_users(users)
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
