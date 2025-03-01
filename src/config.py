
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

    @staticmethod
    def _get_env_var(var_name: str, required: bool = True) -> Optional[str]:
        """
        Retrieve an environment variable.
        Raises an error if required and missing.
        :param var_name: The name of the environment variable.
        :type var_name: str
        :param required: Whether the variable is mandatory.
        :type required: bool
        :returns: The environment variable value if found,
            or None if not required.
        :rtype: str | None
        :raises OSError: If a required environment variable is missing.
        """
        value = os.getenv(var_name)
        if required and value is None:
            raise OSError(
                f"Missing required environment variable: {var_name}"
            )
        return value

    @property
    def guardian_api_key(self) -> Optional[str]:
        """
        Return the Guardian API key.

        Returns:
            str: The Guardian API key.
        """
        return self._get_env_var("GUARDIAN_KEY")

    @property
    def sqs_queue_url(self) -> Optional[str]:
        """
        Return the SQS queue URL.

        Returns:
            str: The SQS queue URL.
        """
        return self._get_env_var("SQS_QUEUE_URL")

    @property
    def aws_region(self) -> Optional[str]:
        """
        Return the AWS region.

        Returns:
            Optional[str]: The AWS region, or None if not set.
        """
        return self._get_env_var("AWS_REGION", required=False)
