
import pytest
import threading
from src.config import Config


class TestConfig:
    @pytest.fixture(autouse=True)
    def reset_config_singleton(self, monkeypatch):
        monkeypatch.setattr("src.config.load_dotenv", lambda: None)
        monkeypatch.setattr(Config, "_instance", None)

    def test_is_singleton(self, monkeypatch):
        monkeypatch.setenv("GUARDIAN_KEY", "test_guardian_key")
        monkeypatch.setenv("SQS_QUEUE_URL", "test_sqs_url")

        config1 = Config()
        config2 = Config()
        assert config1 is config2

    def test_valid_env(self, monkeypatch):
        monkeypatch.setenv("GUARDIAN_KEY", "test_guardian_key")
        monkeypatch.setenv("SQS_QUEUE_URL", "test_sqs_url")
        monkeypatch.setenv("AWS_REGION", "test_region")

        config = Config()
        assert config.guardian_api_key == "test_guardian_key"
        assert config.sqs_queue_url == "test_sqs_url"
        assert config.aws_region == "test_region"

    def test_missing_guardian_api_key(self, monkeypatch):
        monkeypatch.delenv("GUARDIAN_KEY", raising=False)
        monkeypatch.setenv("SQS_QUEUE_URL", "test_sqs_url")

        with pytest.raises(OSError):
            config = Config()
            config.guardian_api_key

    def test_missing_sqs_queue_url(self, monkeypatch):
        monkeypatch.setenv("GUARDIAN_KEY", "test_guardian_key")
        monkeypatch.delenv("SQS_QUEUE_URL", raising=False)

        with pytest.raises(OSError):
            config = Config()
            config.sqs_queue_url

    def test_optional_aws_region(self, monkeypatch):
        monkeypatch.setenv("GUARDIAN_KEY", "test_guardian_key")
        monkeypatch.setenv("SQS_QUEUE_URL", "test_sqs_url")
        monkeypatch.delenv("AWS_REGION", raising=False)
        config = Config()
        assert config.aws_region is None

    def test_thread_safety(self, monkeypatch):
        monkeypatch.setenv("GUARDIAN_KEY", "test_guardian_key")
        monkeypatch.setenv("SQS_QUEUE_URL", "test_sqs_url")

        instances = []

        def get_instance():
            instances.append(Config())

        threads = [threading.Thread(target=get_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        first_instance = instances[0]
        for instance in instances:
            assert instance is first_instance
