import json
import asyncio
import sys
import subprocess
import textwrap
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from v2.llm import Budget, BudgetExceeded, ProviderMismatch, chat, extract_json
from v2.models import MODELS


def test_kimi_reviewer_model_entry():
    model = MODELS["moonshotai/kimi-k3.1-pro"]
    assert (model.provider, model.provider_model_id) == (
        "openrouter", "moonshotai/kimi-k3.1-pro")
    assert model.provider_order == ["moonshotai"]
    assert model.input_usd_per_million == 2.0
    assert model.output_usd_per_million == 10.0
    assert model.supports_temperature is False


def reply(content='{"ok": true}', usage=None):
    return {
        "choices": [{"message": {"content": content}}],
        "usage": usage or {"prompt_tokens": 10, "completion_tokens": 4},
    }


def test_success_and_usage_cost_accounting(tmp_path, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    ledger = tmp_path / "ledger.jsonl"
    seen = {}

    def handler(request):
        seen.update(json.loads(request.content))
        return httpx.Response(200, json=reply(usage={
            "prompt_tokens": 10, "completion_tokens": 4, "cost": 0.0123
        }))

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    async def run():
        try:
            return await chat([{"role": "user", "content": "say JSON"}],
                              ledger_path=ledger, tag="success", client=client)
        finally:
            await client.aclose()
    result = asyncio.run(run())
    assert result.text == '{"ok": true}'
    assert (result.prompt_tokens, result.completion_tokens, result.cost_usd) == (10, 4, 0.0123)
    assert seen["thinking"] == {"type": "disabled"}
    assert seen["response_format"] == {"type": "json_object"}
    assert seen["max_tokens"] == 512
    assert seen["temperature"] == 0.0 and "provider" not in seen
    row = json.loads(ledger.read_text())
    assert row["cost_usd"] == 0.0123 and row["tag"] == "success"
    assert row["model"] == "deepseek-v4-flash"
    assert row["temperature_sent"] is True


@pytest.mark.parametrize("model,provider", [
    ("anthropic/claude-haiku-5.5", "anthropic"),
    ("openai/gpt-6-luna", "openai"),
])
def test_pinned_openrouter_provider_and_unsupported_temperature(
        tmp_path, monkeypatch, model, provider):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    ledger = tmp_path / "ledger.jsonl"
    seen = {}

    def handler(request):
        seen.update(json.loads(request.content))
        return httpx.Response(200, json={**reply(), "provider": provider})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    async def run():
        try:
            return await chat([{"role": "user", "content": "say JSON"}],
                              model=model, ledger_path=ledger, tag="pinned",
                              client=client)
        finally:
            await client.aclose()

    asyncio.run(run())
    assert seen["provider"] == {
        "order": [provider], "allow_fallbacks": False, "data_collection": "deny"
    }
    assert "temperature" not in seen
    row = json.loads(ledger.read_text())
    assert row["served_by"] == provider
    assert row["temperature_sent"] is False


def test_pinned_provider_mismatch_is_charged(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    ledger = tmp_path / "ledger.jsonl"
    client = httpx.AsyncClient(transport=httpx.MockTransport(
        lambda _request: httpx.Response(200, json={**reply(), "provider": "google"})))

    async def run():
        try:
            with pytest.raises(ProviderMismatch):
                await chat([{"role": "user", "content": "json"}],
                           model="anthropic/claude-haiku-5.5", ledger_path=ledger,
                           max_tokens=20, client=client)
        finally:
            await client.aclose()

    asyncio.run(run())
    row = json.loads(ledger.read_text())
    assert row["served_by"] == "google"
    assert row["provider_mismatch"] is True
    assert row["cost_usd"] > 0


def test_retry_then_success(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    attempts = 0

    def handler(_request):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(503, json={"error": "retry"})
        return httpx.Response(200, json={**reply(), "provider": "alibaba"})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    async def run():
        try:
            return await chat([{"role": "user", "content": "json"}],
                              model="qwen/qwen3.8-flash", ledger_path=tmp_path / "ledger.jsonl",
                              client=client, backoff=0)
        finally:
            await client.aclose()
    result = asyncio.run(run())
    assert attempts == 2
    assert result.text == '{"ok": true}'
    rows = [json.loads(line) for line in (tmp_path / "ledger.jsonl").read_text().splitlines()]
    assert len(rows) == 2
    assert rows[0]["billed_conservatively"] is True
    assert rows[0]["error_class"] == "HTTPStatusError"
    assert rows[0]["status_code"] == 503
    assert rows[0]["cost_usd"] > 0


def test_json_extraction():
    assert extract_json('prefix {"ok": true} suffix') == {"ok": True}
    assert extract_json("not json") is None


def test_ledger_restart_reloads_totals(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(json.dumps({"provider": "openrouter", "cost_usd": 1.25}) + "\n")
    budget = Budget(ledger)
    assert budget.totals["openrouter"] == 1.25


def test_budget_cap_refuses_before_sending(tmp_path, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(json.dumps({"provider": "deepseek", "cost_usd": 7.999999}) + "\n")
    budget = Budget(ledger, caps={"deepseek": 8.0})
    calls = 0

    def handler(_request):
        nonlocal calls
        calls += 1
        return httpx.Response(200, json=reply())

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    async def run():
        try:
            with pytest.raises(BudgetExceeded):
                await chat([{"role": "user", "content": "x"}], ledger_path=ledger,
                           budget=budget, max_tokens=10, client=client)
        finally:
            await client.aclose()
    asyncio.run(run())
    assert calls == 0


@pytest.mark.parametrize("usage", [None, {"prompt_tokens": 10}])
def test_missing_usage_charged_at_reservation(tmp_path, monkeypatch, usage):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    ledger = tmp_path / "ledger.jsonl"
    body = reply(usage=usage)
    if usage is None:
        body.pop("usage")
    client = httpx.AsyncClient(transport=httpx.MockTransport(
        lambda _request: httpx.Response(200, json=body)))

    async def run():
        try:
            await chat([{"role": "user", "content": "unknown"}], ledger_path=ledger,
                       max_tokens=20, client=client)
        finally:
            await client.aclose()
    asyncio.run(run())
    row = json.loads(ledger.read_text())
    assert row["usage_missing"] is True
    assert row["cost_usd"] == Budget.estimate(
        __import__("v2.models", fromlist=["MODELS"]).MODELS["deepseek-v4-flash"],
        [{"role": "user", "content": "unknown"}], 20)


def test_transport_failure_is_charged_before_retry(tmp_path, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    calls = 0

    def handler(_request):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise httpx.ReadTimeout("timed out")
        return httpx.Response(200, json=reply())

    ledger = tmp_path / "ledger.jsonl"
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    async def run():
        try:
            await chat([{"role": "user", "content": "retry"}], ledger_path=ledger,
                       max_tokens=20, client=client, backoff=0)
        finally:
            await client.aclose()
    asyncio.run(run())
    rows = [json.loads(line) for line in ledger.read_text().splitlines()]
    assert calls == 2 and len(rows) == 2
    assert rows[0]["billed_conservatively"] is True
    assert rows[0]["error_class"] == "ReadTimeout"
    assert rows[0]["cost_usd"] == rows[1]["cost_usd"] or rows[0]["cost_usd"] > rows[1]["cost_usd"]


def test_client_error_is_recorded_at_zero(tmp_path, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    ledger = tmp_path / "ledger.jsonl"
    client = httpx.AsyncClient(transport=httpx.MockTransport(
        lambda _request: httpx.Response(400, json={"error": "bad request"})))

    async def run():
        try:
            with pytest.raises(httpx.HTTPStatusError):
                await chat([{"role": "user", "content": "bad"}], ledger_path=ledger,
                           max_tokens=20, client=client)
        finally:
            await client.aclose()
    asyncio.run(run())
    row = json.loads(ledger.read_text())
    assert row["cost_usd"] == 0 and row["status_code"] == 400


def test_deepseek_cache_usage_uses_cached_price(tmp_path, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    ledger = tmp_path / "ledger.jsonl"
    usage = {"prompt_tokens": 100, "completion_tokens": 5,
             "prompt_cache_hit_tokens": 70, "prompt_cache_miss_tokens": 30}
    client = httpx.AsyncClient(transport=httpx.MockTransport(
        lambda _request: httpx.Response(200, json=reply(usage=usage))))

    async def run():
        try:
            result = await chat([{"role": "user", "content": "cached"}],
                                ledger_path=ledger, client=client)
            return result
        finally:
            await client.aclose()
    result = asyncio.run(run())
    assert result.cost_usd == pytest.approx((70 * .006 + 30 * .30 + 5 * 1.20) / 1_000_000)
    row = json.loads(ledger.read_text())
    assert row["prompt_cache_hit_tokens"] == 70
    assert row["prompt_cache_miss_tokens"] == 30


def test_two_processes_share_provider_cap(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    code = textwrap.dedent("""
        import asyncio, json, os, sys
        import httpx
        sys.path.insert(0, sys.argv[1])
        from v2.llm import Budget, chat, BudgetExceeded
        from v2.models import MODELS
        ledger = sys.argv[2]
        messages = [{"role": "user", "content": "process"}]
        model = MODELS["deepseek-v4-flash"]
        cap = Budget.estimate(model, messages, 20)
        def handler(_request):
            return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "cost": cap}})
        async def main():
            client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
            budget = Budget(ledger, caps={"deepseek": cap})
            try:
                await chat(messages, ledger_path=ledger, budget=budget, max_tokens=20, client=client)
                print("sent")
            except BudgetExceeded:
                print("blocked")
            finally:
                await client.aclose()
        asyncio.run(main())
    """)
    source = str(Path(__file__).resolve().parents[2] / "src")
    procs = [subprocess.Popen([sys.executable, "-c", code, source, str(ledger)],
                              env={**__import__("os").environ, "DEEPSEEK_API_KEY": "test-key"},
                              stdout=subprocess.PIPE, text=True) for _ in range(2)]
    outputs = [proc.communicate(timeout=20)[0].strip() for proc in procs]
    assert sorted(outputs) == ["blocked", "sent"]
    rows = [json.loads(line) for line in ledger.read_text().splitlines()]
    assert sum(row["cost_usd"] for row in rows if row["provider"] == "deepseek") <= Budget.estimate(
        __import__("v2.models", fromlist=["MODELS"]).MODELS["deepseek-v4-flash"],
        [{"role": "user", "content": "process"}], 20)

