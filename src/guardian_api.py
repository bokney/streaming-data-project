
"""
This module provides classes for representing Guardian articles and making
API requests to the Guardian content service.
"""

import requests
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, List
from src.config import Config
from src.rate_control import backoff, rate_limit


@dataclass
class GuardianArticle:
    """
    Data class representing an article from the Guardian API.

    :ivar id: The unique identifier of the article.
    :ivar type: The type of the article.
    :ivar sectionId: The section identifier where the article belongs.
    :ivar sectionName: The name of the section.
    :ivar webPublicationDate: The publication date of the article as a
        :class:`datetime` object.
    :ivar webTitle: The title of the article.
    :ivar webUrl: The URL of the article on the web.
    :ivar apiUrl: The API URL for the article.
    :ivar isHosted: Flag indicating if the article is hosted on the Guardian
        servers.
    :ivar pillarId: The identifier of the pillar to which the article belongs.
    :ivar pillarName: The name of the pillar.
    """
    id: str
    type: str
    sectionId: str
    sectionName: str
    webPublicationDate: datetime
    webTitle: str
    webUrl: str
    apiUrl: str
    isHosted: bool
    pillarId: str = ""
    pillarName: str = ""

    def __post_init__(self):
        """
        Post-initialization validation.

        If the ``webPublicationDate`` is provided as a string, convert it to a
        :class:`datetime` object.
        """
        if isinstance(self.webPublicationDate, str):
            self.webPublicationDate = datetime.fromisoformat(
                self.webPublicationDate
            )


class GuardianAPI:
    """
    Client for interacting with the Guardian content API.

    This class uses an API key retrieved from the environment to make
    requests to the Guardian API.
    """
    __config: Config
    __headers: Dict

    def __init__(self):
        """
        Initialize the GuardianAPI client.

        Loads configuration from the environment and sets up the required
        request headers.
        """
        self.__config = Config()

        self.__headers = {
            "api-key": self.__config.guardian_api_key,
            "format": "json"
        }

    @rate_limit(max_calls=50)
    @backoff(delay=2, retries=4)
    def get_content(
            self,
            query: str,
            date_from: Optional[datetime] = None
            ) -> List[GuardianArticle]:
        """
        Retrieve articles from the Guardian API matching the specified query.

        :param query: The search query string.
        :param date_from: Optional; filter articles published from this date
            onward.
        :type date_from: Optional[datetime]
        :returns: A list of :class:`GuardianArticle` instances that match
            the query.
        :rtype: List[GuardianArticle]
        :raises requests.exceptions.RequestException: If there is an error
            during the API request.
        """
        url = "https://content.guardianapis.com/search?"
        params = {"q": query}
        if date_from:
            params["from-date"] = date_from.strftime("%Y-%m-%d")

        try:
            response = requests.get(
                url=url, headers=self.__headers, params=params
            )
            response.raise_for_status()

            articles = []
            for item in response.json()['response']['results']:
                articles.append(GuardianArticle(**item))

            return articles

        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(
                f"Error getting Guardian content: {e}"
            ) from e
