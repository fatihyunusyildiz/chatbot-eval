from __future__ import annotations

import requests
import urllib3

from config import get_google_vertex_config, get_model_provider, get_openrouter_config
from google_vertex_client import generate_google_vertex_text
from openrouter_errors import ChatbotClientError, ChatbotConfigError, ChatbotRateLimitError


SYSTEM_PROMPT = (
    "Sen doğru, kısa ve kaynaklara bağlı cevap veren bir müşteri destek asistanısın. "
    "Eğer bilgi verilen bağlamda yoksa uydurma; bunu açıkça belirt."
)


def call_chatbot(input_text: str, reference_context: str | None = None) -> str:
    provider = get_model_provider()
    if provider in {"google", "google_vertex", "vertex", "vertexai", "gemini_vertex"}:
        config = get_google_vertex_config()
        prompt_parts = [f"System:\n{SYSTEM_PROMPT}"]
        if reference_context:
            prompt_parts.append(f"Reference context:\n{reference_context}")
        prompt_parts.append(f"User:\n{input_text}")
        prompt_parts.append("Assistant:")
        return generate_google_vertex_text(
            "\n\n".join(prompt_parts),
            model=config.chatbot_model,
            config=config,
        )

    if provider not in {"openrouter", "open_router"}:
        raise ChatbotConfigError(f"Unsupported MODEL_PROVIDER: {provider}")

    config = get_openrouter_config()
    if not config.api_key:
        raise ChatbotConfigError("OPENROUTER_API_KEY is missing.")

    if not config.ssl_verify:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if reference_context:
        messages.append(
            {
                "role": "system",
                "content": f"Reference context:\n{reference_context}",
            }
        )
    messages.append({"role": "user", "content": input_text})

    payload = {
        "model": config.chatbot_model,
        "messages": messages,
        "temperature": 0,
    }

    try:
        response = requests.post(
            config.chat_completions_url,
            headers=config.default_headers,
            json=payload,
            timeout=config.timeout_seconds,
            verify=config.ssl_verify,
        )
    except requests.RequestException as exc:
        raise ChatbotClientError(f"OpenRouter request failed: {exc}") from exc

    if response.status_code == 429:
        raise ChatbotRateLimitError(f"OpenRouter rate limit/quota error: {response.text}")

    try:
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except (requests.HTTPError, KeyError, IndexError, ValueError) as exc:
        raise ChatbotClientError(f"Invalid OpenRouter response: {response.text}") from exc
