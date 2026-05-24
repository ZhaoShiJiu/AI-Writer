import httpx

from app.config import settings

DEFAULT_MODEL = "deepseek/deepseek-v4-pro"


class LLMClient:
    def __init__(self):
        self.gateway_url = settings.llm_gateway_url.rstrip("/")

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = DEFAULT_MODEL,
    ) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        async with httpx.AsyncClient(timeout=120) as client:
            try:
                response = await client.post(
                    f"{self.gateway_url}/chat/completions",
                    json={"model": model, "messages": messages},
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                return f"[生成失败: {str(e)}] 请稍后重试。"
