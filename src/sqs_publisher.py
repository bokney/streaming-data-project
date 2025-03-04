
"""
This module defines the SQSMessage data class for representing messages,
and the SQSPublisher class for sending messages to the SQS queue.
"""

import json
import boto3
import hashlib
import logging
from botocore.exceptions import ClientError
from dataclasses import dataclass, asdict
from src.config import Config

logger = logging.getLogger(__name__)


@dataclass
class SQSMessage:
    """
    Data class representing an SQS message.

    :ivar webPublicationDate: The publication date in string format.
    :ivar webTitle: The title of the web article.
    :ivar webUrl: The URL of the web article.
    :ivar content_preview: The first 1000 characters of the article.
    """
    webPublicationDate: str
    webTitle: str
    webUrl: str
    content_preview: str

    def to_json(self) -> str:
        """
        Convert the SQSMessage to a JSON-formatted string.

        :return: A JSON string representation of the SQSMessage.
        :rtype: str
        """
        return json.dumps(asdict(self), ensure_ascii=False, indent=4)


class SQSPublisher:
    """
    Publisher for sending messages to an AWS SQS queue.

    Uses AWS credentials and queue url from the environment.
    """
    _config = Config()

    def __init__(self) -> None:
        """
        Initialize the SQSPublisher.

        Loads the SQS queue URL and AWS region from the configuration and
        creates an SQS client using boto3.
        """
        self.queue_url = self._config.sqs_queue_url
        self.aws_region = self._config.aws_region

        self.__client = boto3.client(
            "sqs",
            region_name=self.aws_region or "eu-west-2"
        )
        logger.info(
            "SQSPublisher initialized with queue URL: %s and region: %s",
            self.queue_url, self.aws_region
        )

    def publish_message(self, message: SQSMessage) -> dict:
        """Publish a JSON-formatted message to the SQS queue.

        This method sends the message and verifies that the MD5 checksum of
        the message body matches the value returned in the response.

        :param message: The SQSMessage instance to be sent.
        :type message: SQSMessage
        :return: The response from the SQS send_message call.
        :rtype: dict
        :raises RuntimeError: If a client error occurs or an unexpected error
            is encountered during message sending.
        :raises Exception: If the MD5 checksum of the sent message does not
            match the expected value.
        """
        message_body = message.to_json()
        logger.debug(
            "Attempting to send SQS message with body: %s",
            message_body
        )

        try:
            response = self.__client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=message_body
            )
            logger.debug("Received response from SQS: %s", response)
        except ClientError as e:
            logger.exception(
                "Failed to send SQS message due to client error: %s", e
            )
            raise RuntimeError(
                f"Failed to send SQS message due to client error: {e}"
            ) from e
        except Exception as e:
            logger.exception(
                "Unexpected error sending SQS message: %s", e
            )
            raise RuntimeError(
                f"Unexpected error sending SQS message: {e}"
            ) from e

        calculated_md5 = hashlib.md5(message_body.encode('utf-8')).hexdigest()
        response_md5 = response.get("MD5OfMessageBody")
        if response_md5 != calculated_md5:
            logger.error(
                "MD5 mismatch: expected %s, got %s",
                calculated_md5, response_md5
            )
            raise Exception(
                f"MD5 mismatch: expected {calculated_md5}, got {response_md5}."
            )

        logger.info(
            "Successfully published SQS message. MD5 checksum verified."
        )
        return response
