
"""
This module defines the GuardianToSQS class, which uses a
GuardianAPI client to retrieve articles, converts them to a
SQSMessage using the _transform method and then publishes
them to an AWS SQS queue using a SQSPublisher client.
It also provides a command-line interface to run the pipeline.
"""

from typing import Optional
from datetime import datetime
from src.guardian_api import GuardianAPI, GuardianArticle
from src.sqs_publisher import SQSPublisher, SQSMessage


class GuardianToSQS:
    """
    Transfer Guardian articles to AWS SQS.

    This class retrieves articles from the Guardian API based on a search
    query and an optional start date, transforms them into a SQSMessage, and
    publishes them to an AWS SQS queue using SQSPublisher.
    """
    def __init__(
            self,
            guardian_api: Optional[GuardianAPI] = None,
            sqs_publisher: Optional[SQSPublisher] = None
            ) -> None:
        """
        Initialize a GuardianToSQS instance.

        If no GuardianAPI or SQSPublisher instance is provided, default
        instances will be created.

        :param guardian_api: Optional GuardianAPI instance to use.
        :type guardian_api: Optional[GuardianAPI]
        :param sqs_publisher: Optional SQSPublisher instance to use.
        :type sqs_publisher: Optional[SQSPublisher]
        """
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
        """
        Transfer articles from the Guardian API to AWS SQS.

        This method fetches articles using the given query and an
        optional start date, transforms each article into an SQSMessage,
        and publishes it to AWS SQS.

        :param query: Search query for retrieving Guardian articles.
        :type query: str
        :param date_from: Optional start date for filtering articles.
        :type date_from: Optional[datetime]
        :raises Exception: Propagates any exception that occurs during
            transfer.
        """
        try:
            articles = self._guardian_api.get_content(query, date_from)
            for article in articles:
                message = self._transform(article)
                self._sqs_publisher.publish_message(message)
        except Exception as e:
            raise e

    def _transform(self, article: GuardianArticle) -> SQSMessage:
        """
        Transform a GuardianArticle into an SQSMessage.

        :param article: A GuardianArticle instance to transform.
        :type article: GuardianArticle
        :return: An SQSMessage containing selected fields from the article.
        :rtype: SQSMessage
        """
        return SQSMessage(
            webPublicationDate=article.webPublicationDate.strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            webTitle=article.webTitle,
            webUrl=str(article.webUrl)
        )


if __name__ == "__main__":
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(
        description=(
            "Extract articles from The Guardian and publish them to AWS SQS."
        )
    )
    parser.add_argument(
        "query",
        help="Search query for retrieving Guardian articles"
    )
    parser.add_argument(
        "--date-from",
        help="Start date for filtering articles (format: YYYY-MM-DD)",
        default=None
    )
    args = parser.parse_args()

    date_from = None
    if args.date_from:
        try:
            date_from = datetime.strptime(args.date_from, "%Y-%m-%d")
        except ValueError:
            print(
                "Invalid date format for --date-from. Please use YYYY-MM-DD."
            )
            exit(1)

    try:
        pipeline = GuardianToSQS()
        pipeline.transfer_articles(args.query, date_from)
        print("Transfer completed successfully.")

    except Exception as e:
        raise e
