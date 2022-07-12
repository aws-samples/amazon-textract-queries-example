import os
import boto3
import json
import shared_constants as sc

def main(event, context):
    print(event)
    print(context)
    sm_arn = os.environ[sc.SF_SM_ARN]
    print(sm_arn)
    stepFunction = boto3.client('stepfunctions')
    
    # Bail out for any non-supported formats
    for rec in event['Records']:
        input_file = rec['s3']['object']['key']
        filename, file_extension = os.path.splitext(input_file)
        print ("filename: " + filename + ". extension: " + file_extension)
        if file_extension not in sc.SUPPORTED_FILES:
            print("Unsupported file type: " + input_file)
            return { 'statusCode': 200, 'body': event }
            
    response = stepFunction.start_execution(
        stateMachineArn=sm_arn,
        input = json.dumps(event, indent=4),
        name=context.aws_request_id
    )
    return {
        'statusCode': 200,
        'body': event
    }