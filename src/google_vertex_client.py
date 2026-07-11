from __future__ import annotations

from google import genai
from google.genai import types

from config import GoogleVertexConfig, get_google_vertex_config
from openrouter_errors import ChatbotClientError, ChatbotConfigError, ChatbotRateLimitError


def build_google_vertex_client(config: GoogleVertexConfig | None = None) -> genai.Client:
    config = config or get_google_vertex_config()
    if config.require_project and not config.project:
        raise ChatbotConfigError(
            "Google Cloud project is missing. Set GOOGLE_CLOUD_PROJECT in .env or run "
            "`gcloud config set project <project-id>` after ADC login."
        )

    try:
        http_options = types.HttpOptions(timeout=config.timeout_seconds * 1000)
        if config.project:
            return genai.Client(
                vertexai=True,
                project=config.project,
                location=config.location,
                http_options=http_options,
            )

        return genai.Client(http_options=http_options)
    except Exception as exc:
        raise ChatbotClientError(f"Google Vertex AI client initialization failed: {exc}") from exc


def generate_google_vertex_text(
    prompt: str,
    model: str,
    config: GoogleVertexConfig | None = None,
) -> str:
    config = config or get_google_vertex_config()
    client = build_google_vertex_client(config)

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                safety_settings=[
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE,
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE,
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE,
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE,
                    ),
                ],
            ),
        )
    except Exception as exc:
        message = str(exc)
        lowered = message.lower()
        if "quota" in lowered or "rate" in lowered or "resource exhausted" in lowered:
            raise ChatbotRateLimitError(f"Google Vertex AI quota/rate error: {message}") from exc
        raise ChatbotClientError(f"Google Vertex AI request failed: {message}") from exc

    text = getattr(response, "text", None)
    if not text:
        raise ChatbotClientError(f"Google Vertex AI returned an empty response: {response}")
    return text
