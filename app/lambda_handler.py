"""Lambda handler to pass the function to an AWS lambda"""
from loguru import logger
from send_message import send_message


def lambda_handler(event, context):
    """Passes the send_message function to the AWS lambda

    Parameters
    ----------
    event : Dict
        The event dictionary. JSON.
    context : [type]
        Needed by AWS Lambda.
    """

    logger.info(f"Event: {event} passed to lambda function")
    logger.info(f"Context: {context} passed to lambda function")
    send_message()
    logger.info("Lambda function complete")
