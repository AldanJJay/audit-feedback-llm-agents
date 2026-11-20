"""Post hoc operational benchmark; never writes confirmatory data or ledgers.

Run pilot first, then obtain study-maintainer approval before invoking --stage full.
The full stage uses disjoint decisions and measures both probe schedules at c=1.
Use --summarize-only to rebuild derived outputs offline, without creating a client.
"""

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import random
import socket
import statistics
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import httpx

from .attribution import _current_features, _perturbed_messages
from .conditions import HISTORY_K, PERSONAS, build_messages
from .llm import Budget, BudgetExceeded, _api_key, chat
from .models import MODELS
from .simulate import _fake_decision, _valid_decision, model_slug

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data/v2/latency'
LEDGER = ROOT / 'data/v2/latency_ledger.jsonl'
STUDY_MODELS = ('deepseek-v4-flash', 'anthropic/claude-haiku-5.5', 'openai/gpt-6-luna')
SEED = 20261119
MAX_TOKENS = 512
CAPS = {'deepseek': 0.50, 'openrouter': 0.50}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def reconstruct_file(path):
    """Replay settlement from logged prices/orders/fines, checking every wealth.

    Logged feedback is the input feedback, not the newly generated audit event.
    No market re-simulation, inferred actions, or synthetic prompt formats are used.
    """
    rows = read_jsonl(path)
    if not rows or rows[-1].get('status') != 'complete':
        raise ValueError(f'Incomplete confirmatory source: {path}')
    markets = {r['tick']: r for r in rows if r['type'] == 'market'}
    decisions = defaultdict(list)
    for row in rows:
        if row['type'] == 'decision':
            decisions[row['tick']].append(row)
    portfolios = [dict(cash=p['cash'], position=p['position']) for p in PERSONAS]
    history, previous_price, selected = [], 100.0, []
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    for tick in sorted(markets):
        market = markets[tick]
        for row in sorted(decisions[tick], key=lambda r: r['agent']):
            index = row['agent']
            p = portfolios[index]
            persona = PERSONAS[index]
            if row['persona'] != persona['name']:
                raise ValueError('Persona mismatch')
            messages = build_messages(market['features'], p['cash'] + p['position'] * previous_price,
                                      p['position'], row['condition'], persona, row['feedback'], history[-HISTORY_K:])
            if 20 <= tick <= 39:
                selected.append({
                    'source': str(path.relative_to(ROOT)), 'source_sha256': digest,
                    'tick': tick, 'agent': index, 'condition': row['condition'],
                    'regime': row['regime'], 'messages': messages,
                })
            price = market['price']
            if row['fined']:
                p['cash'] *= 0.9
                p['position'] *= 0.9
            if row['parse_ok']:
                units = min(row['size'], p['cash'] / price) if row['action'] == 'buy' else min(row['size'], p['position'])
                if row['action'] == 'buy':
                    p['cash'] -= units * price
                    p['position'] += units
                else:
                    p['cash'] += units * price
                    p['position'] -= units
            wealth = p['cash'] + p['position'] * price
            if not math.isclose(wealth, row['wealth'], rel_tol=1e-12, abs_tol=1e-8):
                raise ValueError(f'Portfolio replay mismatch: {path}, tick={tick}, agent={index}')
        history.append((market['features'], market['return']))
        previous_price = market['price']
    return selected


def select_samples(model, count=105, root=ROOT):
    """Fixed-seed, balanced round-robin sampling of six condition/regime cells."""
    rng = random.Random(f'{SEED}:{model}')
    cells = defaultdict(list)
    for condition in ('naive', 'label', 'evidence'):
        for path in sorted((root / 'data/v2' / model_slug(model) / 'confirm').glob(f'{condition}_seed_*.jsonl')):
            for decision in reconstruct_file(path):
                cells[(condition, decision['regime'])].append(decision)
    if len(cells) != 6:
        raise ValueError(f'Missing sampling cells for {model}')
    keys = sorted(cells)
    rng.shuffle(keys)
    for values in cells.values():
        rng.shuffle(values)
    sample = []
    for index in range(count):
        cell = cells[keys[index % len(keys)]]
        if not cell:
            raise ValueError('Insufficient disjoint decisions')
        decision = cell.pop()
        decision['decision_id'] = hashlib.sha256(
            f"{model}:{decision['source']}:{decision['tick']}:{decision['agent']}".encode()).hexdigest()[:20]
        sample.append(decision)
    return sample


class TrackingBudget(Budget):
    def __init__(self, ledger_path):
        super().__init__(ledger_path, caps=CAPS)
        self.events = defaultdict(list)

    async def record(self, model, reservation_id, estimate, row):
        await super().record(model, reservation_id, estimate, row)
        self.events[row['tag']].append(row)


