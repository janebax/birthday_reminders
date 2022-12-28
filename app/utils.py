"""Utils needed for send_message.py"""
# pylint: disable=E1136,E1137
from datetime import datetime, timedelta

import boto3
import pandas as pd


def initialise_sns_and_get_birthday_arn():
    """
    Connect to AWS SNS service and identify the previously created 'birthday' Topic.
    """
    # Connect to SNS messaging service
    sns_client = boto3.client("sns", region_name="{REGION}")

    # Get the Arn for the birthfay topic
    topics = sns_client.list_topics()["Topics"]
    for topic in topics:
        if "birthdays" in topic["TopicArn"]:
            birthday_arn = topic["TopicArn"]

    return sns_client, birthday_arn


def send_message_by_sns(sns_client: boto3.client, arn: str, message: str):
    """Sends a message to a topic given a TopicArn

    Args:
        sns_client (boto3.client): client to handle requests for SNS
        arn (string): SNS topic to send the message to
        message (string): message to publish to the topic
    """
    sns_client.publish(
        TopicArn=arn,
        # Set subject and message
        Message=message,
    )


def match_string_for_message(value: str):
    """Provides correct string for text message"""
    if value == "day_before_next_birthday":
        return "tomorrow"
    if value == "month_before_next_birthday":
        return "in a month"
    raise ValueError(f"{value} is not a valid argument for value")


def build_birthday_df(contacts: dict):
    """
    Returns a dataframe containing birthday information and dates to check for text alerts.

    Args:
        contacts (dict): Dictionary with names as keys, with values as nested attributes related
          to the person. E.g. {"Harriet": {"dob": "1993-01-15"}}

    Returns:
        pd.DataFrame: Dataframe with a row for each name, dob, next birthday, day before next
          birthday and month before next birthday
    """
    bday_df = pd.DataFrame.from_dict(contacts, orient="index").reset_index(names="name")
    bday_df["dob"] = pd.to_datetime(bday_df["dob"])
    bday_df["next_birthday"] = bday_df.apply(
        lambda row: get_next_birthday(row["dob"]), axis=1
    )
    bday_df["day_before_next_birthday"] = bday_df.apply(
        lambda row: row["next_birthday"] - timedelta(days=1), axis=1
    )
    bday_df["month_before_next_birthday"] = bday_df.apply(
        lambda row: previous_month(row["next_birthday"]), axis=1
    )
    return bday_df


def get_next_birthday(birthdate: datetime) -> str:
    """
    Returns the next birthday as a string in the format "YYYY-MM-DD"

    Args:
        birthdate (datetime.datetime: the birthdate in the format "YYYY-MM-DD"

    Returns:
        datetime.datetime: the next birthday in the format "YYYY-MM-DD"
    """

    # Convert the birthdate TimeStamp to a datetime object
    birthday = birthdate.date()
    today = datetime.now()

    # If the birthday hasn't passed yet this year, set the year to this year
    if birthday.month < today.month or (
        birthday.month == today.month and birthday.day < today.day
    ):
        birthday = birthday.replace(year=today.year + 1)
    else:
        # If the birthday hasn't passed yet this year, set the year to this year
        birthday = birthday.replace(year=today.year)

    return birthday


def previous_month(date):
    """Returns the date a month before the given date.

    Args:
        date (datetime.datetime): The date to get the previous month for.

    Returns:
        datetime.datetime: The date a month before the given date.
    """
    # If the given date is in the first month of the year (January),
    # we need to handle the case where we need to go back to the previous year.
    if date.month == 1:
        return date.replace(year=date.year - 1, month=12)
    return date.replace(month=date.month - 1)
