
"""
This module provides decorators for implementing exponential backoff
and daily rate limiting. The `backoff` decorator retries a function
call using an exponential backoff strategy when exceptions occur,
while the `rate_limit` decorator restricts the number of times a
function can be called in a single day.
"""

import time
import datetime
from functools import wraps


def backoff(delay: int = 1, retries: int = 4):
    """
    Retry decorator with exponential backoff.

    This decorator calls the decorated function and, if an exception occurs
    (except for ValueError), retries the function call after a delay that
    doubles after each failure until the maximum number of retries is reached.
    If all retries fail, the last exception is raised.

    :param delay: The initial delay between retries in seconds (default is 1).
    :type delay: int
    :param retries: The maximum number of attempts before giving up
        (default is 4).
    :type retries: int
    :raises Exception: If the decorated function continues to fail after the
        specified number of retries.
    :return: The result of the decorated function call.
    :rtype: Any
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_retry = 0
            current_delay = delay
            while current_retry < retries:
                try:
                    return func(*args, **kwargs)
                except ValueError:
                    raise
                except Exception as e:
                    current_retry += 1
                    if current_retry >= retries:
                        raise e
                    time.sleep(current_delay)
                    current_delay *= 2
        return wrapper
    return decorator


def rate_limit(max_calls: int = 50):
    """
    Decorator to enforce a daily rate limit on function calls.

    This decorator restricts the decorated function to be called no more than
    a specified number of times per day. It uses an in-memory counter that
    resets when the date changes.

    :param max_calls: Maximum number of allowed calls per day (default is 50).
    :type max_calls: int
    :raises RuntimeError: If the daily rate limit is exceeded.
    :return: The result of the decorated function call.
    :rtype: Any
    """
    counter = {'date': datetime.date.today(), 'count': 0}

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            today = datetime.date.today()
            if today != counter['date']:
                counter['date'] = today
                counter['count'] = 0
            if counter['count'] >= max_calls:
                raise RuntimeError("Daily rate limit exceeded")
            counter['count'] += 1
            return func(*args, **kwargs)
        return wrapper
    return decorator
