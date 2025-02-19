
from typing import Optional
from datetime import datetime
from src.guardian_api import GuardianAPI, GuardianArticle
from src.sqs_publisher import SQSPublisher, SQSMessage


class GuardianToSQS:
    def __init__(
            self,
            guardian_api: Optional[GuardianAPI] = None,
            sqs_publisher: Optional[SQSPublisher] = None
            ) -> None:
        if guardian_api is None:
            guardian_api = GuardianAPI()
        if sqs_publisher is None:
            sqs_publisher = SQSPublisher()
        self._guardian_api = guardian_api
        self._sqs_publisher = sqs_publisher

    def transfer_articles(
            self,
            query: str,
            date_from: Optional[datetime] = None
            ) -> None:
        try:
            articles = self._guardian_api.get_content(query, date_from)
            for article in articles:
                message = self._transform(article)
                self._sqs_publisher.publish_message(message)
        except Exception as e:
            raise e

    def _transform(self, article: GuardianArticle) -> SQSMessage:
        return SQSMessage(
            webPublicationDate=article.webPublicationDate.strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            webTitle=article.webTitle,
            webUrl=str(article.webUrl)
        )
