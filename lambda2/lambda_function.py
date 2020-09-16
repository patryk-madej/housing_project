import json
import boto3

def lambda_handler(event, context):
    
    try:
        event['lat'], event['lng']=str(event['lat']),str(event['lng']) # turn big floats to strings for DynamoDB
    except:
        print()
    
    table = boto3.resource('dynamodb').Table('housing_wroclaw_coordinates')
    response = table.put_item(Item=event)
    
    return event
