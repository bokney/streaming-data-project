
"""
Configuration file for environment variable access.
"""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """
    Singleton class for environment variable validation and access.

    This class loads environment variables from a .env file and ensures
    required varables are present, raising an :exc:`OSError` if any
    are missing. It implements the singleton pattern so only one
    instance exists across the whole application.
    """

    _instance = None

    def __new__(cls):
        """
        Creates the instance if it does not already exist.
        Returns the singleton instance.
        """
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            load_dotenv()
            cls._validate_env_vars()
        return cls._instance

    @classmethod
    def _validate_env_vars(cls):
        """
        Ensure required environment variables are present.

        Raises:
            OSError: If one or more required environment
            variables are missing.
        """
        required = ["GUARDIAN_KEY", "SQS_QUEUE_URL"]
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            raise OSError(
                f"Missing required environment variables: "
                f"{', '.join(missing)}"
            )

    @property
    def guardian_api_key(self) -> Optional[str]:
        """
        Return the Guardian API key.

        Returns:
            Optional[str]: The Guardian API key.
        """
        return os.getenv("GUARDIAN_KEY")

    @property
    def sqs_queue_url(self) -> Optional[str]:
        """
        Return the SQS queue URL.

        Returns:
            Optional[str]: The SQS queue URL.
        """
        return os.getenv("SQS_QUEUE_URL")

    @property
    def aws_region(self) -> Optional[str]:
        """
        Return the AWS region.

        Returns:
            Optional[str]: The AWS region, or None if not set.
        """
        return os.getenv("AWS_REGION")
