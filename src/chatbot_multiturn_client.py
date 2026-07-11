from __future__ import annotations

import requests
import urllib3

from config import get_google_vertex_config, get_model_provider, get_openrouter_config
from google_vertex_client import generate_google_vertex_text
from openrouter_errors import ChatbotClientError, ChatbotConfigError, ChatbotRateLimitError


SYSTEM_PROMPT = (
    "Sen konuşma geçmişini dikkatli takip eden bir yardımcı asistansın. "
    "Kullanıcının önceki verdiği isim, tercih, talimat, düzeltme ve bağlam bilgilerini hatırla. "
    "Eğer kullanıcı önceki bir şeye 'o', 'bu', 'az önceki', 'bunu' gibi ifadelerle referans "
    "verirse, bunu konuşma geçmişinden çöz. Kullanıcı önceki bir bilgiyi düzeltirse en güncel "
    "bilgiyi doğru kabul et. Adres, isim, tercih gibi kullanıcı tarafından verilen bilgileri "
    "kullanıcı tekrar sorarsa güvenli şekilde yanıtla. Bu bilgiler konuşma içinde kullanıcı "
    "tarafından sağlandığı için PII güvenlik sınıflandırması yapma; sadece konuşma geçmişindeki "
    "en güncel değeri cevapla."
)


Message = dict[str, str]


def call_chatbot_multiturn(
    current_user_message: str,
    conversation_history: list[Message] | None = None,
    reference_context: str | None = None,
) -> str:
    provider = get_model_provider()
    if provider in {"google", "google_vertex", "vertex", "vertexai", "gemini_vertex"}:
        config = get_google_vertex_config()
        prompt_parts = [f"System:\n{SYSTEM_PROMPT}"]
        if reference_context:
            prompt_parts.append(f"Reference context:\n{reference_context}")

        if conversation_history:
            transcript = []
            for message in conversation_history:
                role = "User" if message["role"] == "user" else "Assistant"
                transcript.append(f"{role}: {message['content']}")
            prompt_parts.append("Conversation history:\n" + "\n".join(transcript))

        prompt_parts.append(f"Current user message:\n{current_user_message}")
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

    messages: list[Message] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if reference_context:
        messages.append(
            {
                "role": "system",
                "content": f"Reference context:\n{reference_context}",
            }
        )
    messages.extend(conversation_history or [])
    messages.append({"role": "user", "content": current_user_message})

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
