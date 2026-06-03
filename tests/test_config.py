import pytest
from veloce.config import Config


@pytest.fixture(autouse=True)
def set_required_env(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test123")
    monkeypatch.setenv("GROQ_ENDPOINT", "https://api.groq.example.com/openai/v1")
    monkeypatch.setenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk_test456")
    monkeypatch.setenv("DEEPSEEK_ENDPOINT", "https://deepseek.example.com/v1")
    monkeypatch.setenv("DEEPSEEK_MODEL_NAME", "deepseek-v4-flash")
    monkeypatch.setenv("PHP_SOURCE_PATH", "C:\\fake\\source")
    monkeypatch.setenv("MIRROR_WORK_PATH", "C:\\fake\\work")


def test_config_loads_all_values():
    cfg = Config()
    assert cfg.groq_api_key == "gsk_test123"
    assert cfg.deepseek_api_key == "sk_test456"
    assert cfg.batch_size == 15
    assert cfg.max_retry_compile == 3
    assert cfg.sleep_between_files == 10
    assert cfg.files_before_cleanup == 50
    assert cfg.cpu_cores_limit == 2


def test_config_raises_on_missing_required_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GROQ_API_KEY"):
        Config()
