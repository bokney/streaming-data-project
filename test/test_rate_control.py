
import pytest
import datetime
from src.rate_control import backoff, rate_limit


class TestBackoff:
    def test_retry_count(self):
        call_count = 0
        retries = 4

        @backoff(delay=0.01, retries=retries)
        def count_and_fail():
            nonlocal call_count
            call_count += 1
            raise Exception("Intentional failure.")

        with pytest.raises(Exception, match="Intentional failure."):
            count_and_fail()

        assert call_count == retries


class TestRateLimit:
    def test_under_limit(self):
        call_count = 0

        @rate_limit(max_calls=3)
        def test_function():
            nonlocal call_count
            call_count += 1
            return call_count

        assert test_function() == 1
        assert test_function() == 2
        assert call_count == 2

    def test_over_limit(self):

        @rate_limit(max_calls=2)
        def test_function():
            return None

        test_function()
        test_function()

        with pytest.raises(RuntimeError, match="Daily rate limit exceeded"):
            test_function()

    def test_no_same_day_reset(self, monkeypatch):
        original_date = datetime.date.today()

        @rate_limit(max_calls=2)
        def test_function():
            return None

        test_function()
        test_function()

        class DummyDate(datetime.date):
            @classmethod
            def today(cls):
                return original_date

        monkeypatch.setattr(datetime, 'date', DummyDate)

        with pytest.raises(RuntimeError, match="Daily rate limit exceeded"):
            test_function()
