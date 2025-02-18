
import json
import boto3
import hashlib
from botocore.exceptions import ClientError
from dataclasses import dataclass, asdict
from src.config import Config


class SQSPublishException(Exception):
    pass


@dataclass
class SQSMessage:
    webPublicationDate: str
    webTitle: str
    webUrl: str
    # content_preview: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=4)


class SQSPublisher:
    __config: Config

    def __init__(self):
        """
        Initializes the SQSPublisher.
        """
        self.__config = Config()
        self.queue_url = self.__config.sqs_queue_url
        self.__client = boto3.client("sqs")

    def publish_message(self, message: SQSMessage):
        """
        Publishes a JSON-formatted message to the SQS queue.
        Returns true if response MD5 is equal to MD5 of message body.
        """
        message_body = message.to_json()

        try:
            response = self.__client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=message_body
            )

        except ClientError as e:
            raise SQSPublishException(
                f"Failed to send SQS message due to client error: {e}"
            ) from e
        except Exception as e:
            raise SQSPublishException(
                f"Unexpected error sending SQS message: {e}"
            ) from e

        calculated_md5 = hashlib.md5(message_body.encode('utf-8')).hexdigest()
        response_md5 = response.get("MD5OfMessageBody")
        if response_md5 != calculated_md5:
            raise Exception(
                f"MD5 mismatch: expected {calculated_md5}, got {response_md5}."
            )

        return response
