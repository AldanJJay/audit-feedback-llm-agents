"""Async multi-provider chat client with a persistent cost ledger and caps."""

import asyncio
import fcntl
import json
import os
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import httpx

from .models import MODELS, Model

_BUDGETS = {}


class BudgetExceeded(RuntimeError):
    """Raised before a request when its estimated cost exceeds the cap."""


class ProviderMismatch(RuntimeError):
    """Raised when OpenRouter reports a provider outside the pinned order."""


@dataclass
class ChatResult:
    text: str | None
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    response: dict


class Budget:
    """Provider spend ledger, reloaded from JSONL whenever constructed."""

    def __init__(self, ledger_path, caps=None):
        self.ledger_path = Path(ledger_path)
        self.caps = {"deepseek": 8.0, "openrouter": 8.0}
        if caps:
            self.caps.update(caps)
        self.totals = {provider: 0.0 for provider in self.caps}
        self._reserved = {provider: 0.0 for provider in self.caps}
        self._offset = 0
        self._lock = asyncio.Lock()
        self._read_new_lines()

    @contextmanager
    def _provider_lock(self, provider):
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path = Path(f"{self.ledger_path}.{provider}.lock")
        with lock_path.open("a+") as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    def _read_new_lines(self):
        if not self.ledger_path.exists():
            self._offset = 0
            return
        with self.ledger_path.open("r+", encoding="utf-8") as ledger:
            ledger.seek(self._offset)
            for line in ledger:
                if line.strip():
                    row = json.loads(line)
                    provider = row["provider"]
                    self.totals[provider] = self.totals.get(provider, 0.0) + float(row["cost_usd"])
                    self._reserved.setdefault(provider, 0.0)
                    self.caps.setdefault(provider, 8.0)
            self._offset = ledger.tell()

    def _reservation_file(self, provider):
        return Path(f"{self.ledger_path}.{provider}.reservations.json")

    @staticmethod
    def _pid_alive(pid):
        try:
            os.kill(int(pid), 0)
            return True
        except (ProcessLookupError, ValueError, TypeError):
            return False
        except PermissionError:
            return True

    def _load_reservations(self, provider):
        path = self._reservation_file(provider)
        if path.exists():
            try:
                reservations = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                reservations = {}
        else:
            reservations = {}
        reservations = {key: value for key, value in reservations.items()
                        if self._pid_alive(value.get("pid"))}
        path.write_text(json.dumps(reservations, separators=(",", ":")), encoding="utf-8")
        self._reserved[provider] = sum(float(value["amount"]) for value in reservations.values())
        return reservations

    @staticmethod
    def estimate(model: Model, messages, max_tokens):
        # UTF-8 bytes are a conservative upper bound for token count.
        prompt_bytes = len(json.dumps(messages, ensure_ascii=False).encode("utf-8"))
        return (prompt_bytes * model.input_usd_per_million +
                max_tokens * model.output_usd_per_million) / 1_000_000

    async def reserve(self, model, messages, max_tokens):
        estimate = self.estimate(model, messages, max_tokens)
        async with self._lock:
            provider = model.provider
            with self._provider_lock(provider):
                self._read_new_lines()
                reservations = self._load_reservations(provider)
                total = self.totals.get(provider, 0.0) + self._reserved.get(provider, 0.0)
                cap = self.caps.get(provider, 8.0)
                if total + estimate > cap:
                    raise BudgetExceeded(
                        f"{provider} cap ${cap:.6f} would be exceeded "
                        f"(ledger ${self.totals.get(provider, 0.0):.6f}, "
                        f"reserved ${self._reserved.get(provider, 0.0):.6f}, "
                        f"estimate ${estimate:.6f})"
                    )
                reservation_id = uuid.uuid4().hex
                reservations[reservation_id] = {"pid": os.getpid(), "amount": estimate}
                self._reservation_file(provider).write_text(
                    json.dumps(reservations, separators=(",", ":")), encoding="utf-8"
                )
                self._reserved[provider] = total + estimate - self.totals.get(provider, 0.0)
        return reservation_id, estimate

    async def record(self, model, reservation_id, estimate, row):
        async with self._lock:
            provider = model.provider
            with self._provider_lock(provider):
                self._read_new_lines()
                reservations = self._load_reservations(provider)
                reservations.pop(reservation_id, None)
                self._reservation_file(provider).write_text(
                    json.dumps(reservations, separators=(",", ":")), encoding="utf-8"
                )
                with self.ledger_path.open("a", encoding="utf-8") as ledger:
                    ledger.write(json.dumps(row, separators=(",", ":")) + "\n")
                    ledger.flush()
                    os.fsync(ledger.fileno())
                self._reserved[provider] = sum(float(value["amount"]) for value in reservations.values())

    async def release(self, model, reservation_id):
        async with self._lock:
            provider = model.provider
            with self._provider_lock(provider):
                reservations = self._load_reservations(provider)
                reservations.pop(reservation_id, None)
                self._reservation_file(provider).write_text(
                    json.dumps(reservations, separators=(",", ":")), encoding="utf-8"
                )
                self._reserved[provider] = sum(float(value["amount"]) for value in reservations.values())


