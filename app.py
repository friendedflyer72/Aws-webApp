from flask import Flask, render_template, request, redirect, url_for, session
import boto3

app = Flask(__name__)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb',
                  aws_access_key_id="ASIAXYKJVXP7XFR52OAC",
                  aws_secret_access_key="W8ham5wzpKONmS6K8gIyrQsTkeWaLesMgknSAjkc",
                  aws_session_token=r"IQoJb3JpZ2luX2VjENn//////////wEaCXVzLXdlc3QtMiJHMEUCIBeV97QenR0P/3ikPjbdjYe9++s66cAz5Jz4z9NvXPh9AiEAo+Qp83sMMe37iYliMfKnBOqnL4W1CG8rrQfWoNBPEwUqtgIIEhAAGgw1MzMyNjczMzIwOTUiDDM6cQJTADMlCydLWyqTAut2XrUac8fLF2UqvOI8sM7mijucNyDGF87io64GYGmcli/UhdiII6G4XzjADRP/y9CmjeGmXtdpyz2OUorX0SXzE7sgFHr0G05lXcAF8ewkS9HJjjngcLSRk+OKyuFWmCOZ6aOp/XahpGS/xcMnw/3MrGhxMLXbaFBrSJEsVGvp45hL3PlYsvQB2qOoTt63z/ONgUGwlwxAEcjKVimMDKUTiQQ/kTuzaxbIRU4XOEprdY3LwskGvI9UZnz1uJYVI3KxXfkOb2Ai/n5nNY2O5A6ZTb7YpNDRdV/c/JG3AYXrvUUga06mfSJnbDhoTnl7lzrP25xuYuzoh/d17L9tBM54i2XtbUO1Jryp2zP/dPxilUuvMIiF1LAGOp0B/4ov6ksC1oot/oKh9bqqIMv6R+KB/RtuBKe8jyT6XX54dxsWVBrSOhd2vtBdM7HWGcs/gq58FKej7g895rt9SM4KrtqMWbrX9fLNOdHiaXk1eBPiB4nLPcS4ZQTAtaBAXQibVsvltCkMxExsNg4zceJnr9i9ZcFlUd4o6HYJ1JRlOb/YH13OBBS/DWn7fHzAGHbKElIm3dnKUjgxig==",
                  region_name="us-east-1")
app.secret_key = 'dfdfdsfqeq3e2'

# DynamoDB table name
tableName = 'login'
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
            session['email'] = email

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
            return render_template('main.html', no_result_message=no_result_message, user_name=session['user_name'])
        
        return render_template('main.html', searched_music=searched_music, user_name=session['user_name'])
    
    # Get the logged-in user's email from the session
    email = session.get('email')
    
    # Retrieve subscribed music for the user from DynamoDB
    if email:
        subscribed_music = get_subscribed_music(email)
    else:
        subscribed_music = None
    
    return render_template('main.html', subscribed_music=subscribed_music, user_name=session.get('user_name'))


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

# Route for the subscribe action
@app.route('/subscribe', methods=['POST'])
def subscribe():
    # Get the logged-in user's email from the session
    email = session.get('email')
    title = request.form['title']

    # Check if the user is logged in
    if email:
        # Get the login table
        login_table = dynamodb.Table('login')
        
        # Update the login table to subscribe the user to the music
        response = login_table.update_item(
            Key={'email': email},
            UpdateExpression='ADD music_subscriptions :title',
            ExpressionAttributeValues={':title': {title}}
        )
        
        # Redirect the user back to the main page after subscribing
        return redirect(url_for('main_page'))
    else:
        # If user is not logged in, redirect to login page
        return redirect(url_for('login'))
    
# Route for removing subscription
@app.route('/remove_subscription', methods=['POST'])
def remove_subscription():
    # Get the logged-in user's email from the session
    email = session.get('email')
    title = request.form['title']

    # Check if the user is logged in
    if email:
        # Get the login table
        login_table = dynamodb.Table('login')
        
        # Update the login table to remove the music subscription
        response = login_table.update_item(
            Key={'email': email},
            UpdateExpression='DELETE music_subscriptions :title',
            ExpressionAttributeValues={':title': {title}}
        )
        
        # Redirect the user back to the main page after removing subscription
        return redirect(url_for('main_page'))
    else:
        # If user is not logged in, redirect to login page
        return redirect(url_for('login'))

# Function to retrieve subscribed music for a user from DynamoDB
def get_subscribed_music(email):
    # Get the login table
    login_table = dynamodb.Table('login')
    
    # Retrieve the user's record
    response = login_table.get_item(Key={'email': email})
    
    if 'Item' in response:
        # Check if the user has any subscribed music
        if 'music_subscriptions' in response['Item']:
            subscribed_music_titles = response['Item']['music_subscriptions']
            
            # Get the music details for the subscribed titles from the music table
            music_table = dynamodb.Table('music')
            subscribed_music = []
            for title in subscribed_music_titles:
                music_details = music_table.get_item(Key={'title': title})
                if 'Item' in music_details:
                    subscribed_music.append(music_details['Item'])
            
            return subscribed_music
    
    return None


if __name__ == '__main__':
    app.run(debug=True)
