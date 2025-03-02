
import time
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, UTC
from src.guardian_api import GuardianArticle, GuardianAPI


@pytest.fixture(autouse=True)
def disable_sleep(monkeypatch):
    monkeypatch.setattr(time, 'sleep', lambda _: None)


class TestGuardianArticle:
    def test_article_field_types(self):
        article = GuardianArticle(
            id="test-id",
            type="article",
            sectionId="uk-news",
            sectionName="UK News",
            webPublicationDate="2025-01-01T00:00:00Z",
            webTitle="Test Title",
            webUrl="https://www.theguardian.com",
            apiUrl="https://content.guardianapis.com",
            isHosted=False,
            pillarId="pillar/news",
            pillarName="News",
            body="<p>Test</p>"
        )

        assert isinstance(article.id, str)
        assert isinstance(article.type, str)
        assert isinstance(article.sectionId, str)
        assert isinstance(article.sectionName, str)
        assert isinstance(article.webPublicationDate, datetime)
        assert isinstance(article.webTitle, str)
        assert isinstance(article.webUrl, str)
        assert isinstance(article.apiUrl, str)
        assert isinstance(article.isHosted, bool)
        assert isinstance(article.pillarId, str)
        assert isinstance(article.pillarName, str)
        assert isinstance(article.body, str)
        assert isinstance(article.content_preview, str)

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
            pillarName="News",
            body="<p>Test</p>"
        )
        assert isinstance(article.webPublicationDate, datetime)
        expected_date = datetime.fromisoformat("2025-01-11T13:04:13Z")
        assert article.webPublicationDate == expected_date

    def test_content_preview(self):
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
            pillarName="News",
            body=(
                "<p>Gritting crews have been stopped in their tracks "
                "by “about 200 cars” double parked on a road along the "
                "Peak District.</p> <p>Derbyshire county council said crews "
                "were prevented from gritting the roads on Saturday morning "
                "due to parking on both sides of road at Rushup Edge and Mam "
                "Nick near Edale.</p> <p>In a post on X, the council said: "
                "“We have issues with cars double parked on Rushup Edge and "
                "Man [m] Nick on the road down to Edale. Our gritters cannot "
                "get through with around 200 cars in the area. Please move "
                "your car if you are in the area. If we can’t get through "
                "neither would a bus or fire engine. Thanks.”</p> <p>The "
                "council asked drivers “not to add to the problems on these "
                "roads”.</p> <p>A statement added: “We realise that people "
                "want to enjoy the Peak District, but this level of parking "
                "is making the gritters’ job very difficult.”</p> <p>"
                "Freezing temperatures coupled with snowfall have led to "
                "disruption on the roads around north Derbyshire all week."
                "</p> <p>Roads shut in Derbyshire include Goyts Lane near "
                "Buxton, Rylah Hill in Palterton, Back Lane in Youlgrave "
                "and Curbar Lane, Curbar.</p> <p>Earlier this week, "
                "Derbyshire county council warned drivers in parts of the "
                "county not to venture out after closing more than 20 "
                "roads: “Take care if you are travelling on the roads, and "
                "remember never to drive into flood water or through road "
                "closure signs which are there for your safety.</p> <p>"
                "“We’ll continue to monitor the weather conditions and "
                "we’ll do our very best to keep Derbyshire moving.”</p>"
            )
        )

        expected_text = "Gritting crews have been stopped in their tracks"

        preview = article.content_preview

        assert preview is not None
        assert preview.startswith(expected_text)
        assert len(preview) <= 1000


@pytest.fixture
def guardian_api(monkeypatch):
    monkeypatch.setattr("os.path.exists", lambda _: True)
    monkeypatch.setattr("dotenv.load_dotenv", lambda *_, **__: None)
    monkeypatch.setenv("GUARDIAN_KEY", "ABCDEFG")
    monkeypatch.setenv("SQS_QUEUE_URL", "https://sqs.test.queue/url")
    monkeypatch.setenv("AWS_REGION", "eu-west-2")

    return GuardianAPI()


