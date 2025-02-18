
import json
import boto3
import pytest
import hashlib
from moto import mock_aws
from src.sqs_publisher import SQSPublisher, SQSMessage


class TestSQSMessage:
    def test_to_json(self):
        message = SQSMessage(
            webPublicationDate="2022-10-21T14:06:14",
            webTitle=(
                "Gritters stopped by 200 cars double parked "
                "on Peak District road, says council"
            ),
            webUrl=(
                "https://www.theguardian.com/uk-news/2025/jan/11/"
                "gritters-stopped-by-200-cars-double-parked-on-"
                "peak-district-road-says-council"
            )
        )
        json_str = message.to_json()
        data = json.loads(json_str)
        expected = {
            "webPublicationDate": "2022-10-21T14:06:14",
            "webTitle": (
                "Gritters stopped by 200 cars double parked "
                "on Peak District road, says council"
            ),
            "webUrl": (
                "https://www.theguardian.com/uk-news/2025/jan/11/"
                "gritters-stopped-by-200-cars-double-parked-on-"
                "peak-district-road-says-council"
            )
        }
        assert data == expected


@pytest.fixture
def sqs_queue():
    with mock_aws():
        sqs = boto3.resource('sqs', region_name='eu-west-2')
        queue = sqs.create_queue(QueueName="test-queue")
        yield queue


@pytest.fixture
def sqs_publisher(monkeypatch, sqs_queue):
    monkeypatch.setenv("GUARDIAN_KEY", "ABCDEFG")
    monkeypatch.setenv("SQS_QUEUE_URL", sqs_queue.url)
    return SQSPublisher()


class TestSQSPublisher:
    def test_publish_message_success(self, sqs_publisher, sqs_queue):
        message = SQSMessage(
            webPublicationDate="2022-10-21T14:06:14",
            webTitle=(
                "Gritters stopped by 200 cars double parked "
                "on Peak District road, says council"
            ),
            webUrl=(
                "https://www.theguardian.com/uk-news/2025/jan/11/"
                "gritters-stopped-by-200-cars-double-parked-on-"
                "peak-district-road-says-council"
            )
        )
        response = sqs_publisher.publish_message(message)
        assert "MessageId" in response

    def test_publish_message_md5_success(self, monkeypatch, sqs_publisher):
        message = SQSMessage(
            webPublicationDate="2022-10-21T14:06:14",
            webTitle=(
                "Gritters stopped by 200 cars double parked "
                "on Peak District road, says council"
            ),
            webUrl=(
                "https://www.theguardian.com/uk-news/2025/jan/11/"
                "gritters-stopped-by-200-cars-double-parked-on-"
                "peak-district-road-says-council"
            )
        )
        message_body = message.to_json()
        expected_md5 = hashlib.md5(message_body.encode('utf-8')).hexdigest()

        def dummy_send_message(**kwargs):
            return {"MD5OfMessageBody": expected_md5, "MessageId": "12345"}

        monkeypatch.setattr(
            sqs_publisher._SQSPublisher__client,
            "send_message",
            dummy_send_message
        )

        response = sqs_publisher.publish_message(message)
        assert response["MessageId"] == "12345"
        assert response["MD5OfMessageBody"] == expected_md5

    def test_publish_message_md5_failure(self, monkeypatch, sqs_publisher):
        message = SQSMessage(
            webPublicationDate="2022-10-21T14:06:14",
            webTitle=(
                "Gritters stopped by 200 cars double parked "
                "on Peak District road, says council"
            ),
            webUrl=(
                "https://www.theguardian.com/uk-news/2025/jan/11/"
                "gritters-stopped-by-200-cars-double-parked-on-"
                "peak-district-road-says-council"
            )
        )
        message_body = message.to_json()
        expected_md5 = hashlib.md5(message_body.encode('utf-8')).hexdigest()

        def dummy_send_message(**kwargs):
            return {"MD5OfMessageBody": "wrong_md5", "MessageId": "12345"}

        monkeypatch.setattr(
            sqs_publisher._SQSPublisher__client,
            "send_message",
            dummy_send_message
        )

        with pytest.raises(
            Exception,
            match=f"MD5 mismatch: expected {expected_md5}, got wrong_md5"
        ):
            sqs_publisher.publish_message(message)
