import json
import requests
from flask import Flask, render_template, request, redirect, url_for, session
import boto3

API_BASE_URL = 'https://vfruzgf8j6.execute-api.us-east-1.amazonaws.com/production'

app = Flask(__name__)

app.secret_key = 'dfdfdsfqeq3e2'

# Route for the login page
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None

    # Retrieve the flashed message from the session
    success_message = session.pop('success', None)

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = validate_credentials(email, password)
        if user:
            # Retrieve user name from DynamoDB
            user_name = user['user_name']

            # Store user name in session
            session['user_name'] = user_name
            session['email'] = email

            return redirect(url_for('main_page'))
        else:
            error = 'Email or password is invalid'
    return render_template('login.html', error=error, success_message=success_message)

# Function to validate user credentials
def validate_credentials(email, password):
    response = requests.post(f'{API_BASE_URL}/login', json={'email': email, 'password': password})
    if response.json()['statusCode'] == 200:
        body = json.loads(response.json()['body'])
        return body['user']
    return False

# Function to retrieve user name from DynamoDB
def get_user_name(email):
    response = requests.get(f'{API_BASE_URL}/user', params={'email': email})
    if response.json()['statusCode'] == 200:
        return response.json()['body']['user_name']
    return None

# Route for the main page
@app.route('/main', methods=['GET', 'POST'])
def main_page():
    if request.method == 'POST':
        # Get query parameters from the form
        title = request.form.get('title')
        year = request.form.get('year')
        artist = request.form.get('artist')

        # Perform the search
        searched_music = search_music(title, year, artist)

        # Retrieve subscribed music for the user
        email = session.get('email')
        if email:
            subscribed_music = get_subscribed_music(email)
        else:
            subscribed_music = None

        # If no results are retrieved, display a message
        if not searched_music:
            no_result_message = 'No result found. Please try again with different search criteria.'
            return render_template('main.html', no_result_message=no_result_message, subscribed_music=subscribed_music, user_name=session['user_name'])
        return render_template('main.html', searched_music=searched_music["searched_music"], user_name=session['user_name'], subscribed_music=subscribed_music)

    # Get the logged-in user's email from the session
    email = session.get('email')

    # Retrieve subscribed music for the user
    if email:
        subscribed_music = get_subscribed_music(email)
    else:
        subscribed_music = None

    return render_template('main.html', subscribed_music=subscribed_music, user_name=session.get('user_name'))

# Function to search music
def search_music(title, year, artist):
    response = requests.post(f'{API_BASE_URL}/search-music-db', json={'title': title, 'year': year, 'artist': artist})
    if response.json()['statusCode'] == 200:
        return json.loads(response.json()['body'])
    return None

# Function to retrieve subscribed music for a user
def get_subscribed_music(email):
    response = requests.post(f'{API_BASE_URL}/getUserSubscription', json={'email': email})
    if response.json()['statusCode'] == 200:
        return response.json()['body']
    return None

# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    success_message = None
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        response = requests.post(f'{API_BASE_URL}/register', json={'email': email, 'username':username, 'password': password})
        if response.json()['statusCode'] == 200:
            success_message = 'Registration successful. You can now login.'
            # Pass the success_message variable to the login template
            return render_template('login.html', success_message=success_message)
        else:
            error = 'The email already exists'
    return render_template('register.html', error=error)

# Route for the subscribe action
@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = session.get('email')
    title = request.form['title']
    print(title)
    if email:
        response = requests.post(f'{API_BASE_URL}/music-subscription', json={'email': email, 'title': title})
        if response.json()['statusCode'] == 200:
            return redirect(url_for('main_page'))
    return redirect(url_for('login'))

# Route for removing subscription
@app.route('/remove_subscription', methods=['POST'])
def remove_subscription():
    email = session.get('email')
    title = request.form['title']
    if email:
        response = requests.post(f'{API_BASE_URL}/remove-subscription', json={'email': email, 'title': title})
        if response.json()['statusCode'] == 200:
            return redirect(url_for('main_page'))
    return redirect(url_for('login'))

# Route for logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
