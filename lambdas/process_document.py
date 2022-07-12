import os
import boto3
import shared_constants as sc

def dump_to_s3(event, answers):
    output_bkt = os.environ[sc.OUTPUT_BKT]
    output_prefix = sc.OUT_ANSWERS_PREFIX
    key = event['Detection']['DocumentLocation']['S3ObjectName']
    s3_obj_name = output_prefix + "/" + key + ".txt"
    s3 = boto3.client('s3')
    s3.put_object(Bucket=output_bkt, Key=s3_obj_name, Body=answers);
    
def lambda_handler(event, context):
    print(event)
    job_id = event['Analyze']['JobId']
    textract = boto3.client('textract')
    response = textract.get_document_analysis(JobId=job_id)
    print(response)
    
    # FIXME: This is a big hack
    # perhaps use a hash-table on IDs to store query-result
    answers = ''
    for block in response['Blocks']:
        if block["BlockType"] == "QUERY":
            if 'Relationships' not in block.keys():
                continue
            print(block["Query"]["Text"])
            answers = answers + block["Query"]["Text"] + "|" + block["Query"]["Alias"] + "|"
            for result in response['Blocks']:
                if result["BlockType"] == "QUERY_RESULT":
                    if block['Relationships'][0]['Ids'][0] == result['Id']:
                        print(result['Text'] + "\n")
                        answers = answers + result['Text'] + "\n"
                        break;
    # dump to S3
    dump_to_s3(event, answers)
    return { "status" : "OK" }