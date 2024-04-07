from flask import Flask, render_template, request, redirect, url_for
import boto3

app = Flask(__name__)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb',
                  aws_access_key_id="ASIAXYKJVXP7XAR4DYDX",
                  aws_secret_access_key="D3wmjSmzHVhVY466/0tZes4x6L4mhXu02HJzER/3",
                  aws_session_token=r"IQoJb3JpZ2luX2VjEKL//////////wEaCXVzLXdlc3QtMiJGMEQCIFbHKKQhATZ5WHR85nn9a3OUPROYeijhYEALU4RQuriwAiA3pza0uJBZQU/teJCVu32TKbZJql3I5P+uGm0FdSc09yq/AgjL//////////8BEAAaDDUzMzI2NzMzMjA5NSIMX340Yx9GlPeWSa7EKpMC1WCOmGInh+f+qIcXXRZRO70yWq7EnuYf/DqaDeVsti47XMsa5/llYKbEjGrqqfMlEmZF7uIcov3lblOS8z7SfwExTIlDT81pvIsJwBiTg10jvugMoVTdLvoxeGh/CrSpM0sOlxEvjKth4akBeNAT3TkGBz8seKAbDC3nKgGNfmgOtn36T75izh3QyuaXCHY12q/f258iNjN28VjWcigS1J0WkcEmBqeE4mIGxE0EVeQ1/vE2QlK7OoDXyO5i+HoRCjVfx6awEHu82m2EJ5eieMMCxiMaLeTgE28OvHSxuGTo0fmZEMMZAm/x91m3dSnmyrvASXwGk2sywvYOj/80mY/lM5w1w2kxzzIqfOwfviWudZww/+zHsAY6ngEOuuJEjGIjeIzoHbVYix2pCXbO+tVFSVaHqPuU8pOQvy3YIxdtVV14s3+3pcwxO+NsF7LWo20e1lwgOVpfoJJS7xTVdze7O4BdpN1XZSMhL6xV1o8kAndx7DsYdF92+W/Yfsybp8+kcgSt30x7+Ea7h68LES2IwF7HO8hRd20OfSmF9kvC2Iw7CEBiAL5+bl6Gr+5sibO9eRM01nzDsA==",
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