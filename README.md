
# streaming-data-project     [![Documentation Status](https://readthedocs.org/projects/streaming-data-project/badge/?version=latest)](https://streaming-data-project.readthedocs.io/en/latest/?badge=latest)
A system designed to retrieve articles from the Guardian API and publish them to AWS SQS message broker to be distributed to various applications. Read the full docs on [ReadTheDocs](https://streaming-data-project.readthedocs.io).

# streaming-data-project     [![Documentation Status](https://readthedocs.org/projects/streaming-data-project/badge/?version=latest)](https://streaming-data-project.readthedocs.io/en/latest/?badge=latest)


## Overview

`streaming-data-project` is a Python module that provides a pipeline to stream articles from the Guardian API to AWS SQS. The project integrates a Guardian API client and an SQS publisher, with the option to invoke via a command-line interface (CLI) to automate the process of retrieving, transforming, and forwarding data.
Read the full docs on [ReadTheDocs](https://streaming-data-project.readthedocs.io).

## Installation

Clone the repository and install the required packages:

```bash
git clone https://github.com/bokney/streaming-data-project.git
cd streaming-data-project
pip install -r requirements.txt
```

## Configuration

Set the following environment variables in your system or include them in a `.env` file in the project root:

```text
GUARDIAN_KEY=your_guardian_api_key
SQS_QUEUE_URL=https://sqs.your-region.amazonaws.com/your-account-id/your-queue
AWS_REGION=your_aws_region
```

Additionally, ensure you have valid AWS credentials to interact with AWS SQS.

## Usage

The module can be used as a library or a standalone CLI tool. To run the pipeline from the command line:

```bash
python src/guardian_to_sqs.py [SEARCH_TERM] [--date-from YYYY-MM-DD]
```

- Replace `[SEARCH_TERM]` with the keyword(s) you wish to search.
- Optionally, use `--date-from` to filter articles published from a specific date (YYYY-MM-DD format).

### Example

To search for articles related to "machine learning" starting from January 1, 2023:

```bash
python src/guardian_to_sqs.py "machine learning" --date-from 2023-01-01
```

## Running Tests

To run all tests, execute:

```bash
pytest
```
