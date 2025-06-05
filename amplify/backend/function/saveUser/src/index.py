import json
import boto3
import uuid
from boto3.dynamodb.conditions import Key

def handler(event, context):
    print('received event:')
    print(event)

    if event.get('httpMethod') != "POST":
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Méthode non autorisée. Utilisez POST.'})
        }

    table_name = 'users-anthony'
    dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
    table = dynamodb.Table(table_name)

    try:
        data = json.loads(event.get('body', '{}'))
        name = data.get('name')
        email = data.get('email')

        if not name or not email:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Champs "name" et "email" obligatoires.'})
            }

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'JSON invalide.'})
        }

    try:
        response = table.query(
            IndexName='email-index',  
            KeyConditionExpression=Key('email').eq(email)
        )
        if response['Items']:
            return {
                'statusCode': 409,
                'body': json.dumps({'error': 'Email déjà utilisé.'})
            }
    except Exception as e:
        print(f"Erreur lors de la requête GSI DynamoDB: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Erreur lors de la vérification email.'})
        }

    try:
        table.put_item(
            Item={
                "id": str(uuid.uuid4()),
                "name": name,
                "email": email
            }
        )
        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'Utilisateur enregistré.'})
        }

    except Exception as e:
        print(f"Erreur lors de l'insertion: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Erreur lors de l\'enregistrement.'})
        }
