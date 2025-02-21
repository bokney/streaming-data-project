
import time
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, UTC
from src.guardian_api import GuardianArticle, GuardianAPI


@pytest.fixture(autouse=True)
def disable_sleep(monkeypatch):
    monkeypatch.setattr(time, 'sleep', lambda _: None)


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
        assert len(preview) == 1000


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
        date_from = datetime(2022, 12, 25, 15, 30)
        expected_date_str = "2022-12-25"

        articles = guardian_api.get_content(search_term, date_from)

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
        assert called_params.get("from-date") == expected_date_str

    @patch(
        "src.guardian_api.requests.get",
        side_effect=Exception()
    )
    def test_get_content_failure(self, mock_requests_get, guardian_api):
        search_term = "Test Query"
        with pytest.raises(Exception):
            guardian_api.get_content(search_term)
