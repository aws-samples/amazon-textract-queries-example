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
    
    # TODO: We only support certain file formats
    # Bail out for any non-supported formats
    
    response = stepFunction.start_execution(
        stateMachineArn=sm_arn,
        input = json.dumps(event, indent=4),
        name=context.aws_request_id
    )
    return {
        'statusCode': 200,
        'body': event
    }