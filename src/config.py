
"""
Configuration file for environment variable access.
"""

import os
import threading
from typing import Optional
from dotenv import load_dotenv


load_dotenv()


class Config:
    """
    Singleton class for environment variable validation and access.

    This class loads environment variables from a .env file and ensures
    required varables are present, raising an :exc:`OSError` if any
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
                    cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    @property
    def guardian_api_key(self) -> str:
        """
        Return the Guardian API key.

        Returns:
            str: The Guardian API key.
        """
        value = os.getenv("GUARDIAN_KEY")
        if value is None:
            raise OSError(
                "Missing required environment variable: GUARDIAN_KEY"
            )
        return value

    @property
    def sqs_queue_url(self) -> str:
        """
        Return the SQS queue URL.

        Returns:
            str: The SQS queue URL.
        """
        value = os.getenv("SQS_QUEUE_URL")
        if value is None:
            raise OSError(
                "Missing required environment variable: SQS_QUEUE_URL"
            )
        return value

    @property
    def aws_region(self) -> Optional[str]:
        """
        Return the AWS region.

        Returns:
            Optional[str]: The AWS region, or None if not set.
        """
        return os.getenv("AWS_REGION")
