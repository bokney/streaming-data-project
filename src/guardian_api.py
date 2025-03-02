
"""
This module provides classes for representing Guardian articles and making
API requests to the Guardian content service.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List, Union
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
        :class:`datetime` object or string.
    :ivar webTitle: The title of the article.
    :ivar webUrl: The URL of the article on the web.
    :ivar apiUrl: The API URL for the article.
    :ivar isHosted: Flag indicating if the article is hosted on the Guardian
        servers.
    :ivar pillarId: The identifier of the pillar to which the article belongs.
    :ivar pillarName: The name of the pillar.
    :ivar body: The article body text in HTML format.
    """
    id: str
    type: str
    sectionId: str
    sectionName: str
    webPublicationDate: Union[datetime, str]
    webTitle: str
    webUrl: str
    apiUrl: str
    isHosted: bool
    pillarId: Optional[str] = None
    pillarName: Optional[str] = None
    body: Optional[str] = None

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

    @property
    def content_preview(self) -> Optional[str]:
        """
        Get a preview of the article's text content.

        This property returns the first 1000 characters of the article's body
        text, after stripping out all HTML tags using BeautifulSoup. If no
        body content is available, it returns ``None``.

        :return: A string containing up to the first 1000 characters of the
            article's plain text, or ``None`` if the body is not provided.
        """
        if self.body:
            soup = BeautifulSoup(self.body, "html.parser")
            content = soup.get_text(separator=" ").strip()
            return content[:1000].rsplit(" ", 1)[0]
        return None


class GuardianAPI:
    """
    Client for interacting with the Guardian content API.

    This class uses an API key retrieved from the environment to make
    requests to the Guardian API.
    """
    _config = Config()

    def __init__(self):
        """
        Initialize the GuardianAPI client.

        Loads configuration from the environment and sets up the required
        request headers.
        """
        self._headers = {
            "api-key": self._config.guardian_api_key,
            "format": "json"
        }

    @rate_limit(max_calls=50)
    @backoff(delay=2, retries=4)
    def get_content(
            self,
            query: str,
            date_from: Optional[datetime] = None,
            max_articles: int = 10
            ) -> List[GuardianArticle]:
        """
        Retrieve articles from the Guardian API matching the specified query.

        :param query: The search query string.
        :type query: str
        :param date_from: Optionally filter articles published from this date
            onward.
        :type date_from: Optional[datetime]
        :returns: A list of :class:`GuardianArticle` instances that match
            the query.
        :param max_articles: Maximum amount of articles to retireve. Defaults
            to 10.
        :type max_articles: int
        :rtype: List[GuardianArticle]
        :raises requests.exceptions.RequestException: If there is an error
            during the API request.
        """
        if max_articles <= 0:
            return []

        url = "https://content.guardianapis.com/search"

        params = {"q": query, "show-fields": "body"}
        if date_from:
            params["from-date"] = date_from.strftime("%Y-%m-%d")

        articles: List = []
        current_page = 1

        while len(articles) < max_articles:
            page_size = min(max_articles - len(articles), 50)
            params["page-size"] = str(page_size)
            params["page"] = str(current_page)

            try:
                response = requests.get(
                    url=url, headers=self._headers, params=params
                )
                response.raise_for_status()

            except requests.exceptions.RequestException as e:
                raise requests.exceptions.RequestException(
                    f"Error getting Guardian content: {e}"
                ) from e

            data = response.json()

            response_data = data.get("response")
            if response_data is None:
                raise ValueError(
                    "Invalid response structure: 'response' key not found."
                )

            if response_data.get("status") != "ok":
                raise ValueError(
                    "API returned a non-ok status: "
                    f"{response_data.get('status')}"
                )

            results = response_data.get("results")
            if results is None:
                raise ValueError(
                    "Invalid response structure: "
                    "'results' key not found in response."
                )

            if not results:
                break

            for item in results:
                fields = item.pop("fields", {})
                item["body"] = fields.get("body")
                articles.append(GuardianArticle(**item))
                if len(articles) >= max_articles:
                    break

            total_pages = response_data.get("pages")
            if total_pages is None or current_page >= total_pages:
                break

            current_page += 1

        return articles
