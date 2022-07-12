## AWS Sample: Textract Queries driven intelligent document processing

This repository serves as a sample/example of intelligent document processing using AWS AI services. It covers the following:
1. Setup the example in your AWS account using Infrastructure as Code (IaC) - Cloud Development Kit (CDK)
2. The example uses fully managed serverless components - offloading undifferentiated heavy lifting
3. It uses Textract AI service to extract data from uploaded multi-page documents such as PDFs, images, tables, and forms
3. Classifies documents using custom classification model in the Comprehend AI service (for example PAYSLIP, BANK statement, Rental APPLICATION)
4. Based on the classification, ask a set of questions in natural language to extract key information. For example, in the case of PAYSLIP:
```
       Q. "What is the company's name"
       Q. "What is the company's ABN number"
       Q. "What is the employee's name"
       Q. "What is the annual salary"
       Q. "What is the monthly net pay"
```
5. The example is automatically trigger when a file is uploaded to the designated S3 bucket.
6. It is asynchronous and orchestrated using Step Functions - allowing for documents to be processed in parallel.
7. Both the IaC CDK script and the Lambda handlers are written in Python, making it easy to follow/change/adapt for your needs.

## Getting Started
1. It is recommended to use a Cloud9 environment as it comes bundled with AWS CLI and CDK pre-installed
2. Increase the size of the EBS volume attached to Cloud9 EC2 instance to 20GiB

Once the Cloud9 environment is setup as above, clone the repository:
```
'git clone https://github.com/aws-samples/amazon-textract-queries-example.git'
```
Setup a virtual environment so that all python dependencies are stored within the project directory:
```
Admin:~/environment/amazon-textract-queries-example (main) $ virtualenv .venv
Admin:~/environment/amazon-textract-queries-example (main) $ source .venv/bin/activate
(.venv) Admin:~/environment/amazon-textract-queries-example (main) $ pip install -r requirements.txt
```
To use the newly released Textract Queries feature, we need the bundled Lambda functions to use a new version of Python boto3 library, so install that:
```
(.venv) Admin:~/environment/amazon-textract-queries-example (main) $ pip install boto3 --target=lambdas/newboto3
```

## Train a sample classifier

Now we train a custom classification model in Comprehend. There are 3 sample files provided (payslip, bank-statement and rental-application):
```
(.venv) Admin:~/environment/amazon-textract-queries-example (main) $ ls training
bank-statement.pdf  payslip.pdf  rental-application.pdf  trainer.csv
```
The text from these files has been extracted and placed as a flattened single-line string along with its corresponding label in "trainer.csv". Lines have been duplicated in "trainer.csv" to have minimum entries required to train the model.

To train the classifier:
1. Visit the [Comprehend console](https://console.aws.amazon.com/comprehend/v2/home#classification) (switch to the region you wish to use)
2. Click *Train classifier*
3. Give it a name and check the other details (the defaults are fine to start - use a Multi-class classifier)
4. Specify the S3 location of the training file (upload it first)
5. Click *Train classifier*

Once it's trained (it will take a few minutes), start an endpoint by clicking *Create endpoint* from the classifier's console page. Note the ARN of the endpoint. Export it into your environment using the following variable:
```
(.venv) Admin:~/environment/amazon-textract-queries-example (main) $ export COMPREHEND_EP_ARN=arn:aws:comprehend:ap-southeast-2:NNNNNNNNNNNN:document-classifier-endpoint/classify-ep
```

## Deploy the Sample

We will be using CDK to deploy the application into your account. This is done using two simple commands:
```
1. (.venv) Admin:~/environment/amazon-textract-queries-example (main) $ cdk bootstrap
2. (.venv) Admin:~/environment/amazon-textract-queries-example (main) $ cdk deploy
```
Note that `cdk bootstrap` is required just once for your AWS account. After subsequent changes to the  logic or IaC doing `cdk deploy` is sufficient.

## Processing PDF files

After deployment is complete (typically 4 - 5 minutes) and the status of the Comprehend classification endpoint is "Active" upload one of the provided sample PDF (example `payslip.pdf`) files into the input S3 bucket (`myprojectstack-s3inputbucketNNNNN`) that has been created by CDK.

The set of questions that will be asked against a given document can be inspected here:
```
(.venv) Admin:~/environment/amazon-textract-queries-example (main) $ grep -A 15 Payslip_Queries lambdas/shared_constants.py
Payslip_Queries = [
    {
        "Text": "What is the company's name",
        "Alias": "PAYSLIP_NAME_COMPANY"
    },
    {
        "Text": "What is the company's ABN number",
        "Alias": "PAYSLIP_COMPANY_ABN"
    },
    {
        "Text": "What is the employee's name",
        "Alias": "PAYSLIP_NAME_EMPLOYEE"
    },
    {
        "Text": "What is the annual salary",
        "Alias": "PAYSLIP_SALARY_ANNUAL"

(.venv) Admin:~/environment/amazon-textract-queries-example (main) $ grep -A 15 Bank_Queries lambdas/shared_constants.py
Bank_Queries = [
    {
        "Text": "What is the name of the banking institution",
        "Alias": "BANK_NAME"
    },
    {
        "Text": "What is the name of the account holder",
        "Alias": "BANK_HOLDER_NAME"
    },
    {
        "Text": "What is the account number",
        "Alias": "BANK_ACCOUNT_NUMBER"
    },
    {
        "Text": "What is the current balance of the bank account",
        "Alias": "BANK_ACCOUNT_BALANCE"
```
When you upload the PDF a [Step Functions](https://console.aws.amazon.com/states/home) will be triggered. View that to see the flow of the document and the [CloudWatch](https://console.aws.amazon.com/cloudwatch/home) Log groups for the Lambda logs.

The answers to the questions for a given document will show up in the output S3 bucket (`myprojectstack-s3outputbucketNNNNN`) under the "_answers" folder when the corresponding Step Function is complete.

The Step Functions flow that has been executed is depicted below:
![Step Functions flow](/assets/images/step-function-flow.png)

Now you have successfully run the sample of a scalable, serverless application stack using CDK as IaC to intelligently get answers from a document for your questions expressed in natural language.

## Resources and pricing

Note that for as long as you have the stack deployed, charges may apply to your account. You should delete the resources when you are done with the sample. WARNING all the files in the S3 input (`myprojectstack-s3inputbucketNNNNN`) and output (`myprojectstack-s3outputbucketNNNNN`) buckets will be automatically deleted:
```
(.venv) Admin:~/environment/amazon-textract-queries-example (main) $ cdk destroy
```
You will also need to manually terminate the Comprehend endpoint and delete the Comprehend classifier. Also the Cloud9 environment if that was used to run through the sample.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

