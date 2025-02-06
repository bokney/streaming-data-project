
import os
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, UTC
from src.guardian_api import GuardianArticle, GuardianAPI


class TestGuardianApi:
    @pytest.fixture
    def guardian_api(self):
        with patch("os.path.exists", return_value=True):
            with patch("dotenv.load_dotenv", lambda *args, **kwargs: None):
                with patch.dict(
                    os.environ, {"GUARDIAN_KEY": "ABCDEFG"}, clear=True
                ):
                    yield GuardianAPI()

    @patch("os.path.exists", return_value=False)
    def test_missing_env_file(self, mock_exists):
        with pytest.raises(
            FileNotFoundError, match="Error! .env file is missing!"
        ):
            GuardianAPI()

    @patch("os.path.exists", return_value=True)
    @patch("src.guardian_api.dotenv_values", lambda *args, **kwargs: {})
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_key(self, mock_exists):
        with pytest.raises(
            ValueError, match="Error! GUARDIAN_KEY is missing!"
        ):
            GuardianAPI()

    @patch("src.guardian_api.requests.get")
    def test_get_content_successful(self, mock_requests_get, guardian_api):
        sample_response = {
            "response": {
                "status": "ok",
                "userTier": "developer",
                "total": 1,
                "startIndex": 1,
                "pageSize": 10,
                "currentPage": 1,
                "pages": 1,
                "orderBy": "newest",
                "results": [
                    {
                        "id": "world/2022/oct/21/"
                        "russia-ukraine-war-latest-what-we-know-on-day-"
                        "240-of-the-invasion",
                        "type": "article",
                        "sectionId": "world",
                        "sectionName": "World news",
                        "webPublicationDate": "2022-10-21T14:06:14Z",
                        "webTitle": "Russia-Ukraine war latest: "
                        "what we know on day 240 of the invasion",
                        "webUrl":
                        "https://www.theguardian.com/world/2022/oct/21/"
                        "russia-ukraine-war-latest-what-we-know-on-day-"
                        "240-of-the-invasion",
                        "apiUrl":
                        "https://content.guardianapis.com/"
                        "world/2022/oct/21/"
                        "russia-ukraine-war-latest-what-we-know-on-day-"
                        "240-of-the-invasion",
                        "isHosted": False,
                        "pillarId": "pillar/news",
                        "pillarName": "News"
                    }
                ]
            }
        }

        mock_response = MagicMock()
        mock_response.json.return_value = sample_response
        mock_requests_get.return_value = mock_response

        search_term = "War"
        articles = guardian_api.get_content(search_term)

        assert isinstance(articles, list)
        assert len(articles) == 1
        assert isinstance(articles[0], GuardianArticle)
        assert articles[0].id == (
            'world/2022/oct/21/russia-ukraine-war-latest-'
            'what-we-know-on-day-240-of-the-invasion'
        )
        assert articles[0].type == "article"
        assert articles[0].sectionId == "world"
        assert articles[0].webPublicationDate == datetime(
                2022, 10, 21, 14, 6, 14,
                tzinfo=UTC
        )

    @patch(
        "src.guardian_api.requests.get",
        side_effect=Exception()
    )
    def test_get_content_failure(self, mock_requests_get, guardian_api):
        search_term = "Test Query"
        with pytest.raises(Exception):
            guardian_api.get_content(search_term)
