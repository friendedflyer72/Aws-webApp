import boto3
import json

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    title = event.get('title')
    year = event.get('year')
    artist = event.get('artist')
    
    searched_music = search_music_in_db(title, year, artist)
    
    if not searched_music:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "No music found based on the provided criteria."}),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    
    return {
        "statusCode": 200,
        "body": json.dumps({"searched_music": searched_music}),
        "headers": {
            "Content-Type": "application/json"
        }
    }

def search_music_in_db(title, year, artist):
    music_table = dynamodb.Table('music')
    filter_expressions = []
    expression_attribute_values = {}
    expression_attribute_names = {}
    
    if title:
        filter_expressions.append('contains(#t, :title)')
        expression_attribute_values[':title'] = title
        expression_attribute_names['#t'] = 'title'
    if year:
        filter_expressions.append('contains(#y, :year)')
        expression_attribute_values[':year'] = year
        expression_attribute_names['#y'] = 'year'
    if artist:
        filter_expressions.append('contains(#a, :artist)')
        expression_attribute_values[':artist'] = artist
        expression_attribute_names['#a'] = 'artist'
    
    filter_expression = ' AND '.join(filter_expressions)
    
    if not filter_expressions:
        return []
    
    response = music_table.scan(
        FilterExpression=filter_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values
    )
    
    musics = []
    
    for music in response['Items']:
        musics.append(get_signed_url(music))
    
    return musics
    
    
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