"""Offline checks of prompt replay, accounting, timings and scheduling."""
import asyncio
import json
import sys
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.v2 import latency_benchmark as lb
from src.v2.conditions import PERSONAS, build_messages
from src.v2.llm import BudgetExceeded
from src.v2.models import MODELS


def test_exact_replay_and_fixed_balanced_selection():
    model = lb.STUDY_MODELS[0]
    first = lb.select_samples(model, 105)
    assert first == lb.select_samples(model, 105)
    assert len({d['decision_id'] for d in first}) == 105
    assert not {d['decision_id'] for d in first[:5]} & {d['decision_id'] for d in first[5:]}
    assert {d['condition'] for d in first[:5]} == {'naive','label','evidence'}
    assert {d['regime'] for d in first[:5]} == {'news','momentum'}
    assert all(20 <= d['tick'] <= 39 for d in first)
    for d in first[:5]:
        logged = lb.read_jsonl(ROOT / d['source'])
        row = next(r for r in logged if r['type']=='decision' and r['tick']==d['tick'] and r['agent']==d['agent'])
        # The persisted input feedback, including evidence tables, is used verbatim.
        if row['feedback']:
            assert row['feedback'] in d['messages'][-1]['content']


def fixture_decisions(model, count):
    features = dict(momentum=.5, spread=.01, volume=1., news=-.2, orderflow=.3, sentiment=-.1)
    return [dict(source='offline-fixture',source_sha256='fixture',tick=20,agent=0,
                 condition='naive',regime='news',decision_id=f'{model}-{i}',
                 messages=build_messages(features,6000,20,'naive',PERSONAS[0])) for i in range(count)]


def test_dry_pilot_full_and_stage_relaunch_protection(tmp_path, monkeypatch):
    monkeypatch.setattr(lb,'select_samples',fixture_decisions)
    out,ledger = tmp_path/'latency',tmp_path/'latency_ledger.jsonl'
    pilot = asyncio.run(lb.run_stage('pilot',out=out,ledger=ledger,dry_run=True))
    assert not pilot['models']
    assert all(m['valid_requests']==20 for m in pilot['pilot_models'].values())
    assert sum(pilot['cost_by_provider_usd'].values()) > 0
    with pytest.raises(FileExistsError):
        asyncio.run(lb.run_stage('pilot',out=out,ledger=ledger,dry_run=True))
    result = asyncio.run(lb.run_stage('full',out=out,ledger=ledger,dry_run=True,full_counts=(4,4,8)))
    rows = lb.read_jsonl(out/'requests.jsonl')
    assert len(rows)==3*(5+4+4+8)*4
    assert all(row['valid'] and len(row['attempts'])==1 for row in rows)
    assert all(row['end_monotonic_s'] >= row['start_monotonic_s'] for row in rows)
    for model in lb.STUDY_MODELS:
        assert result['models'][model]['requests']==(4+4+8)*4
        assert result['pilot_models'][model]['requests']==20
        groups=result['models'][model]['by_stage_concurrency_schedule']
        assert groups['full:c8:parallel']['median_latency_inflation_vs_full_c1_parallel'] > 0
        assert groups['full:c1:sequential']['observed_audit_s']['n']==2
        assert groups['full:c1:parallel']['observed_audit_s']['n']==2
        assert result['models'][model]['client_overhead_including_backoff_s']['median'] >= 0
        assert result['models'][model]['invalid_request_share']==0
        assert result['models'][model]['provider_routing_deviations']==0
    decisions={}
    for row in rows:
        decisions.setdefault((row['stage'],row['decision_id']),[]).append(row)
    for group in decisions.values():
        base=next(r for r in group if r['probe']=='base')
        probes=[r for r in group if r['probe']!='base']
        assert all(r['start_monotonic_s'] >= base['end_monotonic_s'] for r in probes)
        if base['schedule']=='sequential':
            assert all(a['end_monotonic_s'] <= b['start_monotonic_s'] for a,b in zip(probes,probes[1:]))
        else:
            assert max(r['start_monotonic_s'] for r in probes) < min(r['end_monotonic_s'] for r in probes)
    for i in range(0,len(rows),4):
        group=rows[i:i+4]
        if group[0]['stage']=='pilot':
            assert group[0]['messages']==group[3]['messages']
    assert (out/'report.md').exists()
    assert all(cost<=.5 for cost in result['cost_by_provider_usd'].values())


