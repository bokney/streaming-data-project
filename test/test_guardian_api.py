
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, UTC
from src.guardian_api import GuardianArticle, GuardianAPI


class TestGuardianArticle:
    def test_post_init_date_conversion(self):
        article = GuardianArticle(
            id=(
                "uk-news/2025/jan/11/"
                "gritters-stopped-by-200-cars-double-parked-"
                "on-peak-district-road-says-council"
            ),
            type="article",
            sectionId="uk-news",
            sectionName="UK news",
            webPublicationDate="2025-01-11T13:04:13Z",
            webTitle=(
                "Gritters stopped by 200 cars double parked "
                "on Peak District road, says council"
            ),
            webUrl=(
                "https://www.theguardian.com/uk-news/2025/jan/11/"
                "gritters-stopped-by-200-cars-double-parked-on-"
                "peak-district-road-says-council"
            ),
            apiUrl=(
                "https://content.guardianapis.com/"
                "uk-news/2025/jan/11/"
                "gritters-stopped-by-200-cars-double-parked-on-"
                "peak-district-road-says-council"
            ),
            isHosted=False,
            pillarId="pillar/news",
            pillarName="News"
        )
        assert isinstance(article.webPublicationDate, datetime)
        expected_date = datetime.fromisoformat("2025-01-11T13:04:13Z")
        assert article.webPublicationDate == expected_date


@pytest.fixture
def guardian_api(monkeypatch):
    monkeypatch.setattr("os.path.exists", lambda _: True)
    monkeypatch.setattr("dotenv.load_dotenv", lambda *_, **__: None)
    monkeypatch.setenv("GUARDIAN_KEY", "ABCDEFG")
    monkeypatch.setenv("SQS_QUEUE_URL", "https://sqs.test.queue/url")
    monkeypatch.setenv("AWS_REGION", "eu-west-2")

    return GuardianAPI()


class TestGuardianAPI:
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
                        "id": (
                            "uk-news/2025/jan/11/"
                            "gritters-stopped-by-200-cars-double-parked-"
                            "on-peak-district-road-says-council"
                        ),
                        "type": "article",
                        "sectionId": "uk-news",
                        "sectionName": "UK news",
                        "webPublicationDate": "2025-01-11T13:04:13Z",
                        "webTitle": (
                            "Gritters stopped by 200 cars double parked "
                            "on Peak District road, says council"
                        ),
                        "webUrl": (
                            "https://www.theguardian.com/uk-news/2025/jan/11/"
                            "gritters-stopped-by-200-cars-double-parked-on-"
                            "peak-district-road-says-council"
                        ),
                        "apiUrl": (
                            "https://content.guardianapis.com/"
                            "uk-news/2025/jan/11/"
                            "gritters-stopped-by-200-cars-double-parked-on-"
                            "peak-district-road-says-council"
                        ),
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

        search_term = "Rushup Edge"
        articles = guardian_api.get_content(search_term)

        assert isinstance(articles, list)
        assert len(articles) == 1
        assert isinstance(articles[0], GuardianArticle)
        assert articles[0].id == (
            "uk-news/2025/jan/11/"
            "gritters-stopped-by-200-cars-double-parked-"
            "on-peak-district-road-says-council"
        )
        assert articles[0].type == "article"
        assert articles[0].sectionId == "uk-news"
        assert articles[0].webPublicationDate == datetime(
                2025, 1, 11, 13, 4, 13,
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
