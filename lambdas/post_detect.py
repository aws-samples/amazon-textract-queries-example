import os
import boto3
import json
import shared_constants as sc

def get_task_token_path(key):
    prefix = sc.OUT_TASK_TOKEN_PREFIX
    return prefix + "/" + key + ".taskToken";

def process_record(record):
    stepFunction = boto3.client('stepfunctions')
    s3_client = boto3.resource('s3')
    msg = record['Sns']['Message']
    print(msg)
    msg_dict = json.loads(msg)
    bucket = msg_dict['DocumentLocation']['S3Bucket']
    key = msg_dict['DocumentLocation']['S3ObjectName']
    print("Completing detect for " + bucket + "/" + key)
    output_bkt = os.environ[sc.OUTPUT_BKT]
    output_key = get_task_token_path(key)
    s3_object = s3_client.Object(output_bkt,output_key)
    token = s3_object.get()['Body'].read().decode("utf-8") 
    print(token)
    status = msg_dict['Status']
    if status == "SUCCEEDED":
        print("Success, resume SFSM")
        response = stepFunction.send_task_success(taskToken=token,
                                                  output=msg)
    else:
        print("Failed with " + status + ", failing SFSM")
        response = stepFunction.send_task_failure(taskToken=token, 
                                                  error=status,
                                                  cause=msg)

def lambda_handler(event, context):
    print(event)
    for rec in event['Records']:
        process_record(rec)
    return event