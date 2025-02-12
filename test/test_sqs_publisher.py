
import os
import pytest
from unittest.mock import patch
from src.sqs_publisher import SQSPublisher


class TestSQSPublisher:
    @patch("os.path.exists", return_value=False)
    def test_missing_env_file(self, mock_exists):
        with pytest.raises(
            FileNotFoundError, match="Error! .env file is missing!"
        ):
            SQSPublisher()

    @patch("os.path.exists", return_value=True)
    @patch("src.sqs_publisher.dotenv_values", lambda *args, **kwargs: {})
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_key(self, mock_exists):
        with pytest.raises(
            ValueError, match="Error! SQS_QUEUE_URL is missing!"
        ):
            SQSPublisher()