class TestGuardianAPI:
    def _make_article(self, i):
        return {
            "id": f"article-{i}",
            "type": "article",
            "sectionId": "uk-news",
            "sectionName": "UK news",
            "webPublicationDate": "2025-01-01T00:00:00Z",
            "webTitle": f"Title {i}",
            "webUrl": "https://www.theguardian.com/article-{i}",
            "apiUrl": "https://content.guardianapis.com/article-{i}",
            "isHosted": False,
            "pillarId": "pillar",
            "pillarName": "Pillar"
        }
    
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

        search_term = '"Rushup Edge"'
        date_from = datetime(2022, 12, 25, 15, 30)
        date_to = datetime(2025, 2, 1)

        articles = guardian_api.get_content(search_term, date_from, date_to)

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
        called_params = mock_requests_get.call_args[1].get("params", {})
        assert called_params.get("q") == search_term
        assert called_params.get("from-date") == "2022-12-25"
        assert called_params.get("to-date") == "2025-02-01"

    @patch(
        "src.guardian_api.requests.get",
        side_effect=Exception()
    )
    def test_get_content_failure(self, mock_requests_get, guardian_api):
        search_term = "Test Query"
        with pytest.raises(Exception):
            guardian_api.get_content(search_term)

    @patch("src.guardian_api.requests.get")
    def test_pagination(self, mock_requests_get, guardian_api):
        response_page_1 = {
            "response": {
                "status": "ok",
                "pages": 3,
                "results": [self._make_article(i) for i in range(10)]
            }
        }
        response_page_2 = {
            "response": {
                "status": "ok",
                "pages": 3,
                "results": [self._make_article(i) for i in range(10, 20)]
            }
        }
        response_page_3 = {
            "response": {
                "status": "ok",
                "pages": 3,
                "results": [self._make_article(i) for i in range(20, 30)]
            }
        }
        mock_response_1 = MagicMock()
        mock_response_1.json.return_value = response_page_1
        mock_response_2 = MagicMock()
        mock_response_2.json.return_value = response_page_2
        mock_response_3 = MagicMock()
        mock_response_3.json.return_value = response_page_3
        mock_requests_get.side_effect = [mock_response_1, mock_response_2, mock_response_3]

        articles = guardian_api.get_content("query", None, max_articles=25)

        assert len(articles) == 25
        expected_ids = [f"article-{i}" for i in range(25)]
        actual_ids = [article.id for article in articles]
        assert actual_ids == expected_ids

    @patch("src.guardian_api.requests.get")
    def test_partial_pagination(self, mock_requests_get, guardian_api):
        response = {
            "response": {
                "status": "ok",
                "pages": 1,
                "results": [self._make_article(i) for i in range(10)]
            }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = response
        mock_requests_get.return_value = mock_response

        articles = guardian_api.get_content("query", None, max_articles=20)

        assert len(articles) == 10

    @patch("src.guardian_api.requests.get")
    def test_results_empty(self, mock_requests_get, guardian_api):
        response = {
            "response": {
                "status": "ok",
                "pages": 1,
                "results": []
            }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = response
        mock_requests_get.return_value = mock_response

        articles = guardian_api.get_content("query", None, max_articles=10)

        assert articles == []

    @patch("src.guardian_api.requests.get")
    def test_incomplete_response_structure(self, mock_requests_get, guardian_api):
        missing_response = {"no_response": {}}
        mock_response_1 = MagicMock()
        mock_response_1.json.return_value = missing_response
        mock_requests_get.return_value = mock_response_1

        with pytest.raises(ValueError):
            guardian_api.get_content("query", None, max_articles=5)

        missing_results = {
            "response": {
                "status": "ok",
                "pages": 1
            }
        }
        mock_response_2 = MagicMock()
        mock_response_2.json.return_value = missing_results
        mock_requests_get.return_value = mock_response_2

        with pytest.raises(ValueError):
            guardian_api.get_content("query", None, max_articles=5)
