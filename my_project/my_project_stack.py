from aws_cdk.aws_lambda_python_alpha import PythonFunction, PythonLayerVersion
import sys
sys.path.append('../')
from lambdas import shared_constants as sc
import os
from aws_cdk import (
    aws_lambda as _lambda,
    RemovalPolicy,
    aws_s3 as _s3,
    aws_s3_notifications,
    aws_iam as _iam,
    aws_stepfunctions as _sfn,
    aws_stepfunctions_tasks as _sfn_tasks,
    aws_sns as _sns,
    aws_sns_subscriptions as _sns_subscriptions,
    Duration, Stack
)
from constructs import Construct


class MyProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        # Here define a Lambda Layer 
        boto3_lambda_layer = PythonLayerVersion(
           self, 'Boto3LambdaLayer',
           entry='lambdas/newboto3',
           compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
           description='Boto3 Library'
        )

        lambdaEnv = {}
        comprehend_ep_arn = os.environ[sc.COMPREHEND_EP_ARN]
        lambdaEnv[sc.COMPREHEND_EP_ARN] = comprehend_ep_arn
        
        # create s3 input bucket
        s3InputBucket = _s3.Bucket(
            self, "s3InputBucket", auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY)
        
        # create s3 output bucket
        s3OutputBucket = _s3.Bucket(
            self, "s3OutputBucket", auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY)

        lambdaEnv[sc.INPUT_BKT] = s3InputBucket.bucket_name
        lambdaEnv[sc.OUTPUT_BKT] = s3OutputBucket.bucket_name
        
        # SNS topic to write to when text-detect is complete:
        detect_topic = _sns.Topic(self, "textDetectTopic")
        analyze_topic = _sns.Topic(self, "textAnalyzeTopic")
        lambdaEnv[sc.DETECT_TOPIC_ARN] = detect_topic.topic_arn
        lambdaEnv[sc.ANALYZE_TOPIC_ARN] = analyze_topic.topic_arn
        
        # permissions for Textract to publish on SNS topic 
        textract_role = _iam.Role(self, "TextractSNSPublishRole", 
            assumed_by=_iam.ServicePrincipal("textract.amazonaws.com"))
        textract_role.add_to_policy(
            _iam.PolicyStatement(actions=["sts:AssumeRole"],
                resources=["*"]))
        textract_role.add_to_policy(
            _iam.PolicyStatement(actions=["sns:Publish"],
                resources=[detect_topic.topic_arn]))
        textract_role.add_to_policy(
            _iam.PolicyStatement(actions=["sns:Publish"],
                resources=[analyze_topic.topic_arn]))
        
        lambdaEnv[sc.TEXTRACT_PUBLISH_ROLE] = textract_role.role_arn

        # lambda to trigger the text detection
        detect_lambda = _lambda.Function(self, 'detectLambda',
                                         handler='detect_function.lambda_handler',
                                         runtime=_lambda.Runtime.PYTHON_3_9,
                                         environment=lambdaEnv,
                                         code=_lambda.Code.from_asset('./lambdas'))
        detect_lambda.role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonTextractFullAccess"))
        s3InputBucket.grant_read(detect_lambda)
        s3OutputBucket.grant_read_write(detect_lambda)
        
        # watch detect-topic for post detection processing
        post_detect_lambda = _lambda.Function(self, 'postDetectLambda', 
                                              handler='post_detect.lambda_handler',
                                              runtime=_lambda.Runtime.PYTHON_3_9,
                                              environment=lambdaEnv,
                                              code=_lambda.Code.from_asset('./lambdas'))
        detect_topic.add_subscription(_sns_subscriptions.LambdaSubscription(post_detect_lambda));
        s3OutputBucket.grant_read_write(post_detect_lambda);

        # classify then analyze the document
        classify_lambda = _lambda.Function(self, 'classifyLambda',
                                         handler='classify_function.lambda_handler',
                                         runtime=_lambda.Runtime.PYTHON_3_9,
                                         environment=lambdaEnv,
                                         code=_lambda.Code.from_asset('./lambdas'))
        classify_lambda.role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonTextractFullAccess"))
        classify_lambda.role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name("ComprehendReadOnly"))
        s3OutputBucket.grant_read_write(classify_lambda)
        
        # analyze the document
        analyze_lambda = _lambda.Function(self, 'analyzeLambda',
                                         handler='analyze_function.lambda_handler',
                                         runtime=_lambda.Runtime.PYTHON_3_9,
                                         layers=[boto3_lambda_layer],
                                         environment=lambdaEnv,
                                         code=_lambda.Code.from_asset('./lambdas'))
        analyze_lambda.role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonTextractFullAccess"))
        s3InputBucket.grant_read(analyze_lambda)
        s3OutputBucket.grant_read_write(analyze_lambda)
        
        # watch analyze-topic for post analyze processing
        post_analyze_lambda = _lambda.Function(self, 'postAnalyzeLambda', 
                                              handler='post_analyze.lambda_handler',
                                              runtime=_lambda.Runtime.PYTHON_3_9,
                                              environment=lambdaEnv,
                                              code=_lambda.Code.from_asset('./lambdas'))
        analyze_topic.add_subscription(_sns_subscriptions.LambdaSubscription(post_analyze_lambda));
        s3OutputBucket.grant_read_write(post_analyze_lambda);
        
        process_payslip_l = _lambda.Function(self, 'processPayslip',
                                         handler='process_payslip.lambda_handler',
                                         runtime=_lambda.Runtime.PYTHON_3_9,
                                         environment=lambdaEnv,
                                         layers=[boto3_lambda_layer],
                                         code=_lambda.Code.from_asset('./lambdas'))
        process_payslip_l.role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonTextractFullAccess"))
        s3OutputBucket.grant_read_write(process_payslip_l)
        process_bank_l = _lambda.Function(self, 'processBank',
                                         handler='process_bank.lambda_handler',
                                         runtime=_lambda.Runtime.PYTHON_3_9,
                                         environment=lambdaEnv,
                                         layers=[boto3_lambda_layer],
                                         code=_lambda.Code.from_asset('./lambdas'))
        process_bank_l.role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonTextractFullAccess"))
        s3OutputBucket.grant_read_write(process_bank_l)
        process_application_l = _lambda.Function(self, 'processApplication',
                                         handler='process_application.lambda_handler',
                                         runtime=_lambda.Runtime.PYTHON_3_9,
                                         environment=lambdaEnv,
                                         layers=[boto3_lambda_layer],
                                         code=_lambda.Code.from_asset('./lambdas'))
        process_application_l.role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonTextractFullAccess"))
        s3OutputBucket.grant_read_write(process_application_l)
        
                                         
        # Step functions Definition
        detect_job = _sfn_tasks.LambdaInvoke(
            self, "Detect Job",
            lambda_function=detect_lambda,
            result_path="$.Detection",
            integration_pattern=_sfn.IntegrationPattern.WAIT_FOR_TASK_TOKEN,
            payload=_sfn.TaskInput.from_object({
                "token": _sfn.JsonPath.task_token,
                "input": _sfn.JsonPath.entire_payload}))

        classify_job = _sfn_tasks.LambdaInvoke(
            self, "Classify Job",
            lambda_function=classify_lambda,
            result_selector = {
                "classification.$":"$.Payload.classification"},
            result_path="$.Classify")

        analyze_job = _sfn_tasks.LambdaInvoke(
            self, "Analyze Job",
            lambda_function=analyze_lambda,
            integration_pattern=_sfn.IntegrationPattern.WAIT_FOR_TASK_TOKEN,
            payload=_sfn.TaskInput.from_object({
                "token": _sfn.JsonPath.task_token,
                "input": _sfn.JsonPath.entire_payload}),
            result_path="$.Analyze")
            
        fail_job = _sfn.Fail(
            self, "Fail",
            cause='AWS Batch Job Failed',
            error='DescribeJob returned FAILED')

        succeed_job = _sfn.Succeed(
            self, "Succeeded",
            comment='AWS Batch Job succeeded')

        process_payslip_task = _sfn_tasks.LambdaInvoke(
            self, "Process Payslip",
            lambda_function=process_payslip_l,
            result_selector = {
                "status.$":"$.Payload.status"
            },
            result_path="$.Process").next(succeed_job)
        
        process_bank_task = _sfn_tasks.LambdaInvoke(
            self, "Process Bank",
            lambda_function=process_bank_l,
            result_selector = {
                "status.$":"$.Payload.status"
            },
            result_path="$.Process").next(succeed_job)
            
        process_application_task = _sfn_tasks.LambdaInvoke(
            self, "Process Application",
            lambda_function=process_application_l,
            result_selector = {
                "status.$":"$.Payload.status"
            },
            result_path="$.Process").next(succeed_job)

        # Create Chain
        definition = detect_job.next(classify_job).next(
            _sfn.Choice(self, 'Known Document Type?')
                .when(_sfn.Condition.string_equals('$.Classify.classification', 'UNKNOWN'), fail_job)
                .otherwise(analyze_job))

        analyze_job.next(
            _sfn.Choice(self, 'Analyze Complete?')
                .when(_sfn.Condition.string_equals('$.Classify.classification', 'PAYSLIP'), process_payslip_task)
                .when(_sfn.Condition.string_equals('$.Classify.classification', 'BANK'), process_bank_task)
                .when(_sfn.Condition.string_equals('$.Classify.classification', 'APPLICATION'), process_application_task)
                .otherwise(fail_job))

        # Create the state machine
        sm = _sfn.StateMachine(
            self, "StateMachine",
            definition=definition,
            timeout=Duration.minutes(60),
        )
        lambdaEnv[sc.SF_SM_ARN] = sm.state_machine_arn
        
        # watch s3 input-bkt, function triggered at file upload
        s3_function = _lambda.Function(
            self, "s3_input_function",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="s3_input_handler.main",
            environment=lambdaEnv,
            code=_lambda.Code.from_asset("./lambdas"))
        
        # create s3 notification that triggers lambda function
        notification = aws_s3_notifications.LambdaDestination(s3_function)

        # assign notification for the s3 event type (ex: OBJECT_CREATED)
        # the corresponding lambda function will kick start the step function
        s3InputBucket.add_event_notification(_s3.EventType.OBJECT_CREATED, notification)
        
        sm.grant_start_execution(s3_function)
        sm.grant_task_response(post_detect_lambda)
        sm.grant_task_response(post_analyze_lambda)