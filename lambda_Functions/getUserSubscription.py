import json
import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')

# Define the DynamoDB table name
music_table_name = 'music'

def lambda_handler(event, context):
    # Retrieve email from the event
    email = event.get('email')
    
    if not email:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Email is required."}),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    
    # Retrieve subscribed music for the user
    subscribed_music = get_subscribed_music(email)
    
    if subscribed_music:
        return {
            "statusCode": 200,
            "body": json.dumps({"subscribed_music": subscribed_music}),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "No subscribed music found for the user."}),
            "headers": {
                "Content-Type": "application/json"
            }
        }

def get_subscribed_music(email):
    # Get the DynamoDB table
    music_table = dynamodb.Table(music_table_name)
    
    # Query the table for subscribed music based on the user's email
    response = music_table.query(
        KeyConditionExpression='user_email = :email',
        ExpressionAttributeValues={
            ':email': email
        }
    )
    
    # Extract the subscribed music items from the response
    subscribed_music = [item for item in response.get('Items', [])]
    
    return subscribed_music