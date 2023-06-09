#create lambda handler
import boto3
import json
import pandas as pd

s3 = boto3.client('s3')

def lambda_handler(event, context):
    print(event)
    #parse event from new object on s3 with eventbridge source
    bucket = event['detail']['bucket']['name']
    key = event['detail']['object']['key']    
    obj = s3.get_object(Bucket=bucket, Key=key)
    #read object
    obj_content = obj['Body'].read()
    #Print first line of xlsx file with pandas library
    df = pd.read_excel(obj_content, sheet_name=0, header=0)
    #using pandas, convert xlsx to json
    df_json = df.to_json(orient='records')
    print(df_json)
    
    

    
    
    
    