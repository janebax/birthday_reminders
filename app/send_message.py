"""Script that runs every day as scheduled by a Lambda and triggers a message"""
import boto3
import pandas as pd
from contacts import contacts
from loguru import logger
from utils import (
    build_birthday_df,
    get_birthday_arn,
    match_string_for_message,
    send_message_by_sns,
)


def send_message(region_name="eu-west-1"):
    """Sends a message to an SNS topic if a birthday occurs on the next day or the same day next
    month

    Args:
        region_name (string): Default value of "eu-west-1"
    """
    current_date = pd.Timestamp.today()

    sns_client = boto3.client("sns", region_name)
    birthday_arn = get_birthday_arn(sns_client)

    # Get list of birthdays and create columns with date a day before and a month before
    birthday_df = build_birthday_df(contacts)

    columns = ["day_before_next_birthday", "month_before_next_birthday"]
    for column_name in columns:
        message_date_text = match_string_for_message(column_name)
        for _, row in birthday_df.iterrows():
            if row[column_name] == current_date.date():
                person = row["name"]
                birthday_text = row["dob"]
                # Send message
                message = (
                    f"It is {person}'s Birthday {message_date_text}!,"
                    f" Their birthday is {birthday_text.date()}."
                )
                logger.info(f"Sending message: {message}")
                send_message_by_sns(sns_client, birthday_arn, message)
            else:
                logger.info(
                    f'No message sent relating to {column_name.replace("_"," ")} for {row["name"]}'
                )


if __name__ == "__main__":
    send_message()
