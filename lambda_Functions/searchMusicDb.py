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
        filter_expressions.append('#t = :title')
        expression_attribute_values[':title'] = title
        expression_attribute_names['#t'] = 'title'
    if year:
        filter_expressions.append('#y = :year')
        expression_attribute_values[':year'] = year
        expression_attribute_names['#y'] = 'year'
    if artist:
        filter_expressions.append('#a = :artist')
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
    
    return response['Items']