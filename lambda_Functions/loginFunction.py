import boto3
import json

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    email = event['email']
    password = event['password']

    if not email or not password:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Both email and password are required for login."}),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    user = validate_credentials(email, password)
    if user:
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Login successful.", "user": user}),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    else:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Invalid email or password."}),
            "headers": {
                "Content-Type": "application/json"
            }
        }

def validate_credentials(email, password):
    # Retrieve user record from DynamoDB based on email
    table = dynamodb.Table('login')
    response = table.get_item(Key={'email': email})

    if 'Item' in response:
        # Check if the provided password matches the stored password
        if response['Item']['password'] == password:
            return response['Item']

    return False