class TimedClient:
    def __init__(self, client):
        self.client = client
        self.attempts = []

    async def post(self, url, **kwargs):
        start = time.monotonic()
        row = {'start_monotonic_s': start, 'start_utc': utc_now(), 'http_status': None}
        try:
            response = await self.client.post(url, **kwargs)
            row['http_status'] = response.status_code
            return response
        except httpx.TransportError as exc:
            row['error_class'] = type(exc).__name__
            raise
        finally:
            row['end_monotonic_s'] = time.monotonic()
            row['latency_s'] = row['end_monotonic_s'] - start
            row['end_utc'] = utc_now()
            self.attempts.append(row)


def fake_client():
    async def handler(request):
        payload = json.loads(request.content)
        spec = MODELS[payload['model']]
        await asyncio.sleep(0.001)
        return httpx.Response(200, json={
            'provider': spec.provider_order[0] if spec.provider_order else 'deepseek',
            'choices': [{'message': {'content': _fake_decision(payload['messages'])}}],
            'usage': {'prompt_tokens': 900, 'completion_tokens': 30, 'cost': 0.000105},
        })
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def balances(client):
    result = {}
    for provider, url in [('deepseek', 'https://api.deepseek.com/user/balance'),
                          ('openrouter', 'https://openrouter.ai/api/v1/credits')]:
        response = await client.get(url, headers={'Authorization': ' '.join(('Bearer', _api_key(provider)))})
        response.raise_for_status()
        data = response.json()
        if provider == 'deepseek':
            usd = [item for item in data['balance_infos'] if item['currency'] == 'USD']
            if len(usd) != 1:
                raise ValueError('Expected one USD DeepSeek balance')
            remaining = float(usd[0]['total_balance'])
        else:
            remaining = float(data['data']['total_credits']) - float(data['data']['total_usage'])
        result[provider] = {'remaining_usd': remaining, 'checked_utc': utc_now()}
    return result


async def request_one(decision, probe, messages, *, model, stage, concurrency, schedule,
                      budget, client, output):
    tag = f"latency:{stage}:{model}:{decision['decision_id']}:{probe}"
    timed = TimedClient(client)
    start, started = time.monotonic(), utc_now()
    response, error = None, None
    try:
        response = await chat(messages, model=model, temperature=0.0, max_tokens=MAX_TOKENS,
                              budget=budget, tag=tag, client=timed)
    except Exception as exc:
        error = type(exc).__name__  # Never persist request headers or credentials.
    end = time.monotonic()
    events = budget.events.pop(tag, [])
    parsed = _valid_decision(response.text) if response else None
    row = {key: value for key, value in decision.items() if key != 'messages'}
    row.update(model=model, provider=MODELS[model].provider, stage=stage,
               concurrency=concurrency, schedule=schedule, probe=probe,
               messages=messages, prompt_sha256=hashlib.sha256(json.dumps(messages, sort_keys=True).encode()).hexdigest(),
               start_utc=started, end_utc=utc_now(), start_monotonic_s=start,
               end_monotonic_s=end, latency_s=end-start, attempts=timed.attempts,
               http_status=timed.attempts[-1]['http_status'] if timed.attempts else None,
               retries=max(0, len(timed.attempts)-1),
               count_429=sum(a['http_status'] == 429 for a in timed.attempts),
               count_5xx=sum(a['http_status'] is not None and a['http_status'] >= 500 for a in timed.attempts),
               prompt_tokens=sum(e['prompt_tokens'] for e in events),
               completion_tokens=sum(e['completion_tokens'] for e in events),
               cost_usd=sum(e['cost_usd'] for e in events), cost_records=events,
               cost_basis=('native_token_price_estimate' if MODELS[model].provider == 'deepseek'
                           else 'reported_usage_cost_or_study_token_price'),
               charged_cost_usd=(None if MODELS[model].provider == 'deepseek' or
                                 any(e.get('billed_conservatively') or e.get('usage_missing') for e in events) else
                                 sum(e['cost_usd'] for e in events)),
               served_provider=((response.response.get('provider') or 'deepseek') if response and
                                MODELS[model].provider == 'deepseek' else
                                response.response.get('provider') if response else
                                next((e.get('served_by_raw') or e.get('served_by') for e in reversed(events)
                                      if e.get('served_by_raw') or e.get('served_by')), None)),
               valid=parsed is not None, action=parsed['action'] if parsed else None,
               response_text=response.text if response else None, error_class=error)
    output.write(json.dumps(row, separators=(',', ':')) + '\n')
    output.flush()
    if error in ('BudgetExceeded', 'ProviderMismatch'):
        raise RuntimeError(f'Benchmark stopped: {error}')
    return row


