import logging
import time
from typing import Any, Dict

import httpx

from app.core.config import settings
from app.services.ai.provider import BaseAIProvider

logger = logging.getLogger(__name__)


class GroqProvider(BaseAIProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or "llama-3.1-70b-versatile"
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    async def generate_response(
        self, prompt: str, system_prompt: str = None, json_mode: bool = False
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not configured in environment variables.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 4096,
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        start_time = time.time()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.url, json=payload, headers=headers, timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPStatusError as e:
                error_msg = f"Groq API returned status {e.response.status_code}: {e.response.text}"
                logger.error(error_msg)
                raise Exception(error_msg) from e
            except httpx.RequestError as e:
                error_msg = f"Failed to connect to Groq API: {str(e)}"
                logger.error(error_msg)
                raise Exception(error_msg) from e

        end_time = time.time()
        response_time = end_time - start_time

        choices = data.get("choices", [])
        if not choices:
            raise Exception("Groq API returned an empty choices array.")

        content = choices[0]["message"]["content"]
        usage = data.get("usage", {})

        tokens = {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }

        return {"response": content, "tokens": tokens, "response_time": response_time}
