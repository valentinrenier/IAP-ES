import boto3
import watchtower
import logging
from application import application

cloudwatch_handler = watchtower.CloudWatchLogHandler(
    boto3_client=boto3.client('logs', region_name='us-east-1'),
    log_group="EC2_logs",
    stream_name="EC2_stream"
)

cloudwatch_handler.setLevel(logging.INFO)
    
# Ajoutez le gestionnaire CloudWatch aux gestionnaires de logs Flask
application.logger.addHandler(cloudwatch_handler)
application.logger.setLevel(logging.INFO)