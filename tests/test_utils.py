from datetime import date, datetime
import re
import pandas as pd
import pytest
from moto import mock_sns
import boto3
from freezegun import freeze_time
from pandas import Timestamp
from pandas.testing import assert_frame_equal

from app.utils import (
    get_birthday_arn,
    send_message_by_sns,
    build_birthday_df,
    get_next_birthday,
    match_string_for_message,
    previous_month,
)


@mock_sns
def test_get_birthday_arn_success():
    sns = boto3.client("sns", region_name="eu-west-1")
    sns.create_topic(Name="birthdays_v1")
    birthday_arn = get_birthday_arn(sns)
    re_pattern = r"arn:aws:sns:eu-west-1:[0-9]*:birthdays_v1"
    assert re.search(re_pattern, birthday_arn) is not None


@mock_sns
def test_get_birthday_arn_fail():
    sns = boto3.client("sns", region_name="eu-west-1")
    sns.create_topic(Name="nada")
    with pytest.raises(
        Exception, match='No Topic exists with the string "birthdays" in it'
    ):
        get_birthday_arn(sns)


@mock_sns
def test_send_message_by_sns():
    sns = boto3.client("sns", region_name="eu-west-1")
    response = sns.create_topic(Name="birthdays_v1")
    topicarn = response["TopicArn"]
    send_message_by_sns(sns, topicarn, "hello")


class TestMatchStringForMessage:
    def test_day_before(self):
        assert match_string_for_message("day_before_next_birthday") == "tomorrow"

    def test_month_before(self):
        assert match_string_for_message("month_before_next_birthday") == "in a month"

    def test_error(self):
        with pytest.raises(ValueError, match="hello is not a valid argument for value"):
            match_string_for_message("hello")


class TestBuildBdayDf:
    people = {
        "Harriet": {"dob": "1993-10-22"},
        "Jane": {"dob": "1995-05-13"},
    }

    @freeze_time("2021-12-28")  # mocks current date
    def test_correct_format(self):
        output_df = build_birthday_df(self.people)
        expected_df = pd.DataFrame(
            {
                "name": ["Harriet", "Jane"],
                "dob": [
                    Timestamp("1993-10-22 00:00:00"),
                    Timestamp("1995-05-13 00:00:00"),
                ],
                "next_birthday": [
                    date(2022, 10, 22),
                    date(2022, 5, 13),
                ],
                "day_before_next_birthday": [
                    date(2022, 10, 21),
                    date(2022, 5, 12),
                ],
                "month_before_next_birthday": [
                    date(2022, 9, 22),
                    date(2022, 4, 13),
                ],
            }
        )
        expected_df["dob"] = pd.to_datetime(expected_df["dob"])
        assert_frame_equal(output_df, expected_df)


class TestGetNextBirthday:
    @freeze_time("2021-12-28")  # mocks current date
    def test_get_next_birthday(self):
        # Test a birthday in next calendar year
        date = datetime.strptime("1995-07-20", "%Y-%m-%d")
        new_date = get_next_birthday(date)
        assert new_date == datetime.strptime("2022-07-20", "%Y-%m-%d").date()

        # Test a birthday in current calendar year
        date = datetime.strptime("1995-12-29", "%Y-%m-%d")
        new_date = get_next_birthday(date)
        assert new_date == datetime.strptime("2021-12-29", "%Y-%m-%d").date()


class TestPreviousMonth:
    def test_previous_month(self):
        # Test a date in the middle of the year
        date = datetime(2020, 5, 15)
        assert previous_month(date) == datetime(2020, 4, 15)

        # Test a date in January
        date = datetime(2020, 1, 31)
        assert previous_month(date) == datetime(2019, 12, 31)

        # Test a date on the first day of the month
        date = datetime(2020, 2, 1)
        assert previous_month(date) == datetime(2020, 1, 1)
