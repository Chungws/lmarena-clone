"""
LLM API client for OpenAI-compatible endpoints
"""

import logging
import time
from typing import Dict, List, Optional

import httpx
from llmbattler_shared.config import settings

from .model_service import ModelConfig

logger = logging.getLogger(__name__)


class LLMResponse:
    """
    LLM API response wrapper

    Contains response text and metadata
    """
    def __init__(self, content: str, latency_ms: int, model_id: str):
        self.content = content
        self.latency_ms = latency_ms
        self.model_id = model_id


class LLMClient:
    """
    HTTP client for OpenAI-compatible LLM APIs

    Supports:
    - OpenAI API (https://api.openai.com/v1)
    - Anthropic API (via OpenAI-compatible proxy)
    - Ollama (http://localhost:11434/v1)
    - vLLM (custom endpoint)
    - Any endpoint exposing /v1/chat/completions
    """
    def __init__(self):
        """
        Initialize LLM client with timeout and retry settings
        """
        self.timeout = httpx.Timeout(
            connect=settings.llm_connect_timeout,
            read=settings.llm_read_timeout,
            write=settings.llm_write_timeout,
            pool=settings.llm_pool_timeout
        )
        self.retry_attempts = settings.llm_retry_attempts
        self.retry_backoff_base = settings.llm_retry_backoff_base

    async def chat_completion(
        self,
        model_config: ModelConfig,
        messages: List[Dict[str, str]],
    ) -> LLMResponse:
        """
        Call LLM API with OpenAI chat completion format

        Args:
            model_config: Model configuration
            messages: Conversation history in OpenAI format
                [{"role": "user", "content": "Hello"}, ...]

        Returns:
            LLMResponse with content and latency

        Raises:
            httpx.HTTPError: If API call fails after retries
        """
        url = f"{model_config.base_url.rstrip('/')}/chat/completions"
        headers = self._build_headers(model_config)
        payload = {
            "model": model_config.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024,
        }

        # Retry loop with exponential backoff
        last_error: Optional[Exception] = None

        for attempt in range(self.retry_attempts):
            try:
                start_time = time.time()

                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    response.raise_for_status()

                latency_ms = int((time.time() - start_time) * 1000)

                # Parse OpenAI-compatible response
                data = response.json()
                content = data["choices"][0]["message"]["content"]

                logger.info(
                    f"LLM API call successful: model={model_config.id}, "
                    f"latency={latency_ms}ms, attempt={attempt + 1}"
                )

                return LLMResponse(
                    content=content,
                    latency_ms=latency_ms,
                    model_id=model_config.id
                )

            except (httpx.HTTPError, KeyError, IndexError) as e:
                last_error = e
                logger.warning(
                    f"LLM API call failed: model={model_config.id}, "
                    f"attempt={attempt + 1}/{self.retry_attempts}, error={str(e)}"
                )

                # Exponential backoff (1s, 2s, 4s)
                if attempt < self.retry_attempts - 1:
                    backoff_delay = self.retry_backoff_base * (2 ** attempt)
                    logger.info(f"Retrying in {backoff_delay}s...")
                    time.sleep(backoff_delay)

        # All retries failed
        error_msg = f"LLM API call failed after {self.retry_attempts} attempts: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)

    def _build_headers(self, model_config: ModelConfig) -> Dict[str, str]:
        """
        Build HTTP headers for LLM API request

        Args:
            model_config: Model configuration

        Returns:
            Headers dictionary
        """
        headers = {
            "Content-Type": "application/json",
        }

        # Add API key if available
        if model_config.api_key:
            headers["Authorization"] = f"Bearer {model_config.api_key}"

        return headers


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    Get singleton LLMClient instance

    Returns:
        LLMClient instance
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
