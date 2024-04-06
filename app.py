from flask import Flask, render_template, request, redirect, url_for
import boto3

app = Flask(__name__)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb',
                  aws_access_key_id="ASIAXYKJVXP7X7P4VGAK",
                  aws_secret_access_key="kBu4lGMCX2IytpPjySIHGPw9696WZFiGfLoyifbi",
                  aws_session_token=r"IQoJb3JpZ2luX2VjEJX//////////wEaCXVzLXdlc3QtMiJHMEUCIBkzp/0gKoFIeePh5a7c7rANQwc6ELWG1lSdMijvgcz/AiEA8dpYZDxmyccvYlRVuYHnF0pVUv3o3plbFJfzgjZ5pWEqvwIIvv//////////ARAAGgw1MzMyNjczMzIwOTUiDAHLcdqM6tlafsUiRyqTAmcA8MklDTKVmhl6PgJfAcp80cfNHN0c5oKAkiKAw925NjtvsbnozbjX6SmblOrhZD25ygw/b32ucwWyF6NtgJKnmN01DVgN35DYa5n/9GGBCCwd0Va6re6p+1DqGKZrL1FcEwneXRQ48Qy0qep+6BDCfMGKIqArDVWyCEVYLROK+eaG3FpHKSoH/wYfXJbW8uENMTmLBNQxHplUdoZBn9NeWy5xWXWm6HISI9rbNdpoKsQkGq6Lhz+qS+xkFzw2JlyMjQyDTl0ZlV6vb1iGljN2XgkyHKxDTLHaUq9+DHucO5yP5NDCdi3FFxmKXQavkf2J5ei/RVIBwBvXkQK2IO6QFODCtNc+yhrVj/3WftsGBuxbMICTxbAGOp0BOWKGWHMhnA+MwNy+8teiWJrFJgpDpcXySEpfk4qp71Znox2HAT0KN9AQEhJ17vxeV687uG2W3Bjjbqb/ErS5NErHo4Tn7YbvTZfDD+tRMuPQRC/1NBynSJCgp4/uMikjT3lwKYnt6E7QNvOiReb/ud7zSJkAuNSjCp5EAA2XpYcaOhYw/y2rKkmlzOBT9+xrtokUoB/buqhGz+9SRA==",
                  region_name="us-east-1")

# DynamoDB table name
tableName = 'login'

# Route for the login page
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if validate_credentials(email, password):
            return redirect(url_for('main_page'))
        else:
            error = 'Email or password is invalid'
    return render_template('login.html', error=error)

# Route for the main page
@app.route('/main')
def main_page():
    return render_template('main.html')

# Function to validate user credentials
def validate_credentials(email, password):
    table = dynamodb.Table('login')
    response = table.get_item(Key={'email': email})
    if 'Item' in response:
        if response['Item']['password'] == password:
            return True
    return False

if __name__ == '__main__':
    app.run(debug=True)