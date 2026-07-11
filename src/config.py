from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _bool_env(name: str, default: bool = True) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


@dataclass(frozen=True)
class GoogleVertexConfig:
    project: str | None
    location: str
    chatbot_model: str
    judge_model: str
    timeout_seconds: int
    require_project: bool


@dataclass(frozen=True)
class OpenRouterConfig:
    api_key: str | None
    base_url: str
    chatbot_model: str
    judge_model: str
    http_referer: str
    title: str
    ssl_verify: bool
    timeout_seconds: int

    @property
    def chat_completions_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/chat/completions"

    @property
    def default_headers(self) -> dict[str, str]:
        headers = {
            "HTTP-Referer": self.http_referer,
            "X-Title": self.title,
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers


def get_model_provider() -> str:
    return os.getenv("MODEL_PROVIDER", "google_vertex").strip().lower()


def get_timeout_seconds() -> int:
    timeout_raw = os.getenv("CHATBOT_TIMEOUT_SECONDS", "120")
    try:
        return int(timeout_raw)
    except ValueError:
        return 120


def _nonempty_env(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    return None


def _project_from_adc() -> str | None:
    try:
        import google.auth

        _credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
    except Exception:
        return None

    if project_id and project_id.strip():
        return project_id.strip()
    return None


def _project_from_gcloud_config() -> str | None:
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        return None

    project_id = result.stdout.strip()
    if result.returncode == 0 and project_id and project_id != "(unset)":
        return project_id
    return None


def get_google_cloud_project() -> str | None:
    return (
        _nonempty_env("GOOGLE_CLOUD_PROJECT", "GCLOUD_PROJECT", "GOOGLE_CLOUD_QUOTA_PROJECT")
        or _project_from_adc()
        or _project_from_gcloud_config()
    )


def get_google_vertex_config() -> GoogleVertexConfig:
    return GoogleVertexConfig(
        project=get_google_cloud_project(),
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        chatbot_model=os.getenv("GOOGLE_CHATBOT_MODEL", "gemini-2.5-flash"),
        judge_model=os.getenv("GOOGLE_JUDGE_MODEL", "gemini-2.5-flash"),
        timeout_seconds=get_timeout_seconds(),
        require_project=_bool_env("GOOGLE_REQUIRE_PROJECT", False),
    )


def get_openrouter_config() -> OpenRouterConfig:
    return OpenRouterConfig(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        chatbot_model=os.getenv("OPENROUTER_CHATBOT_MODEL", "openrouter/free"),
        judge_model=os.getenv("OPENROUTER_JUDGE_MODEL", "openrouter/free"),
        http_referer=os.getenv("OPENROUTER_HTTP_REFERER", "http://localhost"),
        title=os.getenv("OPENROUTER_X_TITLE", "chatbot-eval"),
        ssl_verify=_bool_env("OPENROUTER_SSL_VERIFY", True),
        timeout_seconds=get_timeout_seconds(),
    )
