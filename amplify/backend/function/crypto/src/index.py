import json
import requests
import boto3
from datetime import datetime
from decimal import Decimal

def handler(event, context):
    table_name = 'cryptoPrices-anthony'
    dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
    table = dynamodb.Table(table_name)
    print('Received event:')
    print(event)

    #url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin"
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=50&page=1"

    headers = {
        "accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    timestamp = datetime.utcnow().isoformat()

    for coin in data:
        print(f"Inserting coin: {coin['name']}")
        table.put_item(
            Item={
                "crypto_id": coin["id"],
                "timestamp": timestamp,
                "name": coin["name"],
                "symbol": coin["symbol"],
                "price": Decimal(str(coin["current_price"])) 
            }
        )

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(data)
    }