def test_budget_reservations_enforce_separate_caps(tmp_path):
    async def run():
        budget=lb.TrackingBudget(tmp_path/'latency_ledger.jsonl')
        budget.caps['deepseek']=.001
        model=MODELS['deepseek-v4-flash']
        messages=[{'role':'user','content':'small prompt'}]
        reservation,_=await budget.reserve(model,messages,512)
        with pytest.raises(BudgetExceeded):
            await budget.reserve(model,messages,512)
        await budget.release(model,reservation)
        await budget.reserve(model,messages,512)
    asyncio.run(run())


def test_retry_status_cost_and_invalid_parser_recorded(tmp_path, monkeypatch):
    monkeypatch.setenv('OPENROUTER_API_KEY','offline')
    calls=[]
    def handler(request):
        calls.append(json.loads(request.content))
        if len(calls)==1:
            return httpx.Response(429,json={'error':'rate limited'})
        return httpx.Response(200,json={'provider':'anthropic','choices':[{'message':{'content':'{"action":"buy"}'}}],
                                      'usage':{'prompt_tokens':11,'completion_tokens':3,'cost':.00001}})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with (tmp_path/'requests.jsonl').open('w') as output:
                d=fixture_decisions('anthropic/claude-haiku-5.5',1)[0]
                return await lb.request_one(d,'base',d['messages'],model='anthropic/claude-haiku-5.5',
                     stage='pilot',concurrency=1,schedule='sequential',budget=lb.TrackingBudget(tmp_path/'ledger.jsonl'),
                     client=client,output=output)
    row=asyncio.run(run())
    assert row['count_429']==1 and row['retries']==1 and row['http_status']==200
    assert row['cost_usd']==.00001 and row['prompt_tokens']==11 and not row['valid']
    assert 'temperature' not in calls[0] and calls[0]['max_tokens']==512
    assert calls[0]['provider']=={'order':['anthropic'],'allow_fallbacks':False,'data_collection':'deny'}


def test_balance_parsing_and_no_paid_calls_below_threshold(tmp_path, monkeypatch):
    monkeypatch.setenv('DEEPSEEK_API_KEY','offline')
    monkeypatch.setenv('OPENROUTER_API_KEY','offline')
    def handler(request):
        assert request.method=='GET'
        if request.url.host=='api.deepseek.com':
            return httpx.Response(200,json={'balance_infos':[{'currency':'USD','total_balance':'2.50'}]})
        return httpx.Response(200,json={'data':{'total_credits':3,'total_usage':2.5}})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await lb.balances(client)
    result=asyncio.run(run())
    assert result['deepseek']['remaining_usd']==2.5
    assert result['openrouter']['remaining_usd']==.5
    client=httpx.AsyncClient(transport=httpx.MockTransport(handler))
    out,ledger=tmp_path/'live-output',tmp_path/'latency_ledger.jsonl'
    monkeypatch.setattr(lb,'OUT',out)
    monkeypatch.setattr(lb,'LEDGER',ledger)
    monkeypatch.setattr(lb.httpx,'AsyncClient',lambda **kwargs:client)
    with pytest.raises(RuntimeError,match='below USD 1.00'):
        asyncio.run(lb.run_stage('pilot',out=out,ledger=ledger))
    assert not ledger.exists() and not (out/'requests.jsonl').exists()
    assert json.loads((out/'pilot.stage.json').read_text())['status']=='aborted'


def test_percentiles_and_incomplete_decisions():
    assert lb.percentiles([1,2,3,4])=={'n':4,'median':2.5,'p90':3.7,'p95':3.8499999999999996,'max':4}
    assert lb.group_summary([])['complete_decisions']==0


