
import os
import requests
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import List
from urllib.parse import quote
from dotenv import dotenv_values


class GuardianArticle(BaseModel):
    """
    Data model representing an article retrieved from The Guardian API.

    Attributes:
        id (str): The unique identifier for the article.
        type (str): The type of content (e.g. "article").
        sectionId (str): The identifier for the section to which the article
            belongs.
        sectionName (str): The name of the section.
        webPublicationDate (datetime): The publication date and time of the
            article.
        webTitle (str): The title of the article.
        webUrl (HttpUrl): The URL where the article is available on The
            Guardian's website.
        apiUrl (HttpUrl): The API endpoint URL for the article.
        isHosted (bool): Flag indicating whether the article is hosted on The
            Guardian's servers.
        pillarId (str): The identifier for the content pillar
            (e.g., "pillar/news").
        pillarName (str): The name of the content pillar.
    """
    id: str
    type: str
    sectionId: str
    sectionName: str
    webPublicationDate: datetime
    webTitle: str
    webUrl: HttpUrl
    apiUrl: HttpUrl
    isHosted: bool
    pillarId: str
    pillarName: str


class GuardianAPI:
    """
    Client for interacting with The Guardian Content API.

    Overview:
        The Guardian API provides access to a rich set of content including
        articles, tags, sections, and editions. This client focuses on the
        content endpoint ("/search"), which returns a paginated list of
        articles. By default, 10 entries per page are returned.

    API Details:
        - Accessing the API requires an API key named 'GUARDIAN_KEY', which
          must be stored in a '.env' file.
        - Endpoints support filtering with parameters such as query (q), tags,
          dates, and more.
        - The get_content() method retrieves content related to a given search
          term.

    Raises:
        FileNotFoundError: If the .env file is missing.
        ValueError: If the GUARDIAN_KEY is not found in either the environment
                    or the .env file.
    """

    __config: dict
    __headers: dict

    def __init__(self):
        env_path = ".env"
        if not os.path.exists(env_path):
            raise FileNotFoundError(f"Error! {env_path} file is missing!")

        self.__config = dotenv_values(env_path)

        if (
            not os.environ.get("GUARDIAN_KEY")
            and "GUARDIAN_KEY" not in self.__config
        ):
            raise ValueError("Error! GUARDIAN_KEY is missing!")

        self.__headers = {
            "api-key": self.__config.get("GUARDIAN_KEY"),
            "format": "json"
        }

    def get_content(self, query: str) -> List[GuardianArticle]:
        """
        Retrieve ... from Guardian API
        """
        url = "https://content.guardianapis.com/search?"
        url += "q=" + quote(string=query)

        try:
            response = requests.get(url=url, headers=self.__headers)

            articles = []
            for item in response.json()['response']['results']:
                articles.append(GuardianArticle(**item))

            return articles

        except Exception as e:
            raise e

    # def get_tags(self):
    #     pass

    # def get_sections(self):
    #     pass

    # def get_editions(self):
    #     pass

    # def get_single_item(self):
    #     pass


# api = GuardianAPI()
# content = api.get_content("Rushup Edge")
# for article in content:
#     print(article)
