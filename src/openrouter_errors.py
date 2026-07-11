from __future__ import annotations


class ChatbotClientError(RuntimeError):
    """Raised when the black-box chatbot call cannot be completed."""


class ChatbotConfigError(ChatbotClientError):
    """Raised when required chatbot configuration is missing."""


class ChatbotRateLimitError(ChatbotClientError):
    """Raised when the provider returns a rate-limit or quota response."""
