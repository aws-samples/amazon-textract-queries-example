SF_SM_ARN = 'SF_SM_ARN'
INPUT_BKT = 'INPUT_BKT'
OUTPUT_BKT = 'OUTPUT_BKT'
DETECT_TOPIC_ARN = 'DETECT_TOPIC_ARN'
TEXTRACT_PUBLISH_ROLE = 'TEXTRACT_PUBLISH_ROLE'
ANALYZE_TOPIC_ARN = 'ANALYZE_TOPIC_ARN'
OUT_DETECT_PREFIX = '_detectText'
OUT_ANALYZE_PREFIX = '_analyzeText'
OUT_TASK_TOKEN_PREFIX = '_tasks'
OUT_DUMP_PREFIX ='_dump'
OUT_ANSWERS_PREFIX='_answers'
COMPREHEND_EP_ARN = 'COMPREHEND_EP_ARN'

SUPPORTED_FILES = [".pdf", ".png", ".jpg", ".jpeg", ".tiff"]

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
    },
    {
        "Text": "What is the monthly net pay",
        "Alias": "PAYSLIP_SALARY_MONTHLY"
    }
]

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
    },
    {
        "Text": "What is the period for the bank statement",
        "Alias": "BANK_STATEMENT_PERIOD"
    },
    {
        "Text": "What is the largest credit transaction in the statement",
        "Alias": "BANK_LARGEST_CREDIT"
    },
    {
        "Text": "What is the largest debit transaction in the statement",
        "Alias": "BANK_LARGEST_DEBIT"
    },
]

Application_Queries = [
    {
        "Text": "What is the name of the realestate company",
        "Alias": "APP_COMPANY_NAME"
    },
    {
        "Text": "What is the name of the applicant or the prospective tenant",
        "Alias": "APP_APPLICANT_NAME"
    },
    {
        "Text": "What is the monthly rental amount",
        "Alias": "APP_RENTAL_AMOUNT_MONTHLY"
    },
    {
        "Text": "What is the weekly rental amount",
        "Alias": "APP_RENTAL_AMOUNT_WEEKLY"
    },
    {
        "Text": "What is the address of the property",
        "Alias": "APP_PROPERTY_ADDRESS"
    },
    {
        "Text": "What is the appicants monthly net pay",
        "Alias": "PAYSLIP_SALARY_MONTHLY"
    },
]