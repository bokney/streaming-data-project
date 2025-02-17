
import pytest
from src.config import Config


class TestConfig:
    @pytest.fixture(autouse=True)
    def reset_config_singleton(self, monkeypatch):
        monkeypatch.setattr("src.config.load_dotenv", lambda: None)
        monkeypatch.setattr(Config, "_instance", None)

    def test_is_singleton(self):
        config1 = Config()
        config2 = Config()
        assert config1 is config2

    def test_valid_env(self, monkeypatch):
        monkeypatch.setenv("GUARDIAN_KEY", "test_guardian_key")
        monkeypatch.setenv("SQS_QUEUE_URL", "test_sqs_url")

        config = Config()
        assert config.guardian_api_key == "test_guardian_key"
        assert config.sqs_queue_url == "test_sqs_url"

    def test_missing_env(self, monkeypatch):
        monkeypatch.delenv("GUARDIAN_KEY", raising=False)
        monkeypatch.delenv("SQS_QUEUE_URL", raising=False)

        with pytest.raises(EnvironmentError):
            Config()
