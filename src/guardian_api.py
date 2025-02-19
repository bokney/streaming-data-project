
import requests
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, List
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

    def get_content(
            self,
            query: str,
            date_from: Optional[datetime] = None
            ) -> List[GuardianArticle]:
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