def _api_key(provider):
    env_name = {"deepseek": "DEEPSEEK_API_KEY", "openrouter": "OPENROUTER_API_KEY"}[provider]
    key = os.environ.get(env_name)
    if key:
        return key
    auth_path = os.environ.get("NS_B1_AUTH_JSON")
    if not auth_path:
        raise RuntimeError(f"Set {env_name} or NS_B1_AUTH_JSON")
    with open(auth_path, encoding="utf-8") as auth_file:
        return json.load(auth_file)[provider]["key"]


async def chat(messages, model="deepseek-v4-flash", *, temperature=0.0,
               max_tokens=512, ledger_path=None, tag="", budget=None,
               client=None, semaphore=None, retries=3, backoff=1.0):
    """Call a registered model and return ChatResult; every HTTP response is billed."""
    if model not in MODELS:
        raise ValueError(f"Unknown model: {model}")
    if ledger_path is None and budget is None:
        raise ValueError("ledger_path or budget is required")
    spec = MODELS[model]
    if budget is None:
        budget_key = str(Path(ledger_path).resolve())
        if budget_key not in _BUDGETS:
            _BUDGETS[budget_key] = Budget(ledger_path)
        budget = _BUDGETS[budget_key]
    elif ledger_path is not None and Path(ledger_path) != budget.ledger_path:
        raise ValueError("ledger_path must match budget.ledger_path")
    own_client = client is None
    client = client or httpx.AsyncClient(timeout=180)
    payload = {
        "model": spec.provider_model_id,
        "messages": messages,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }
    if spec.provider == "deepseek":
        if spec.supports_temperature:
            payload["temperature"] = temperature
        payload["thinking"] = {"type": "disabled"}
    else:
        if spec.supports_temperature:
            payload["temperature"] = temperature
        if spec.provider_order is not None:
            payload["provider"] = {
                "order": spec.provider_order,
                "allow_fallbacks": False,
                "data_collection": "deny",
            }
        payload["reasoning"] = {"enabled": False}
    headers = {"Authorization": " ".join(("Bearer", _api_key(spec.provider)))}
    def ledger_row(cost, **fields):
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": spec.provider, "model": model,
            "prompt_tokens": 0, "completion_tokens": 0,
            "cost_usd": cost, "tag": tag,
            "temperature_sent": spec.supports_temperature, **fields,
        }

    try:
        for attempt in range(retries):
            reservation_id, estimate = await budget.reserve(spec, messages, max_tokens)
            try:
                async def send():
                    return await client.post(spec.endpoint, json=payload, headers=headers)
                if semaphore is None:
                    response = await send()
                else:
                    async with semaphore:
                        response = await send()
            except httpx.TransportError as exc:
                await budget.record(spec, reservation_id, estimate, ledger_row(
                    estimate, billed_conservatively=True, error_class=type(exc).__name__
                ))
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(backoff * (2 ** attempt))
                continue

            if response.status_code >= 500:
                error = httpx.HTTPStatusError(
                    f"Server error {response.status_code}", request=response.request, response=response
                )
                await budget.record(spec, reservation_id, estimate, ledger_row(
                    estimate, billed_conservatively=True, error_class=type(error).__name__,
                    status_code=response.status_code,
                ))
                if attempt == retries - 1:
                    raise error
                await asyncio.sleep(backoff * (2 ** attempt))
                continue

            if response.status_code >= 400 and response.status_code != 429:
                await budget.record(spec, reservation_id, estimate,
                                    ledger_row(0.0, status_code=response.status_code))
                response.raise_for_status()
            if response.status_code == 429:
                await budget.record(spec, reservation_id, estimate,
                                    ledger_row(0.0, status_code=response.status_code))
                if attempt == retries - 1:
                    response.raise_for_status()
                await asyncio.sleep(backoff * (2 ** attempt))
                continue

            try:
                response_data = response.json() if response.content else {}
            except (ValueError, json.JSONDecodeError):
                response_data = {}
            if not isinstance(response_data, dict):
                response_data = {}
            usage = response_data.get("usage") or {}
            if not isinstance(usage, dict):
                usage = {}
            has_counts = "prompt_tokens" in usage and "completion_tokens" in usage
            prompt_tokens = int(usage.get("prompt_tokens", 0) or 0)
            completion_tokens = int(usage.get("completion_tokens", 0) or 0)
            missing = not has_counts
            cache_hit = usage.get("prompt_cache_hit_tokens")
            cache_miss = usage.get("prompt_cache_miss_tokens")
            if missing:
                cost = estimate
            elif spec.provider == "deepseek" and spec.cached_input_usd_per_million is not None \
                    and cache_hit is not None and cache_miss is not None:
                cost = (int(cache_hit) * spec.cached_input_usd_per_million +
                        int(cache_miss) * spec.input_usd_per_million +
                        completion_tokens * spec.output_usd_per_million) / 1_000_000
            elif usage.get("cost") is not None:
                cost = float(usage["cost"])
            else:
                cost = (prompt_tokens * spec.input_usd_per_million +
                        completion_tokens * spec.output_usd_per_million) / 1_000_000
            cost = float(cost)
            choice = (response_data.get("choices") or [{}])[0]
            text = (choice.get("message") or {}).get("content")
            row = ledger_row(cost, prompt_tokens=prompt_tokens,
                             completion_tokens=completion_tokens)
            provider_name = response_data.get("provider")
            served_by = provider_name
            if isinstance(provider_name, str) and spec.provider_order is not None:
                served_by = next(
                    (allowed for allowed in spec.provider_order
                     if provider_name.casefold() == allowed.casefold()),
                    provider_name,
                )
            if spec.provider == "openrouter":
                row["served_by"] = served_by
                if provider_name != served_by:
                    row["served_by_raw"] = provider_name
            mismatch = spec.provider_order is not None and (
                not served_by or served_by not in spec.provider_order
            )
            if mismatch:
                row["provider_mismatch"] = True
            if missing:
                row["usage_missing"] = True
            if cache_hit is not None and cache_miss is not None:
                row["prompt_cache_hit_tokens"] = int(cache_hit)
                row["prompt_cache_miss_tokens"] = int(cache_miss)
            await budget.record(spec, reservation_id, estimate, row)
            if mismatch:
                raise ProviderMismatch(
                    f"Expected provider in {spec.provider_order!r}, got {served_by!r}"
                )
            return ChatResult(text, prompt_tokens, completion_tokens, cost, response_data)
    except BaseException:
        # Every attempted request is recorded before control reaches this point.
        raise
    finally:
        if own_client:
            await client.aclose()


def extract_json(text):
    """Parse JSON output, tolerating a short wrapper around the first object."""
    if isinstance(text, ChatResult):
        text = text.text
    if not text:
        return None
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        if start < 0:
            return None
        depth = 0
        for index in range(start, len(text)):
            if text[index] == "{":
                depth += 1
            elif text[index] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:index + 1])
                    except json.JSONDecodeError:
                        return None
    return None
