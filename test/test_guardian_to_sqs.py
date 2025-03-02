
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
        pipeline = GuardianToSQS(
            guardian_api=MagicMock(), sqs_publisher=MagicMock()
        )
        message = pipeline._transform(test_article)
        expected_date_str = test_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        assert message.webPublicationDate == expected_date_str
        assert message.webTitle == test_article.webTitle
        assert message.webUrl == test_article.webUrl
        assert message.content_preview.startswith("Gritting crews")
        assert len(message.content_preview) <= 1000

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

        query = '"Rushup Edge"'
        date_from = datetime(2023, 3, 1, 0, 0, 0)
        date_to = datetime(2025, 2, 1)

        pipeline.transfer_articles(query, date_from, date_to, max_articles=10)

        guardian_api.get_content.assert_called_once_with(
            query='"Rushup Edge"',
            date_from=datetime(2023, 3, 1, 0, 0, 0),
            date_to=datetime(2025, 2, 1),
            max_articles=10
        )

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