async def audit_one(decision, *, model, stage, concurrency, schedule, budget, client, output):
    kwargs = dict(model=model, stage=stage, concurrency=concurrency, schedule=schedule,
                  budget=budget, client=client, output=output)
    messages = decision['messages']
    base = await request_one(decision, 'base', messages, **kwargs)
    current = _current_features(messages)
    probes = [('news', _perturbed_messages(messages, 'news', -current['news'])),
              ('momentum', _perturbed_messages(messages, 'momentum', -current['momentum'])),
              ('null', [dict(m) for m in messages])]
    if schedule == 'parallel':
        rows = await asyncio.gather(*(request_one(decision, probe, prompt, **kwargs) for probe, prompt in probes),
                                    return_exceptions=True)
        for row in rows:
            if isinstance(row, BaseException):
                raise row
    else:
        rows = [await request_one(decision, probe, prompt, **kwargs) for probe, prompt in probes]
    return [base, *rows]


def percentiles(values):
    if not values:
        return None
    values = sorted(values)
    def quantile(p):
        x = (len(values)-1)*p
        lo, hi = math.floor(x), math.ceil(x)
        return values[lo] + (values[hi]-values[lo])*(x-lo)
    return {'n': len(values), 'median': statistics.median(values), 'p90': quantile(.90),
            'p95': quantile(.95), 'max': max(values)}


def group_summary(rows):
    decisions = defaultdict(list)
    for row in rows:
        decisions[(row['model'], row['stage'], row['concurrency'], row['schedule'], row['decision_id'])].append(row)
    complete = [group for group in decisions.values()
                if len(group) == 4 and {r['probe'] for r in group} == {'base', 'news', 'momentum', 'null'}]
    probe_groups = [[r for r in group if r['probe'] != 'base'] for group in decisions.values()]
    probe_groups = [group for group in probe_groups
                    if len(group) == 3 and {r['probe'] for r in group} == {'news', 'momentum', 'null'}]
    sidecar = [max(r['end_monotonic_s'] for r in group) - min(r['start_monotonic_s'] for r in group)
               for group in probe_groups]
    sequential = [sum(r['latency_s'] for r in group) for group in complete]
    parallel = [next(r['latency_s'] for r in group if r['probe'] == 'base') +
                max(r['latency_s'] for r in group if r['probe'] != 'base') for group in complete]
    observed = [max(r['end_monotonic_s'] for r in group) - min(r['start_monotonic_s'] for r in group)
                for group in complete]
    attempts = [a for r in rows for a in r['attempts']]
    routing_deviations = sum(
        r['error_class'] == 'ProviderMismatch' or
        (r['error_class'] is None and bool(MODELS[r['model']].provider_order) and
        (r['served_provider'] or '').casefold() not in
        [p.casefold() for p in MODELS[r['model']].provider_order]) for r in rows)
    changes = {}
    for probe in ('news', 'momentum', 'null'):
        pairs = [(next(r for r in g if r['probe'] == 'base'), next(r for r in g if r['probe'] == probe))
                 for g in complete]
        valid = [(a,b) for a,b in pairs if a['valid'] and b['valid']]
        changes[probe] = {'valid_pairs': len(valid), 'changes': sum(a['action'] != b['action'] for a,b in valid),
                          'rate': sum(a['action'] != b['action'] for a,b in valid)/len(valid) if valid else None}
    return {'requests': len(rows), 'valid_requests': sum(r['valid'] for r in rows),
            'complete_decisions': len(complete), 'latency_s': percentiles([r['latency_s'] for r in rows]),
            'http_attempt_latency_s': percentiles([a['latency_s'] for a in attempts]),
            'client_overhead_including_backoff_s': percentiles([
                r['latency_s'] - sum(a['latency_s'] for a in r['attempts']) for r in rows]),
            'sequential_sum_s': percentiles(sequential), 'parallel_critical_path_s': percentiles(parallel),
            'sidecar_added_latency_s': percentiles(sidecar),
            'observed_audit_s': percentiles(observed), 'cost_usd': sum(r['cost_usd'] for r in rows),
            'probe_cost_usd': sum(r['cost_usd'] for r in rows if r['probe'] != 'base'),
            'cost_per_audited_decision_usd': sum(r['cost_usd'] for r in rows)/len(complete) if complete else None,
            'probe_cost_per_audited_decision_usd': (
                sum(r['cost_usd'] for r in rows if r['probe'] != 'base')/len(probe_groups) if probe_groups else None),
            'request_utc_window': {'start': min(r['start_utc'] for r in rows),
                                   'end': max(r['end_utc'] for r in rows)} if rows else None,
            'errors': sum(r['error_class'] is not None for r in rows),
            'invalid_responses': sum(not r['valid'] and r['error_class'] is None for r in rows),
            'invalid_request_share': sum(not r['valid'] for r in rows)/len(rows) if rows else None,
            'invalid_response_share_among_returned': (
                sum(not r['valid'] and r['error_class'] is None for r in rows) /
                sum(r['error_class'] is None for r in rows)
                if any(r['error_class'] is None for r in rows) else None),
            'provider_routing_deviations': routing_deviations,
            'http_attempts': len(attempts), 'retries': sum(r['retries'] for r in rows),
            'count_429': sum(r['count_429'] for r in rows), 'count_5xx': sum(r['count_5xx'] for r in rows),
            'error_rate': sum(r['error_class'] is not None for r in rows)/len(rows) if rows else None,
            'rate_429': sum(a['http_status'] == 429 for a in attempts)/len(attempts) if attempts else None,
            'action_changes_sanity_only': changes}


