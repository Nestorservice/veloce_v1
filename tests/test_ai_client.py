import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from veloce.ai_client import AIClient
from veloce.config import Config


@pytest.fixture
def cfg(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test")
    monkeypatch.setenv("GROQ_ENDPOINT", "https://api.groq.example.com/openai/v1")
    monkeypatch.setenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk_test")
    monkeypatch.setenv("DEEPSEEK_ENDPOINT", "https://api.deepseek.example.com/v1")
    monkeypatch.setenv("DEEPSEEK_MODEL_NAME", "deepseek-v4-flash")
    monkeypatch.setenv("PHP_SOURCE_PATH", "C:\\fake")
    monkeypatch.setenv("MIRROR_WORK_PATH", "C:\\fake2")
    return Config()


@pytest.mark.asyncio
async def test_groq_success(cfg):
    client = AIClient(cfg)
    mock_resp = MagicMock(status_code=200)
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "package main\n\nfunc main() {}"}}]
    }
    with patch.object(client._http, "post", new_callable=AsyncMock, return_value=mock_resp):
        result = await client.complete("Traduis ce PHP en Go")
    assert result == "package main\n\nfunc main() {}"


@pytest.mark.asyncio
async def test_failover_to_deepseek_on_429(cfg):
    client = AIClient(cfg)
    groq_429 = MagicMock(status_code=429)
    deepseek_ok = MagicMock(status_code=200)
    deepseek_ok.json.return_value = {
        "choices": [{"message": {"content": "// Go code from DeepSeek V4-Flash"}}]
    }
    with patch.object(client._http, "post", new_callable=AsyncMock,
                      side_effect=[groq_429, deepseek_ok]):
        result = await client.complete("Traduis ce PHP en Go")
    assert result == "// Go code from DeepSeek V4-Flash"


@pytest.mark.asyncio
async def test_raises_when_both_apis_fail(cfg):
    client = AIClient(cfg)
    fail = MagicMock(status_code=500)
    with patch.object(client._http, "post", new_callable=AsyncMock, return_value=fail):
        with pytest.raises(RuntimeError, match="Les deux API ont échoué"):
            await client.complete("Traduis ce PHP en Go")
