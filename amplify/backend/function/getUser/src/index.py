import json
import boto3
import os
from boto3.dynamodb.conditions import Key

def handler(event, context):
    table_name = 'users-anthony'
    dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
    table = dynamodb.Table(table_name)
    
    params = event.get('queryStringParameters') or {}

    user_id = params.get('id')
    if user_id:
        try:
            response = table.get_item(Key={'id': user_id})
            user = response.get('Item')
            if user:
                return {
                    'statusCode': 200,
                    'body': json.dumps(user)
                }
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': 'Utilisateur non trouvé'})
                }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }
    
    email = params.get('email')
    if email:
        try:
            response = table.query(
                IndexName='email-index',
                KeyConditionExpression=Key('email').eq(email)
            )
            items = response.get('Items')
            if items:
                return {
                    'statusCode': 200,
                    'body': json.dumps(items[0])  
                }
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': 'Utilisateur non trouvé'})
                }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }
    
    return {
        'statusCode': 400,
        'body': json.dumps({'error': 'Fournir un paramètre id ou email'})
    }
