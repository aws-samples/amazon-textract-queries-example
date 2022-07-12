import os
import boto3
import shared_constants as sc

def lambda_handler(event, context):
    # Do any further processing for rental-application here
    print(event)
    return { "status" : "OK" }