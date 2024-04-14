import boto3
import json

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    email = event.get('email')
    title = event.get('title')
    
    if not email or not title:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Both email and title are required for removing subscription."}),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    
    if remove_subscription(email, title):
        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Successfully removed subscription of {email} to {title}."}),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": f"Failed to remove subscription of {email} to {title}. Subscription not found."}),
            "headers": {
                "Content-Type": "application/json"
            }
        }

def remove_subscription(email, title):
    login_table = dynamodb.Table('login')

    # Update the login table to remove the music subscription
    response = login_table.update_item(
        Key={'email': email},
        UpdateExpression='DELETE music_subscriptions :title',
        ExpressionAttributeValues={':title': {title}}
    )
    return True