import os
import boto3
import shared_constants as sc

def lambda_handler(event, context):
    print(event)
    job_id = event['Analyze']['JobId']
    textract = boto3.client('textract')
    response = textract.get_document_analysis(JobId=job_id)
    print(response)
    
    # This is a big hack
    # perhaps use a hash to store query-result IDs, if speed becomes an issue
    for block in response['Blocks']:
        if block["BlockType"] == "QUERY":
            if 'Relationships' not in block.keys():
                continue
            print(block["Query"]["Text"])
            for result in response['Blocks']:
                if result["BlockType"] == "QUERY_RESULT":
                    if block['Relationships'][0]['Ids'][0] == result['Id']:
                        print(result['Text'] + "\n")
                        break;
    return { "status" : "OK" }