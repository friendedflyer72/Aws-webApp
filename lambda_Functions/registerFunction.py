import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('login')

def lambda_handler(event, context):
    if 'email' in event and 'username' in event and 'password' in event:
        email = event['email']
        username = event['username']
        password = event['password']
        
        if email and username and password:
            if not email_exists(email):
                create_user(email, username, password)
                return {
                    "statusCode": 200,
                    "body": json.dumps({"message": "Registration successful. You can now login."}),
                    "headers": {
                        "Content-Type": "application/json"
                    }
                }
            else:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "The email already exists"}),
                    "headers": {
                        "Content-Type": "application/json"
                    }
                }
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields"}),
                "headers": {
                    "Content-Type": "application/json"
                }
            }
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid input format"}),
            "headers": {
                "Content-Type": "application/json"
            }
        }

def email_exists(email):
    response = table.get_item(Key={'email': email})
    return 'Item' in response

def create_user(email, username, password):
    table.put_item(
        Item={'email': email, 'user_name': username, 'password': password}
    )