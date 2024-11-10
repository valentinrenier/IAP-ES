import boto3
import watchtower
import logging


def setup_logging():
    logger = logging.getLogger('my_app_logger')
    logger.setLevel(logging.INFO)

    cloudwatch_handler = watchtower.CloudWatchLogHandler(
        boto3_client=boto3.client('logs', region_name='us-east-1'),
        log_group="EC2_logs",
        stream_name="EC2_stream"
    )

    cloudwatch_handler.setLevel(logging.INFO)
    logger.addHandler(cloudwatch_handler)

    return logger

logger = setup_logging()