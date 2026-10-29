"""Provider endpoints and price snapshots for the study agent models."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Model:
    name: str
    provider: str
    provider_model_id: str
    input_usd_per_million: float
    output_usd_per_million: float
    endpoint: str
    cached_input_usd_per_million: float | None = None
    provider_order: list[str] | None = None
    supports_temperature: bool = True


# Prices are USD per 1M tokens, recorded 2026-10-26. DeepSeek official pricing
# (https://api-docs.deepseek.com/quick_start/pricing/, checked 2026-10-26): the
# legacy deepseek-v4-flash alias is served by V4.1 Flash. Peak rates are used
# conservatively because the API can double rates during its weekday peak.
# OpenRouter prices are from https://openrouter.ai/api/v1/models, fetched
# 2026-10-26; prompt/completion prices are converted from USD/token.
DEEPSEEK_ENDPOINT = "https://api.deepseek.com/chat/completions"
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

MODELS = {
    "deepseek-v4-flash": Model(
        "deepseek-v4-flash", "deepseek", "deepseek-v4-flash", 0.30, 1.20,
        DEEPSEEK_ENDPOINT, 0.006, None, True,
    ),
    # OpenRouter endpoints listing checked 2026-10-27:
    # https://openrouter.ai/api/v1/models/anthropic/claude-haiku-5.5/endpoints
    "anthropic/claude-haiku-5.5": Model(
        "anthropic/claude-haiku-5.5", "openrouter", "anthropic/claude-haiku-5.5",
        0.10, 0.50, OPENROUTER_ENDPOINT, provider_order=["anthropic"],
        supports_temperature=False,
    ),
    # OpenRouter endpoints listing checked 2026-10-27:
    # https://openrouter.ai/api/v1/models/openai/gpt-6-luna/endpoints
    "openai/gpt-6-luna": Model(
        "openai/gpt-6-luna", "openrouter", "openai/gpt-6-luna",
        0.10, 0.50, OPENROUTER_ENDPOINT, provider_order=["openai"],
        supports_temperature=False,
    ),
    # OpenRouter endpoints listing checked 2026-10-27:
    # https://openrouter.ai/api/v1/models/qwen/qwen3.8-flash/endpoints
    "qwen/qwen3.8-flash": Model(
        "qwen/qwen3.8-flash", "openrouter", "qwen/qwen3.8-flash",
        0.15, 0.47, OPENROUTER_ENDPOINT, provider_order=["alibaba"],
        supports_temperature=True,
    ),
    # Reviewer-only; OpenRouter catalog and endpoint listing checked 2026-10-28:
    # https://openrouter.ai/api/v1/models
    # https://openrouter.ai/api/v1/models/moonshotai/kimi-k3.1-pro/endpoints
    # Catalog rates are USD per 1M tokens; endpoint omits temperature support.
    "moonshotai/kimi-k3.1-pro": Model(
        "moonshotai/kimi-k3.1-pro", "openrouter", "moonshotai/kimi-k3.1-pro",
        2.0, 10.0, OPENROUTER_ENDPOINT, provider_order=["moonshotai"],
        supports_temperature=False,
    ),
}

