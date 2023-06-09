from aws_cdk import (
    Duration,
    Stack,
    # aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_s3_notifications as s3_event,
    aws_events as events,
    aws_events_targets as targets,
)
import boto3
from constructs import Construct
from aws_cdk import aws_lambda as _lambda
eb_client = boto3.client('events')

class LambdaExcelParseCdkStack(Stack):


    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #Create S3 bucket with which triggers a message to the default eventbridge event bus when a new object is created
        #This is the bucket where the excel files are stored
        
        bucket = s3.Bucket(self, "LambdaExcelParseCdkBucket",
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            #turn on amazon eventbridge for this s3 bucket
            event_bridge_enabled=True,
            auto_delete_objects=False,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
            public_read_access=False
        )
     
        lambda_function = _lambda.Function(self, "LambdaExcelParseCdkFunction",
                                            runtime=_lambda.Runtime.PYTHON_3_10,
                                            description="Parse excel files and send a message to the eventbridge event bus",
                                            architecture=_lambda.Architecture.ARM_64,
                                            timeout=Duration.seconds(300),
                                            memory_size=1024,
                                            handler="lambda_excel_parse_cdk.lambda_handler",
                                            code=_lambda.Code.from_asset("lambda/lambda_excel_parse_cdk"),
                                            layers=[_lambda.LayerVersion.from_layer_version_arn(self, "pandas_layer", "arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python310-Arm64:2")]
        )
        #allow lambda_function to read object from s3 bucket
        bucket.grant_read(lambda_function)
        
        # add lambda target to eventbridge eventbus rule, only files that end in xlsx and xls
        rule = events.Rule(self, "excelrule",
            event_pattern=events.EventPattern(
                source=["aws.s3"],
                detail_type=["Object Created"],
                detail={
                    'object': {'key':[ { "suffix": ".xls" }, { "suffix": ".xlsx" } ]}
                }

            )   
        )
        rule.add_target(targets.LambdaFunction(lambda_function,
                                               retry_attempts=2,                                    
        ))              
                        