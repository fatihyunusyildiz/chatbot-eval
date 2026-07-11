from __future__ import annotations

from deepeval.models import GeminiModel, OpenRouterModel

from config import get_google_vertex_config, get_model_provider, get_openrouter_config
from metrics.google_genai_model import GoogleGenAIADCModel


def get_judge_model():
    provider = get_model_provider()
    if provider in {"google", "google_vertex", "vertex", "vertexai", "gemini_vertex"}:
        config = get_google_vertex_config()
        if not config.project:
            return GoogleGenAIADCModel(model=config.judge_model)

        return GeminiModel(
            model=config.judge_model,
            project=config.project,
            location=config.location,
            use_vertexai=True,
            temperature=0,
            http_options={"timeout": config.timeout_seconds * 1000},
        )

    if provider not in {"openrouter", "open_router"}:
        raise ValueError(f"Unsupported MODEL_PROVIDER: {provider}")

    config = get_openrouter_config()
    return OpenRouterModel(
        model=config.judge_model,
        api_key=config.api_key,
        base_url=config.base_url,
        temperature=0,
        default_headers={
            "HTTP-Referer": config.http_referer,
            "X-Title": config.title,
        },
    )
