import os
import boto3
import shared_constants as sc
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_dump_path(key):
    prefix = sc.OUT_DUMP_PREFIX
    return prefix + "/" + key + ".dump.txt";

def lambda_handler(event, context):
    logger.info(event)
    output_bkt = os.environ[sc.OUTPUT_BKT]
    
    s3_obj_name = event['Detection']['DocumentLocation']['S3ObjectName']
    job_id = event['Detection']['JobId']
    textract = boto3.client('textract')
    response = textract.get_document_text_detection(JobId=job_id)
    
    # generate flat dump
    dump = ''
    for block in response['Blocks']:
        if block['BlockType'] == "LINE":
            dump = dump + block['Text'] + ' '
    logger.info(dump)
    
    # dump to S3
    s3 = boto3.client('s3')
    s3.put_object(Bucket=output_bkt, Key=get_dump_path(s3_obj_name), Body=dump);
    
    # do sync classify
    comprehend = boto3.client('comprehend')
    comprehend_arn = os.environ[sc.COMPREHEND_EP_ARN]
    response = comprehend.classify_document(Text=dump, EndpointArn=comprehend_arn)
    classification = 'UNKNOWN'
    if len(response['Classes']) > 0:
        name = response['Classes'][0]['Name']
        score = response['Classes'][0]['Score']
        if score > 0.5:
            classification = name
    
    logger.info(classification)
    return {"classification" : classification}