from flask import Flask, render_template, request, redirect, url_for, session
import boto3

app = Flask(__name__)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb',
                  aws_access_key_id="ASIAXYKJVXP7VN3N5OM5",
                  aws_secret_access_key="Q26Fo1iadd5hGMKqgtVKyNMsDemr350eT19Ssmbf",
                  aws_session_token=r"IQoJb3JpZ2luX2VjELn//////////wEaCXVzLXdlc3QtMiJIMEYCIQDXLgy5gFTk6lffpm+ko48PKfpVF/bAenSZ32UM9vka+wIhAKKmErOdqkbEomTrMiCblMQ2NpNI1dyhCT7LGY7+rO4CKr8CCOL//////////wEQABoMNTMzMjY3MzMyMDk1Igwr/c5GePFZm4DDB8kqkwK9kt0detNhRq4kobNIsKsppVm1srN7ILw6FyOhluDqhk05ZmyPe0bl18eXQRKblh2oJGgSociORsm7Sf6lUzfBhUSKZSPbuuqKBEe2NbARYuUIuQnLgr1duvRDsOHMH38lHEnxyuPZUjMjHvLbeu2dPl1LoiDD4vzocF7LZh+7vRJ0w0Bxm9Z+I8w33gmxsR188dswkuC/jSMA2sY/zqeo3xr7ZZKpVacgYK+zqK7q1D8f32AeAyIIlDhFL1wSG/j+Z16C6NZncFqSVke3r3yANqsKIFA18UX5HV8aON9j0zgcEPwFSYompFzLBtHO7WFebpTlI8HseNfWMp7J041NMnW1P8hDrQoaz4lapfcBpq8WuTCigM2wBjqcAcPHQFTUaGNZ8cwoQr9Ogt1+Jikmv66Yhnts+xrxySjchhbXV+HnFFqBpHOn7GWh295yow6s36UH/33sARg7xGtE7/SVIZoxJ4WqB65cP1/mM5b9WtXvF4wpYY+mkwJoPwQF6586YvdLpmzyf8jkekDwPBbqj8RcIznIMQmYwVTmpPSVbGB71hpf1/KVj3ipTnfin/aZkwW0hvahGQ==",
                  region_name="us-east-1")
app.secret_key = 'dfdfdsfqeq3e2'

# DynamoDB table name
tableName = 'login'

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
            return redirect(url_for('main_page'))
        else:
            error = 'Email or password is invalid'
    return render_template('login.html', error=error, success_message=success_message)

# Route for the main page
@app.route('/main')
def main_page():
    user_name = session.get('user_name')
    return render_template('main.html', user_name=user_name)

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