from flask import Flask, render_template, request, redirect, url_for, session
import boto3

app = Flask(__name__)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb',
                  aws_access_key_id="ASIAXYKJVXP7RNNKSNFU",
                  aws_secret_access_key="s0DYM+P4KiNgg5ha7RRo9OSvS7uzBi3fXJlmuo1u",
                  aws_session_token=r"IQoJb3JpZ2luX2VjENH//////////wEaCXVzLXdlc3QtMiJIMEYCIQDvFakheWIPTkIvZvnBXOLHYlq+cYjDUGfqTX6BImA3WgIhALx6WNgq0n1j8x5GtBuUWug9U2h7NxtXdWyKgLPdPDdSKr8CCPn//////////wEQABoMNTMzMjY3MzMyMDk1IgyMXNuhN7OhXnKgbK4qkwKOYYOYulsHNGjsGQql9xtIkGxkZMd3iwJhp4JHI6OpHiPTRLpm8BV1jhYsBFVxmI1+GHAHB0JfYP4mrvbVpb8EsA186M5bk4Cs8YrFA7Zl7VzzXEtyyR/lZCoa0fjtHhr7VmkxtuyGeZv+Tm+eZlxjwIpZNjMmjU6QmUtIq1eD9x6m6xcNtj4lMy5+6UX/JYWCwguGRp0YqcXZDDucOoXS4PCfdOm5wbbSdw0UvF2P6z1JBgNHYbD51bkGKpM6WDmdgbh1NIAxHC7g2RDpqy6PC0z0zUe3RU15mH7jP8AvUCOT0bDAThZqlme+zK1idMecbEkcW8X5Dz8cVfXW0XlyBIerd1GwLEG/3iODjQ0lDj4qpjCDlNKwBjqcAYauPyWqSr/JMkplvT3MPgnsisTszNbXM1F7JghQOFukJT+NM/arEKYtiPMhPbX7Fgu7//OiI9F3dyE9fzxjfhb/Mk7nQKy6gO1ZX9DFY5l/zp9VLrW7vPK9axpOBOrXFzBXksefthLDpNrHX/cGq4TDJIaGvdQjNPRXtvtwT7h/gAi2HqbjSkTegxcLVZCDB5rFbgTiwafOYolsow==",
                  region_name="us-east-1")
app.secret_key = 'dfdfdsfqeq3e2'

# DynamoDB table name
tableName = 'login'

# DynamoDB table name for music
music_table_name = 'music'

# Route for the login page
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    
    # Retrieve the flashed message from the session
    success_message = session.pop('success', None)
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if validate_credentials(email, password):
            # Retrieve user name from DynamoDB
            user_name = get_user_name(email)
            
            # Store user name in session
            session['user_name'] = user_name
            
            return redirect(url_for('main_page'))
        else:
            error = 'Email or password is invalid'
    return render_template('login.html', error=error, success_message=success_message)

# Function to retrieve user name from DynamoDB
def get_user_name(email):
    table = dynamodb.Table('login')
    response = table.get_item(Key={'email': email})
    if 'Item' in response:
        return response['Item']['user_name']
    return None

# Route for the main page
@app.route('/main', methods=['GET', 'POST'])
def main_page():
    user_name = session.get('user_name')
    if request.method == 'POST':
        # Get query parameters from the form
        title = request.form.get('title')
        year = request.form.get('year')
        artist = request.form.get('artist')
        
        # Perform the search
        searched_music = search_music_in_db(title, year, artist)
        
        # If no results are retrieved, display a message
        if not searched_music:
            no_result_message = 'No result is retrieved. Please try again'
            return render_template('main.html', no_result_message=no_result_message)
        
        return render_template('main.html', searched_music=searched_music, user_name=user_name)
    
    return render_template('main.html', user_name=user_name)

# Function to search music in the database based on the search term
def search_music_in_db(title, year, artist):
    # Get the music table
    music_table = dynamodb.Table('music')
    
    # Define the filter expressions for each search term
    filter_expressions = []
    expression_attribute_values = {}
    expression_attribute_names = {}  # New dictionary for attribute names
    
    if title:
        filter_expressions.append('#t = :title')
        expression_attribute_values[':title'] = title
        expression_attribute_names['#t'] = 'title'  # Alias for reserved keyword
    if year:
        filter_expressions.append('#y = :year')
        expression_attribute_values[':year'] = year
        expression_attribute_names['#y'] = 'year'  
    if artist:
        filter_expressions.append('#a = :artist')
        expression_attribute_values[':artist'] = artist
        expression_attribute_names['#a'] = 'artist'  
    
    # Combine filter expressions using 'AND'
    filter_expression = ' AND '.join(filter_expressions)
    
    # Perform the scan operation with the filter expression
    response = music_table.scan(
        FilterExpression=filter_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values
    )
    
    # Return the search results
    return response['Items']


# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    success_message = None
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        if not email_exists(email):
            create_user(email, username, password)
            success_message = 'Registration successful. You can now login.'
            # Pass the success_message variable to the login template
            return render_template('login.html', success_message=success_message)
        else:
            error = 'The email already exists'
    return render_template('register.html', error=error)


# Function to validate user credentials
def validate_credentials(email, password):
    table = dynamodb.Table('login')
    response = table.get_item(Key={'email': email})
    if 'Item' in response:
        if response['Item']['password'] == password:
            return True
    return False

# Function to check if email already exists in the login table
def email_exists(email):
    table = dynamodb.Table('login')
    response = table.get_item(Key={'email': email})
    return 'Item' in response

# Function to create a new user in the login table
def create_user(email, username, password):
    table = dynamodb.Table('login')
    table.put_item(Item={'email': email, 'user_name': username, 'password': password})

if __name__ == '__main__':
    app.run(debug=True)