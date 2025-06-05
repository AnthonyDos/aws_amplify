import json
import boto3
from decimal import Decimal
from datetime import datetime


table_name = 'cryptoPrices-anthony'
dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
table = dynamodb.Table(table_name)
s3 = boto3.client('s3')
bucket_name = 'crypto-export-anthonyf42c9-anthony'


def decimal_to_float(obj):
    if isinstance(obj, list):
        return [decimal_to_float(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    return obj

def handler(event, context):

    if event.get('httpMethod') != "GET":
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Méthode non autorisée. Utilisez GET.'})
        }

    response = table.scan()
    items = response['Items']
    cleaned = decimal_to_float(items)
    cleaned.sort(key=lambda x: x.get("name", ""))

    timestamp = datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")
    filename = f"exports/crypto_{timestamp}.json"

    file_content = json.dumps(cleaned, indent=2)

    s3.put_object(
        Bucket=bucket_name,
        Key=filename,
        Body=file_content,
        ContentType='application/json'
    )

    presigned_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': filename},
        ExpiresIn=3600
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'download_url': presigned_url}),
        'headers': {'Content-Type': 'application/json'}
    }
