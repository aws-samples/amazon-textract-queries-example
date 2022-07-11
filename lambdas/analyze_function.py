import os
import boto3
import shared_constants as sc

def get_task_token_path(key):
    prefix = sc.OUT_TASK_TOKEN_PREFIX
    return prefix + "/" + key + ".analyzeTaskToken";

def lookup_query_config(classification):
    if classification == "PAYSLIP":
        return sc.Payslip_Queries
    elif classification == "BANK":
        return sc.Bank_Queries
    elif classification == "APPLICATION":
        return sc.Application_Queries
    else:
        return []
            

# process a file upload
def process_record(rec, event):
    token = event['token']
    classification = event['input']['Classify']['classification']
    query_config = lookup_query_config(classification)
    print(query_config)
    input_bucket = rec['s3']['bucket']['name']
    input_file = rec['s3']['object']['key']
    request_id = rec['responseElements']['x-amz-request-id']
    analyze_arn = os.environ[sc.ANALYZE_TOPIC_ARN]
    analyze_role = os.environ[sc.TEXTRACT_PUBLISH_ROLE]
    output_bucket = os.environ[sc.OUTPUT_BKT]
    output_prefix = sc.OUT_ANALYZE_PREFIX
    
    client = boto3.client('textract')
    response = client.start_document_analysis(
        DocumentLocation={
            'S3Object': {
                'Bucket': input_bucket,
                'Name': input_file
            }
        },
        FeatureTypes=[
            'QUERIES'
        ],
        ClientRequestToken=request_id,
        NotificationChannel={
            'SNSTopicArn': analyze_arn,
            'RoleArn': analyze_role
        },
        OutputConfig={
            'S3Bucket': output_bucket,
            'S3Prefix': output_prefix
        },
        QueriesConfig={
            'Queries': query_config
        }
    )
    s3_client = boto3.client('s3')
    s3_client.put_object(Bucket=output_bucket, Key=get_task_token_path(input_file), Body=token);

# event handler
def lambda_handler(event, context):
    # lets just dump it
    print(event)
    
    for rec in event['input']['Records']:
        process_record(rec, event)
        
    return {"submit_status": "SUCCEEDED"}