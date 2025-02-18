
import requests
from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass
from src.config import Config


@dataclass
class GuardianArticle:
    id: str
    type: str
    sectionId: str
    sectionName: str
    webPublicationDate: datetime
    webTitle: str
    webUrl: str
    apiUrl: str
    isHosted: bool
    pillarId: str
    pillarName: str

    def __post_init__(self):
        if isinstance(self.webPublicationDate, str):
            self.webPublicationDate = datetime.fromisoformat(
                self.webPublicationDate
            )


class GuardianAPI:
    __config: Config
    __headers: Dict

    def __init__(self):
        self.__config = Config()

        self.__headers = {
            "api-key": self.__config.guardian_api_key,
            "format": "json"
        }

    def get_content(self, query: str) -> List[GuardianArticle]:
        url = "https://content.guardianapis.com/search?"
        params = {"q": query}

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