def append_amendment_report(lines, result):
    def pair(stats):
        return f'{stats["median"]:.6f} / {stats["p95"]:.6f}'

    lines.extend(['## Measured sidecar-added latency (probes only)', '',
                  'Base excluded; n counts decisions with exactly one news, momentum and null probe. Each span runs from first probe start to last probe end. Full-run and pilot groups remain separate.', '',
                  '| Model / stage / concurrency / schedule | n | Median / p90 / p95 / max added latency (s) |',
                  '|---|---:|---:|'])
    for stage_key in ('models', 'pilot_models'):
        for model,entry in result[stage_key].items():
            for key,group in entry['by_stage_concurrency_schedule'].items():
                stats = group['sidecar_added_latency_s']
                if stats:
                    values = ' / '.join(f'{stats[q]:.6f}' for q in ('median','p90','p95','max'))
                    lines.append(f'| {model} / {key} | {stats["n"]} | {values} |')
    checks = []
    for model,expected in zip(STUDY_MODELS,(.82,1.78,1.37)):
        group = result['models'].get(model,{}).get('by_stage_concurrency_schedule',{}).get('full:c1:parallel')
        if group and group['sidecar_added_latency_s']:
            actual = group['sidecar_added_latency_s']['median']
            checks.append(f'{model}: {actual:.6f} s (reference rounded check {expected:.2f} s; {"matches" if round(actual,2) == expected else "differs"})')
    lines.extend(['', 'Reference reconciliation: ' + '; '.join(checks) + '. The larger base-inclusive observed audit medians below measure a different interval.', '',
                  '## Pilot measurements (separate from main statistics)', '',
                  '| Model | Valid / total | Request median / p95 (s) | Base-inclusive observed audit median / p95 (s) | Cost USD | Request UTC window |',
                  '|---|---:|---:|---:|---:|---|'])
    for model,entry in result['pilot_models'].items():
        lines.append(f'| {model} | {entry["valid_requests"]}/{entry["requests"]} | {pair(entry["latency_s"])} | {pair(entry["observed_audit_s"])} | {entry["cost_usd"]:.9f} | {entry["request_utc_window"]} |')
    lines.extend(['', '## Temporal variability', ''])
    luna = 'openai/gpt-6-luna'
    pilot,full = result['pilot_models'].get(luna),result['models'].get(luna)
    if pilot and full:
        sequential = full['by_stage_concurrency_schedule'].get('full:c1:sequential')
        comparison = (f' Full-run c1 sequential base-inclusive audit median was {sequential["observed_audit_s"]["median"]:.6f} s (about {sequential["observed_audit_s"]["median"]:.1f} s).'
                      if sequential else '')
        lines.extend([f'Luna in the pilot stage (stage UTC window {next((m for m in result["stages"] if m["stage"] == "pilot"), {}).get("start_utc")} to {next((m for m in result["stages"] if m["stage"] == "pilot"), {}).get("end_utc")}; exact model request window {pilot["request_utc_window"]}) had request median / p95 {pair(pilot["latency_s"])} s ({pilot["latency_s"]["median"]:.2f} / {pilot["latency_s"]["p95"]:.2f} s) and base-inclusive observed audit median {pilot["observed_audit_s"]["median"]:.6f} s (about {pilot["observed_audit_s"]["median"]:.1f} s). Full-run Luna request median / p95 was {pair(full["latency_s"])} s (about {full["latency_s"]["median"]:.2f} / {full["latency_s"]["p95"]:.2f} s).{comparison}', ''])
    haiku = result['models'].get('anthropic/claude-haiku-5.5')
    if haiku:
        lines.extend([f'Haiku full-run maximum request latency was {haiku["latency_s"]["max"]:.6f} s ({haiku["latency_s"]["max"]:.2f} s).', ''])
    lines.extend(['One approximately 17-minute window from a single host cannot characterize provider latency distributions or tails. Pilot/full differences demonstrate temporal variability; chronology, disjoint prompts and network conditions prevent a causal attribution to provider load or concurrency.', '',
                  '## Facts for the manuscript', '',
                  'Full-run facts below exclude the pilot. Times are seconds, displayed to six decimals; unrounded values are in summary.json. Costs distinguish the three deployment probes from the four-call benchmark protocol. Concurrency ratios are descriptive comparisons between separate time windows and samples.', ''])
    for model,entry in result['models'].items():
        groups = entry['by_stage_concurrency_schedule']
        seq,par = groups.get('full:c1:sequential'),groups.get('full:c1:parallel')
        facts = [f'{model}: {entry["requests"]} requests / {entry["complete_decisions"]} audited decisions; per-request median / p95 {pair(entry["latency_s"])} s']
        if seq and par:
            facts.append(f'c1 probes-only median / p95 sequential {pair(seq["sidecar_added_latency_s"])} s versus parallel {pair(par["sidecar_added_latency_s"])} s')
        for c in (4,8):
            group = groups.get(f'full:c{c}:parallel')
            if group:
                facts.append(f'c{c} parallel request median / p95 {pair(group["latency_s"])} s ({group["median_latency_inflation_vs_full_c1_parallel"]:.6f}x c1 request median), probes-only median / p95 {pair(group["sidecar_added_latency_s"])} s ({group["median_sidecar_inflation_vs_full_c1_parallel"]:.6f}x c1 probes-only median)')
        facts.extend([f'errors / 429 / 5xx / retries / invalid {entry["errors"]} / {entry["count_429"]} / {entry["count_5xx"]} / {entry["retries"]} / {entry["requests"]-entry["valid_requests"]}',
                      f'USD per audited decision: probes only {entry["probe_cost_per_audited_decision_usd"]:.9f}, base plus probes {entry["cost_per_audited_decision_usd"]:.9f}',
                      f'full model request UTC window {entry["request_utc_window"]}'])
        lines.append('- ' + '; '.join(facts) + '.')
    lines.extend(['', f'- Overall stage UTC window (pilot included): {result["run_utc_window"]}; total cost USD {result["total_cost_usd"]:.9f}. DeepSeek costs are estimates from recorded token/cache usage and the study price snapshot; OpenRouter costs use reported charges.', ''])