@pytest.mark.parametrize('schedule,spans,expected',[
    ('sequential',[(110,112),(115,118),(118,121)],11),
    ('parallel',[(110,112),(111,118),(110.5,115)],8),
])
def test_sidecar_span_excludes_base_and_includes_probe_gaps(schedule,spans,expected):
    # These timestamps distinguish the observed span from sums/maxima and from
    # base-inclusive time, including delayed probe dispatch and scheduling gaps.
    def row(probe,start,end):
        return dict(model=lb.STUDY_MODELS[0],stage='full',concurrency=1,schedule=schedule,
                    decision_id='fixture',probe=probe,start_monotonic_s=start,end_monotonic_s=end,
                    latency_s=end-start,attempts=[],error_class=None,served_provider='deepseek',
                    valid=True,action='buy',cost_usd=.001,retries=0,count_429=0,count_5xx=0,
                    start_utc=f'2026-11-19T00:00:{start-100:06.3f}+00:00',
                    end_utc='2026-11-19T00:00:30+00:00')
    base=row('base',100,109)
    probes=[row(probe,*span) for probe,span in zip(('news','momentum','null'),spans)]
    summary=lb.group_summary([base,*reversed(probes)])
    assert summary['sidecar_added_latency_s']==dict(n=1,median=expected,p90=expected,p95=expected,max=expected)
    assert summary['observed_audit_s']['median']==max(end for _,end in spans)-100
    assert lb.group_summary(probes)['sidecar_added_latency_s']['median']==expected
    assert lb.group_summary([base,*probes[:2]])['sidecar_added_latency_s'] is None
    assert lb.group_summary([base,probes[0],probes[0],probes[2]])['sidecar_added_latency_s'] is None


def test_summarize_only_cli_is_offline_and_preserves_inputs(tmp_path,monkeypatch):
    monkeypatch.setattr(lb,'select_samples',fixture_decisions)
    out,ledger=tmp_path/'latency',tmp_path/'latency_ledger.jsonl'
    asyncio.run(lb.run_stage('pilot',out=out,ledger=ledger,dry_run=True))
    asyncio.run(lb.run_stage('full',out=out,ledger=ledger,dry_run=True,full_counts=(2,2,2)))
    paths=[out/'requests.jsonl',ledger,out/'pilot.stage.json',out/'full.stage.json']
    before={path:path.read_bytes() for path in paths}
    def forbidden(*args,**kwargs):
        pytest.fail('Offline summary must not construct clients, run stages or query balances')
    monkeypatch.setattr(lb.httpx,'AsyncClient',forbidden)
    monkeypatch.setattr(lb,'run_stage',forbidden)
    monkeypatch.setattr(lb,'balances',forbidden)
    monkeypatch.setattr(sys,'argv',['latency_benchmark','--summarize-only','--out',str(out),'--ledger',str(ledger)])
    lb.main()
    result=json.loads((out/'summary.json').read_text())
    assert result['main_statistics_stage']=='full'
    for model in lb.STUDY_MODELS:
        assert result['models'][model]['requests']==24
        assert result['pilot_models'][model]['requests']==20
        assert all(key.startswith('full:') for key in result['models'][model]['by_stage_concurrency_schedule'])
        assert result['models'][model]['sidecar_added_latency_s']['n']==6
    assert {path:path.read_bytes() for path in paths}==before
    report=(out/'report.md').read_text()
    assert '## Temporal variability' in report and '## Facts for the manuscript' in report


def test_routing_mismatch_is_recorded_and_stops(tmp_path,monkeypatch):
    monkeypatch.setenv('OPENROUTER_API_KEY','offline')
    def handler(request):
        return httpx.Response(200,json={'provider':'unexpected','choices':[{'message':{'content':'{}'}}],
                                      'usage':{'prompt_tokens':11,'completion_tokens':3,'cost':.00001}})
    path=tmp_path/'requests.jsonl'
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with path.open('w') as output:
                d=fixture_decisions('anthropic/claude-haiku-5.5',1)[0]
                await lb.request_one(d,'base',d['messages'],model='anthropic/claude-haiku-5.5',
                     stage='pilot',concurrency=1,schedule='sequential',budget=lb.TrackingBudget(tmp_path/'ledger.jsonl'),
                     client=client,output=output)
    with pytest.raises(RuntimeError,match='ProviderMismatch'):
        asyncio.run(run())
    rows=lb.read_jsonl(path)
    assert rows[0]['served_provider']=='unexpected'
    assert lb.group_summary(rows)['provider_routing_deviations']==1


@pytest.mark.parametrize('provider,variable', [('deepseek','DEEPSEEK_API_KEY'), ('openrouter','OPENROUTER_API_KEY')])
def test_credentials_require_documented_provider_environment(provider, variable, monkeypatch):
    monkeypatch.delenv(variable, raising=False)
    with pytest.raises(RuntimeError, match=f'Set {variable}'):
        lb._api_key(provider)
    monkeypatch.setenv(variable, 'offline')
    assert lb._api_key(provider) == 'offline'
