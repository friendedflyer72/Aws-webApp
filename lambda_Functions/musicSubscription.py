import boto3
import json

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    email = event.get('email')
    title = event.get('title')
    
    if not email or not title:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Both email and title are required for subscription."}),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    
    if subscribe_user_to_music(email, title):
        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Successfully subscribed {email} to {title}."}),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": f"Failed to subscribe {email} to {title}. Music or user not found."}),
            "headers": {
                "Content-Type": "application/json"
            }
        }

def subscribe_user_to_music(email, title):
    login_table = dynamodb.Table('login')

    # Update the login table to subscribe the user to the music
    response = login_table.update_item(
        Key={'email': email},
        UpdateExpression='ADD music_subscriptions :title',
        ExpressionAttributeValues={':title': {title}}
    )
    return True