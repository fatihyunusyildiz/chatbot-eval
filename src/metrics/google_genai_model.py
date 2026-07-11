from __future__ import annotations

import asyncio
from typing import Optional

from google.genai import types
from pydantic import BaseModel

from deepeval.models.base_model import DeepEvalBaseLLM

from config import get_google_vertex_config
from google_vertex_client import build_google_vertex_client, generate_google_vertex_text


class GoogleGenAIADCModel(DeepEvalBaseLLM):
    """DeepEval model adapter backed by google-genai Client() / ADC."""

    def __init__(self, model: Optional[str] = None):
        self.config = get_google_vertex_config()
        super().__init__(model or self.config.judge_model)

    def load_model(self):
        return build_google_vertex_client(self.config)

    def generate(self, prompt: str, schema: Optional[type[BaseModel]] = None):
        if schema is not None:
            response = self.model.models.generate_content(
                model=self.name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0,
                ),
            )
            if response.parsed is not None:
                return response.parsed
            return schema.model_validate_json(response.text)

        return generate_google_vertex_text(prompt, model=self.name, config=self.config)

    async def a_generate(self, prompt: str, schema: Optional[type[BaseModel]] = None):
        return await asyncio.to_thread(self.generate, prompt, schema)

    def get_model_name(self) -> str:
        return f"{self.name} (Google GenAI ADC)"
