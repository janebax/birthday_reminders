from unittest.mock import patch

import boto3


class TestSendMessageBySNS:
    def test_publish_called(self):
        sns_client = boto3.client("sns", region_name="{REGION}")
        with patch.object(boto3.client, "publish", return_value=None) as mock_method:
            send_message_by_sns(sns_client, "dummy_arn", "dummy_message")
        mock_method.assert_called_once_with("dummy_arn", "dummy_message")
