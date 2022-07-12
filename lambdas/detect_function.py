import os
import boto3
import shared_constants as sc
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_task_token_path(key):
    prefix = sc.OUT_TASK_TOKEN_PREFIX
    return prefix + "/" + key + ".taskToken";

# process a file upload
def process_record(rec, token):
    logger.info(__name__)
    logger.info(rec)
    input_bucket = rec['s3']['bucket']['name']
    input_file = rec['s3']['object']['key']
    request_id = rec['responseElements']['x-amz-request-id']
    detect_arn = os.environ[sc.DETECT_TOPIC_ARN]
    detect_role = os.environ[sc.TEXTRACT_PUBLISH_ROLE]
    output_bucket = os.environ[sc.OUTPUT_BKT]
    output_prefix = sc.OUT_DETECT_PREFIX
    
    client = boto3.client('textract')
    response = client.start_document_text_detection(
        DocumentLocation={
            'S3Object': {
                'Bucket': input_bucket,
                'Name': input_file
            }
        },
        ClientRequestToken=request_id,
        NotificationChannel={
            'SNSTopicArn': detect_arn,
            'RoleArn': detect_role
        },
        OutputConfig={
            'S3Bucket': output_bucket,
            'S3Prefix': output_prefix
        })
    s3_client = boto3.client('s3')
    s3_client.put_object(Bucket=output_bucket, Key=get_task_token_path(input_file), Body=token);

# event handler
def lambda_handler(event, context):
    # lets just dump it
    logger.info(event)
    
    for rec in event['input']['Records']:
        process_record(rec, event['token'])
        
    return {
        "submit_status": "SUCCEEDED",
    }