def summarize(out, ledger):
    rows = read_jsonl(out / 'requests.jsonl')
    metadata = sorted([json.loads(p.read_text()) for p in out.glob('*.stage.json')], key=lambda r:r['start_utc'])
    result = {'post_hoc_operational_only': True, 'seed': SEED, 'stages': metadata,
              'cost_by_provider_usd': {p: sum(r['cost_usd'] for r in read_jsonl(ledger) if r['provider'] == p) for p in CAPS},
              'main_statistics_stage': 'full', 'models': {}, 'pilot_models': {},
              'sidecar_added_latency_definition': 'Per decision: last probe end minus first probe start; news, momentum and null only; base excluded.',
              'input_sha256': {os.path.relpath(path.resolve(), ROOT): hashlib.sha256(path.read_bytes()).hexdigest()
                               for path in (out / 'requests.jsonl', ledger) if path.exists()}}
    result['total_cost_usd'] = sum(result['cost_by_provider_usd'].values())
    result['run_utc_window'] = {'start':metadata[0]['start_utc'], 'end':metadata[-1].get('end_utc')} if metadata else None
    validation_path = out / 'validation.json'
    if validation_path.exists():
        result['validation'] = json.loads(validation_path.read_text())
    for stage,model in ((stage,model) for stage in ('full','pilot') for model in STUDY_MODELS):
        subset = [r for r in rows if r['model'] == model and r['stage'] == stage]
        if not subset:
            continue
        entry = group_summary(subset)
        entry['by_stage_concurrency_schedule'] = {}
        for stage,c,s in sorted({(r['stage'], r['concurrency'], r['schedule']) for r in subset}):
            group = [r for r in subset if (r['stage'],r['concurrency'],r['schedule']) == (stage,c,s)]
            entry['by_stage_concurrency_schedule'][f'{stage}:c{c}:{s}'] = group_summary(group)
        baseline = entry['by_stage_concurrency_schedule'].get('full:c1:parallel')
        for key,group in entry['by_stage_concurrency_schedule'].items():
            group['median_latency_inflation_vs_full_c1_parallel'] = (
                group['latency_s']['median']/baseline['latency_s']['median'] if baseline else None)
            group['median_sidecar_inflation_vs_full_c1_parallel'] = (
                group['sidecar_added_latency_s']['median']/baseline['sidecar_added_latency_s']['median']
                if baseline and group['sidecar_added_latency_s'] and baseline['sidecar_added_latency_s'] else None)
        result['models' if stage == 'full' else 'pilot_models'][model] = entry
    write_json(out / 'summary.json', result)
    lines = ['# Post hoc audit-sidecar latency benchmark', '',
             'November 2026 operational measurement; separate from the preregistered study.', '',
             f'Fixed sample seed: {SEED}. Total cost: USD {result["total_cost_usd"]:.8f}; cost by provider: {result["cost_by_provider_usd"]}.', '',
             f'Run UTC window: {result["run_utc_window"]}.', '',
             'Main statistics use full-run rows only; pilot measurements are reported separately. Costs and the overall run window above include both stages.', '',
             '## Measurement and limitations', '',
             '- Prompts use the original build_messages and _perturbed_messages functions, with max_tokens=512 and unchanged study provider routing/parameters.',
             '- Portfolios are replayed from initial personas and logged actions, settlement prices and 10% fines; every logged wealth is checked. Features, input feedback and completed history come directly from confirmatory logs. No prompt-state approximation is used.',
             '- Each decision has a fresh base response, news and momentum sign flips, and an identical-prompt null. Action-change rates are sanity checks, not inferential estimates.',
             '- Deployment sidecar-added latency is last probe end minus first probe start per decision, using only news, momentum and null re-asks. The agent decision already exists in deployment, so the benchmark base call is excluded. This is measured wall time, including gaps between probes and client overhead; it is not an arithmetic sum or maximum of durations.',
             '- Sequential sums and parallel critical paths are paired arithmetic estimates from the same four request latencies. They exclude orchestration overhead; the parallel estimate on sequential observations does not measure contention. Observed audit times are measured wall time, including scheduling; schedule-specific tables distinguish actual sequential and parallel execution.',
             '- Pilot: five decisions/model, sequential probes, one audited decision in flight. Full target: 60/model at c=1 split equally across sequential/parallel probes, then 20/model at c=4 and c=8 with parallel probes. Concurrency means audited decisions; up to 3*c probe HTTP calls may be in flight. Models are measured separately in bounded waves, rather than a steady-state load generator; the final wave may be smaller than the target concurrency.',
             '- End-to-end client request latency includes budget locks/reservation, HTTP attempts, retries/backoff, parsing and ledger writes. Pure HTTP attempt latency measures client.post through receipt of the full buffered response. Overhead is end-to-end latency minus the sum of attempt durations; it includes backoff when retries occur. At most three attempts/request use the study retry policy. No whole batch is retried.',
             '- OpenRouter charged cost uses reported usage.cost when supplied; native DeepSeek cost uses the study price snapshot and reported cache/token usage (an estimate of charge, not an invoice). Unknown charges on transport/5xx failures are conservatively reserved and labelled. Balance deltas may differ due to display precision, delayed usage reporting or other account activity. DeepSeek served provider is identified by the native endpoint; it does not independently report a served-provider field.',
             '- USD 0.50/provider reservations enforce the USD 1.00 aggregate cap in a separate latency ledger. Dry-run costs and timings are synthetic and must never be interpreted as measurements.',
             '- All calls originate from a single client host, a container in the research workspace. Physical host location, egress region, route and competing network load are not independently verified; timezone settings do not establish location. No streaming/TTFT is measured.',
             '- Percentiles use linear interpolation on order statistics; small-sample tail percentiles are descriptive only. The fixed condition/regime round-robin sample is not a population-representative efficacy sample.', '',
             '- Models and schedules run in a fixed chronological order with disjoint prompts. Concurrency inflation is descriptive and may include prompt composition, cache warming, provider load and time-of-run differences; it is not a randomized estimate of the effect of concurrency.', '',
             '## Runs', '']
    for item in metadata:
        lines.extend([f'### {item["stage"]}', '', '```json', json.dumps(item, indent=2), '```', ''])
    if result.get('validation'):
        lines.extend(['## Original run validation and deviations', '',
                      'Historical validation snapshot from the paid run; its test counts and code hashes predate this offline amendment. Current input hashes are in summary.json.', '',
                      '```json', json.dumps(result['validation'],indent=2), '```', ''])
    append_amendment_report(lines, result)
    lines.extend(['## Full-run per-model measurements', '',
                  '| Model / group | Requests valid/total | Median / p90 / p95 / max request (s) | Sequential sum median (s) | Parallel path median (s) | Observed audit median (s) | Errors / 429 / 5xx | Cost USD |',
                  '|---|---:|---:|---:|---:|---:|---:|---:|'])
    for model,entry in result['models'].items():
        for key,group in [('full only',entry), *entry['by_stage_concurrency_schedule'].items()]:
            def metric(name, quantile='median'):
                stats = group[name]
                return f'{stats[quantile]:.3f}' if stats else 'n/a'
            latency = ' / '.join(metric('latency_s', q) for q in ('median','p90','p95','max'))
            lines.append(f'| {model} / {key} | {group["valid_requests"]}/{group["requests"]} | {latency} | {metric("sequential_sum_s")} | {metric("parallel_critical_path_s")} | {metric("observed_audit_s")} | {group["errors"]} / {group["count_429"]} / {group["count_5xx"]} | {group["cost_usd"]:.6f} |')
    lines.extend(['', '## Full-run base-inclusive audit completion by actual schedule', '',
                  'These are observed four-call audit wall times, including the base call and orchestration. Deployment probes-only added latency is reported separately above. Arithmetic parallel-path estimates above are not measured parallel completion times.', '',
                  '| Model / actual schedule | Decisions | Median / p90 / p95 / max audit (s) |',
                  '|---|---:|---:|'])
    for model,entry in result['models'].items():
        for key,group in entry['by_stage_concurrency_schedule'].items():
            stats=group['observed_audit_s']
            if stats:
                values=' / '.join(f'{stats[q]:.3f}' for q in ('median','p90','p95','max'))
                lines.append(f'| {model} / {key} | {stats["n"]} | {values} |')
    lines.extend(['', '## Pure HTTP latency, client overhead and validity', '',
                  '| Model | HTTP attempt median / p95 (s) | Client overhead median / p95 (s) | Invalid / all requests | Invalid share | Routing deviations |',
                  '|---|---:|---:|---:|---:|---:|'])
    for model,entry in result['models'].items():
        http,overhead=entry['http_attempt_latency_s'],entry['client_overhead_including_backoff_s']
        http_text=f'{http["median"]:.4f} / {http["p95"]:.4f}' if http else 'n/a'
        overhead_text=f'{overhead["median"]:.4f} / {overhead["p95"]:.4f}' if overhead else 'n/a'
        lines.append(f'| {model} | {http_text} | {overhead_text} | {entry["requests"]-entry["valid_requests"]}/{entry["requests"]} | {entry["invalid_request_share"]:.4%} | {entry["provider_routing_deviations"]} |')
    lines.extend(['', '## Concurrency and sanity checks', '',
                  '| Model / group | Request median inflation vs full c1 parallel | Error rate | HTTP 429 rate |',
                  '|---|---:|---:|---:|'])
    for model,entry in result['models'].items():
        for key,group in entry['by_stage_concurrency_schedule'].items():
            inflation = group['median_latency_inflation_vs_full_c1_parallel']
            lines.append(f'| {model} / {key} | {inflation if inflation is not None else "n/a"} | {group["error_rate"]} | {group["rate_429"]} |')
    lines.extend(['', '| Model | Probe | Changes / valid pairs | Rate (sanity check only) |',
                  '|---|---|---:|---:|'])
    for model,entry in result['models'].items():
        for probe,change in entry['action_changes_sanity_only'].items():
            lines.append(f'| {model} | {probe} | {change["changes"]}/{change["valid_pairs"]} | {change["rate"]} |')
    lines.extend(['', 'Full median/p90/p95/max, concurrency inflation, action-change counts/rates, source hashes, and all per-request details are in summary.json and requests.jsonl.', ''])
    (out / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    return result


def stage_plan(stage, full_counts):
    if stage == 'pilot':
        return [(1, 'sequential', 0, 5)]
    n1,n4,n8 = full_counts
    return [(1,'sequential',5,n1//2), (1,'parallel',5+n1//2,n1-n1//2),
            (4,'parallel',5+n1,n4), (8,'parallel',5+n1+n4,n8)]


async def run_stage(stage, *, out=OUT, ledger=LEDGER, dry_run=False, full_counts=(60,20,20)):
    if not dry_run and (out.resolve() != OUT.resolve() or ledger.resolve() != LEDGER.resolve()):
        raise ValueError('Live outputs and ledger must use the dedicated latency paths')
    if dry_run and (out.resolve() == OUT.resolve() or ledger.resolve() == LEDGER.resolve()):
        raise ValueError('Dry runs require separate output and ledger paths')
    if stage == 'full':
        pilot_path = out / 'pilot.stage.json'
        if not pilot_path.exists():
            raise ValueError('Pilot must be completed before full stage')
        pilot = json.loads(pilot_path.read_text())
        if pilot['status'] != 'complete' or pilot['dry_run'] != dry_run:
            raise ValueError('Full stage requires a completed pilot in the same live/offline mode')
    out.mkdir(parents=True, exist_ok=True)
    marker = out / f'{stage}.stage.json'
    metadata = {'stage':stage, 'status':'started', 'start_utc':utc_now(), 'dry_run':dry_run,
                'host':socket.gethostname(), 'platform':platform.platform(), 'python':platform.python_version(),
                'versions':{p:importlib.metadata.version(p) for p in ('httpx','httpcore','anyio','numpy')},
                'full_counts_per_model':list(full_counts), 'seed':SEED,
                'client_location':'Unverified physical host/egress location; container timezone is not geolocation'}
    with marker.open('x', encoding='utf-8') as f:
        json.dump(metadata,f,indent=2)
    client = fake_client() if dry_run else httpx.AsyncClient(timeout=180)
    # Fake keys are local to offline mode and never replace live credentials.
    old_env = {key:os.environ.get(key) for key in ('DEEPSEEK_API_KEY','OPENROUTER_API_KEY')}
    if dry_run:
        os.environ.update({'DEEPSEEK_API_KEY': 'offline-fake', 'OPENROUTER_API_KEY': 'offline-fake'})
    try:
        if not dry_run:
            metadata['balances_before'] = await balances(client)
            write_json(marker, metadata)
            print(json.dumps({'balances_before':metadata['balances_before']}),flush=True)
            if any(b['remaining_usd'] < 1.0 for b in metadata['balances_before'].values()):
                raise RuntimeError('Aborted: a provider balance is below USD 1.00')
        budget = TrackingBudget(ledger)
        plan = stage_plan(stage,full_counts)
        samples = {model:select_samples(model,max(offset+n for _,_,offset,n in plan)) for model in STUDY_MODELS}
        metadata['sample_plan'] = [{'concurrency':c,'schedule':s,'decisions_per_model':n} for c,s,_,n in plan]
        write_json(marker,metadata)
        with (out / 'requests.jsonl').open('a', encoding='utf-8') as output:
            for model in STUDY_MODELS:
                for concurrency,schedule,offset,count in plan:
                    # Waves put a strict limit on audited decisions, and drain all in-flight
                    # requests before stopping on a cap or routing violation.
                    for start in range(offset,offset+count,concurrency):
                        wave = samples[model][start:min(start+concurrency,offset+count)]
                        results = await asyncio.gather(*(audit_one(d,model=model,stage=stage,
                            concurrency=concurrency,schedule=schedule,budget=budget,client=client,output=output)
                            for d in wave),return_exceptions=True)
                        for result in results:
                            if isinstance(result,BaseException):
                                raise result
                    print(json.dumps({'completed':model,'concurrency':concurrency,'schedule':schedule,'decisions':count}),flush=True)
        metadata['status'] = 'complete'
    except BaseException as exc:
        metadata.update(status='aborted',error_class=type(exc).__name__,error=str(exc) if isinstance(exc, (ValueError,RuntimeError)) else type(exc).__name__)
        raise
    finally:
        metadata['end_utc'] = utc_now()
        if not dry_run:
            try:
                metadata['balances_after'] = await balances(client)
            except Exception as exc:
                metadata['balances_after_error'] = type(exc).__name__
        await client.aclose()
        if dry_run:
            for key,value in old_env.items():
                if value is None:
                    os.environ.pop(key,None)
                else:
                    os.environ[key] = value
        write_json(marker,metadata)
        summarize(out,ledger)
    return json.loads((out / 'summary.json').read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--stage',choices=['pilot','full'])
    mode.add_argument('--summarize-only',action='store_true',help='Rebuild summary/report offline; no API calls or ledger writes')
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--out',type=Path,default=OUT)
    parser.add_argument('--ledger',type=Path,default=LEDGER)
    parser.add_argument('--full-counts',nargs=3,type=int,default=[60,20,20],metavar=('C1','C4','C8'))
    args = parser.parse_args()
    if args.summarize_only:
        if not (args.out / 'requests.jsonl').is_file():
            parser.error('--summarize-only requires an existing requests.jsonl')
        summarize(args.out,args.ledger)
        return
    if any(n < 2 for n in args.full_counts):
        parser.error('All full-stage counts must be at least two')
    asyncio.run(run_stage(args.stage,out=args.out,ledger=args.ledger,dry_run=args.dry_run,full_counts=args.full_counts))


if __name__ == '__main__':
    main()
