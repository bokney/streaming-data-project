
"""
Configuration file for environment variable access.
"""

import os
import logging
import threading
from typing import Optional
from dotenv import load_dotenv


load_dotenv()
logger = logging.getLogger(__name__)


class Config:
    """
    Singleton class for environment variable validation and access.

    This class loads environment variables from a .env file and ensures
    required variables are present, raising an :exc:`OSError` if any
    are missing. It implements the singleton pattern so only one
    instance exists across the whole application.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """
        Creates the instance if it does not already exist.
        Returns the singleton instance.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    logger.debug("Creating a new Config instance.")
                    cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    @property
    def guardian_api_key(self) -> str:
        """
        :returns: The Guardian API key.
        :rtype: str
        :raises OSError: If the 'GUARDIAN_KEY' environment variable
            is not set.
        """
        value = os.getenv("GUARDIAN_KEY")
        if value is None:
            logger.error(
                "Missing required environment variable: GUARDIAN_KEY"
            )
            raise OSError(
                "Missing required environment variable: GUARDIAN_KEY"
            )
        logger.debug("Guardian API key successfully retrieved.")
        return value

    @property
    def sqs_queue_url(self) -> str:
        """
        :returns: The SQS queue URL.
        :rtype: str
        :raises OSError: If the 'SQS_QUEUE_URL' environment variable
            is not set.
        """
        value = os.getenv("SQS_QUEUE_URL")
        if value is None:
            logger.error(
                "Missing required environment variable: SQS_QUEUE_URL"
            )
            raise OSError(
                "Missing required environment variable: SQS_QUEUE_URL"
            )
        logger.debug("SQS queue URL successfully retrieved.")
        return value

    @property
    def aws_region(self) -> Optional[str]:
        """
        :returns: The AWS region, or None if not set.
        :rtype: Optional[str]
        """
        value = os.getenv("AWS_REGION")
        if value:
            logger.debug("AWS region set to %s", value)
        else:
            logger.debug("No AWS region set.")
        return value
