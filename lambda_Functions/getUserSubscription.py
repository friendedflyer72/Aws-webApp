import boto3

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    email = event.get('email')

    if not email:
        return {
            "statusCode": 400,
            "body": "Email is required for fetching subscribed music.",
            "headers": {
                "Content-Type": "application/json"
            }
        }

    subscribed_music = get_subscribed_music(email)
    if subscribed_music:
        return {
            "statusCode": 200,
            "body": subscribed_music,
            "headers": {
                "Content-Type": "application/json"
            }
        }
    else:
        return {
            "statusCode": 404,
            "body": "No subscribed music found for the provided email.",
            "headers": {
                "Content-Type": "application/json"
            }
        }

def get_subscribed_music(email):
    login_table = dynamodb.Table('login')

    response = login_table.get_item(Key={'email': email})

    if 'Item' in response:
        if 'music_subscriptions' in response['Item']:
            subscribed_music_titles = response['Item']['music_subscriptions']
            music_table = dynamodb.Table('music')
            subscribed_music = []
            for title in subscribed_music_titles:
                music_details = music_table.get_item(Key={'title': title})
                if 'Item' in music_details:
                    subscribed_music.append(music_details['Item'])
            for music in subscribed_music:
                music = get_signed_url(music)
            return subscribed_music

    return None

def get_signed_url(music):
        # Create a new S3 client
    s3_client = boto3.client('s3')
    obj = music['img_url'].split("/")[-1]
    # Generate the signed URL
    signed_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': 's3960290', 'Key': obj},
        ExpiresIn=1000
    )

    music['img_url'] = signed_url
    return music