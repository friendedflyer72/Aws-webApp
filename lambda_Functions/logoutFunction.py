import json

def lambda_handler(event, context):
    # Clear the user session
    session.clear()
    
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Logout successful."}),
        "headers": {
            "Content-Type": "application/json"
        }
    }