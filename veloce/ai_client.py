import httpx
from veloce.config import Config


class AIClient:
    def __init__(self, config: Config):
        self._config = config
        self._http = httpx.AsyncClient(timeout=120.0)

    async def complete(self, prompt: str) -> str:
        result = await self._call_groq(prompt)
        if result is not None:
            return result
        result = await self._call_deepseek(prompt)
        if result is not None:
            return result
        raise RuntimeError("Les deux API ont échoué pour ce prompt.")

    async def _call_groq(self, prompt: str) -> str | None:
        response = await self._http.post(
            f"{self._config.groq_endpoint}/chat/completions",
            headers={
                "Authorization": f"Bearer {self._config.groq_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self._config.groq_model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 4096,
            },
        )
        if response.status_code == 429:
            return None
        if response.status_code != 200:
            return None
        return response.json()["choices"][0]["message"]["content"]

    async def _call_deepseek(self, prompt: str) -> str | None:
        response = await self._http.post(
            f"{self._config.deepseek_endpoint}/chat/completions",
            headers={
                "Authorization": f"Bearer {self._config.deepseek_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self._config.deepseek_model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 8192,
            },
        )
        if response.status_code != 200:
            return None
        return response.json()["choices"][0]["message"]["content"]

    async def close(self) -> None:
        await self._http.aclose()
