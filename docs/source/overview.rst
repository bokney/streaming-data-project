
Overview
========
`streaming-data-project` is a Python module that provides a pipeline to
stream articles from the Guardian API to AWS SQS. The project integrates a
Guardian API client and an SQS publisher, with the option to invoke via
a command-line interface (CLI) to automate the process of retrieving,
transforming, and forwarding data.

How to install
--------------
The project is hosted on GitHub. To install it, clone the repository and
install the required packages:

.. code-block:: bash

   git clone https://github.com/bokney/streaming-data-project.git
   cd streaming-data-project
   pip install -r requirements.txt

How to configure
----------------
The module requires several environment variables for proper operation.
Ensure the following variables are set in your environment or included in a
``.env`` file in the project root:

- **GUARDIAN_KEY**: Your API key for accessing the Guardian API.
- **SQS_QUEUE_URL**: The URL of the AWS SQS queue to which messages will be
  published.
- **AWS_REGION**: The AWS region in which your SQS queue is located.

A sample ``.env`` file might look like:

.. code-block:: text

   GUARDIAN_KEY=your_guardian_api_key
   SQS_QUEUE_URL=https://sqs.your-region.amazonaws.com/your-account-id/your-queue
   AWS_REGION=your_aws_region

In addition, the application requires valid AWS credentials to interact with
AWS SQS. The AWS profile can be set with:

.. code-block:: text

   export AWS_PROFILE=your_profile_name

How to use
----------
The module can be used both as a library and as a standalone CLI tool.
To run the pipeline from the command line, execute:

.. code-block:: bash

   python src/guardian_to_sqs.py [QUERY_STRING] [--date-from YYYY-MM-DD] [--date-to YYYY-MM-DD]

- Replace ``[QUERY_STRING]`` with the query string you wish to search for.
- Optionally, use the ``--date-from`` and/or ``--date-to`` flags to filter articles published from
  or before a specific date (formatted as YYYY-MM-DD).

Example
*******
To search for articles related to "machine learning" starting from January 1,
2023, run:

.. code-block:: bash

   python src/guardian_to_sqs.py '"machine learning"' --date-from 2023-01-01

Running Tests
-------------

This project uses **pytest** as its testing framework.
To run all tests, execute:

.. code-block:: bash

   pytest
