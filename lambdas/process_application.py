import os
import boto3
import shared_constants as sc
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Do any further processing for rental-application here
    logger.info(event)
    return { "status" : "OK" }