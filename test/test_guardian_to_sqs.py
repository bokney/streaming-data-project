
import pytest
from datetime import datetime
from unittest.mock import MagicMock
from src.guardian_api import GuardianArticle
from src.guardian_to_sqs import GuardianToSQS


class TestGuardianToSQS:
    def test_transformation(self):
        test_date = datetime(2025, 1, 11, 13, 4, 13)
        test_article = GuardianArticle(
            id=(
                "uk-news/2025/jan/11/"
                "gritters-stopped-by-200-cars-double-parked-"
                "on-peak-district-road-says-council"
            ),
            type="article",
            sectionId="uk-news",
            sectionName="UK news",
            webPublicationDate=test_date,
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
        pipeline = GuardianToSQS(
            guardian_api=MagicMock(), sqs_publisher=MagicMock()
        )
        message = pipeline._transform(test_article)
        expected_date_str = test_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        assert message.webPublicationDate == expected_date_str
        assert message.webTitle == test_article.webTitle
        assert message.webUrl == test_article.webUrl

    def test_pipeline(self):
        test_date = datetime(2025, 1, 11, 13, 4, 13)
        test_article = GuardianArticle(
            id=(
                "uk-news/2025/jan/11/"
                "gritters-stopped-by-200-cars-double-parked-"
                "on-peak-district-road-says-council"
            ),
            type="article",
            sectionId="uk-news",
            sectionName="UK news",
            webPublicationDate=test_date,
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
        guardian_api = MagicMock()
        sqs_publisher = MagicMock()

        guardian_api.get_content.return_value = [test_article]

        pipeline = GuardianToSQS(
            guardian_api=guardian_api, sqs_publisher=sqs_publisher
        )

        query = "Rushup Edge"
        date_from = datetime(2023, 3, 1, 0, 0, 0)

        pipeline.transfer_articles(query, date_from)

        guardian_api.get_content.assert_called_once_with(query, date_from)
        sqs_publisher.publish_message.assert_called_once()
        published_message = sqs_publisher.publish_message.call_args[0][0]
        expected_date_str = test_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        assert published_message.webPublicationDate == expected_date_str
        assert published_message.webTitle == test_article.webTitle
        assert published_message.webUrl == test_article.webUrl

    def test_run_error_propagation(self):
        guardian_api = MagicMock()
        guardian_api.get_content.side_effect = Exception("API error")
        sqs_publisher = MagicMock()
        pipeline = GuardianToSQS(
            guardian_api=guardian_api, sqs_publisher=sqs_publisher
        )

        with pytest.raises(Exception, match="API error"):
            pipeline.transfer_articles("test query", None)
