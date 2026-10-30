"""Generate six manuscript inputs from frozen, offline analysis outputs.

With the inline conditions table these form seven tables. Full flow, specificity,
exposure, condition-by-regime rates and null-condition contrasts remain in
data/v2/analysis/exploratory/{results.json,report.md}.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R = json.loads((ROOT / 'data/v2/analysis/exploratory/results.json').read_text())
C = json.loads((ROOT / 'data/v2/analysis/confirm/results.json').read_text())
W = json.loads((ROOT / 'data/v2/analysis/exploratory/network_service_summary.json').read_text())
OUT = Path(__file__).parent / 'tables'
OUT.mkdir(exist_ok=True)
MODELS = [('deepseek-v4-flash', 'DeepSeek'), ('anthropic/claude-haiku-5.5', 'Haiku'),
          ('openai/gpt-6-luna', 'Luna')]
CONDS = ['naive', 'punitive', 'label', 'evidence', 'placebo']
KEYS = ['H1_precision_evidence_minus_naive', 'H1_dependence_evidence_minus_naive',
        'H3_sci_label', 'H4_sci_placebo']
GENERATED = {'primary', 'secondary', 'descriptive', 'regime', 'robustness', 'workload'}
OBSOLETE = {'flow', 'regimecontrasts', 'noise', 'adjusted', 'exposure', 'sensitivity'}


def f(x):
    return f'{x:.4f}'


def p(x):
    if x >= .00005:
        return f'{x:.4f}'
    mantissa, exponent = f'{x:.2e}'.split('e')
    return rf'${mantissa}\times10^{{{int(exponent)}}}$'


def ci(d):
    return '[' + ', '.join(map(f, d['bootstrap_ci_95'])) + ']'


def est(d):
    return f(d['mean_delta']) + ' ' + ci(d)


def cond(x):
    return 'false-label' if x == 'placebo' else x


def bold(value):
    return r'{\bfseries\boldmath ' + value + '}'


def stack(*lines):
    return r'\shortstack[l]{' + r'\\{}'.join(lines) + '}'


def tabular(cols, header, rows):
    return (r'\begin{tabularx}{\linewidth}{@{}' + cols + '@{}}\n'
            + r'\toprule' + '\n' + header + r' \\' + '\n' + r'\midrule' + '\n'
            + '\n'.join(row if isinstance(row, str) else ' & '.join(row) + r' \\'
                        for row in rows)
            + '\n' + r'\bottomrule' + '\n' + r'\end{tabularx}' + '\n')


def table(name, caption, body):
    assert name in GENERATED
    text = (r'\begin{table}[tbp]' + '\n' + r'\caption{' + caption + '}\n'
            + r'\label{tab:' + name + '}\n' + r'\centering\footnotesize' + '\n'
            + r'\setlength{\tabcolsep}{3pt}' + '\n'
            + r'\renewcommand{\arraystretch}{1.0}' + '\n'
            + body + r'\end{table}' + '\n')
    (OUT / (name + '.tex')).write_text(text)


rows = []
for mid, label in MODELS:
    for i, key in enumerate(KEYS):
        d = R['models'][mid]['primary_reproduced'][key]
        delta, holm = f(d['mean_delta']), p(d['holm_p'])
        if d['holm_p'] < .05:
            delta, holm = bold(delta), bold(holm)
        rows.append([label, 'P' + str(i + 1), str(d['n_seed_pairs']),
                     str(d['n_common_decisions']), delta, ci(d), p(d['paired_t_p']),
                     holm, f(d['cohen_dz'])])
table('primary',
      r'Primary tests, ticks 20--39; all predictions are positive. P1 (H1): '
      r'evidence minus naive precision; P2 (H1): evidence minus naive true-driver '
      r'sign-flip sensitivity; P3 (H3): label citation--sensitivity difference '
      r'(CSD), current driver; P4 (H4): false-label CSD, opposite current driver. '
      r'CSD is citation change minus sensitivity change relative to naive. '
      r'$\Delta$ is the equal-seed contrast (mean seed CSD for P3/P4); '
      r'$n_s$ counts seed pairs and $n_j$ matched decisions per arm. All tests '
      r'require valid bases and both valid probes in both arms; P1 also requires '
      r'nonempty cited probe sets. CI: descriptive 95\% paired-seed bootstrap '
      r'confidence interval; $d_z$: $\Delta$ divided by the sample standard '
      r'deviation of seed contrasts. Holm adjusts four tests per model. Bold '
      r'marks corrected rejections, all opposite to prediction.',
      tabular('llrrrXrrr',
              r'Model & Test & $n_s$ & $n_j$ & $\Delta$ & 95\% CI & Raw $p$ & Holm $p$ & $d_z$', rows))

sec = [
    ('H2_fidelity_label_minus_naive', 'H2: label--naive, $E$'),
    ('H2_precision_label_minus_naive', 'H2: label--naive, $P$'),
    ('H2_precision_evidence_minus_label', 'H2: evidence--label, $P$'),
    ('H4_fidelity_placebo_minus_label', 'H4: false-label--label, $E$'),
    ('H4_false_citation_placebo_minus_naive', 'H4: false-label--naive, opposite citation'),
    ('H5_precision_evidence_minus_punitive', 'H5: evidence--punitive, $P$'),
    ('H5_precision_punitive_minus_naive', 'Context: punitive--naive, $P$'),
    ('H1_dependence_evidence_minus_punitive', 'H1: evidence--punitive, true sensitivity'),
    ('H5_dependence_punitive_minus_naive', 'Punitive--naive, true sensitivity'),
]
rows = []
for mid, label in MODELS:
    for key, desc in sec:
        d = R['models'][mid]['C_secondary_table3'][key]
        status = 'Post hoc' if key == 'H5_dependence_punitive_minus_naive' else 'Registered'
        rows.append([label, desc + ' (' + status + ')', est(d), p(d['paired_t_p']),
                     f(d['cohen_dz']), str(d['n_common_decisions'])])
table('secondary',
      r'Secondary comparisons, ticks 20--39; row labels state analysis status. '
      r'$E$: environmental fidelity (true-driver citation); $P$: process '
      r'precision; sensitivity: true-driver sign-flip sensitivity. Citation '
      r'uses matched valid bases; current-opposite citation differs from '
      r'persisted-label adoption. Precision and sensitivity require complete '
      r'probes; precision also requires nonempty cited probe sets. '
      r'Figure~\ref{fig:decomposition} matches complete probes for both components '
      r'of the citation--sensitivity difference (CSD), citation change minus '
      r'sensitivity change relative to naive. $\Delta$: equal-seed target-minus-reference contrast; '
      r'CI: descriptive 95\% paired-seed bootstrap confidence interval; '
      r'$d_z$: mean contrast divided by its sample standard deviation; '
      r'$n_j$: matched decisions per arm. Seeds: 20 DeepSeek, 10 Haiku, 10 Luna. '
      r'Raw $p$ values are diagnostic.',
      tabular('lXlrrr',
              r'Model & Contrast and outcome & $\Delta$ [95\% CI] & Raw $p$ & $d_z$ & $n_j$', rows))

rows = []
for mid, label in MODELS:
    for con in CONDS:
        d = R['models'][mid]['A_descriptive'][con]
        vals = [f(d[k]['mean']) + r'$\pm$' + f(d[k]['seed_sd']) for k in [
            'environmental_fidelity', 'dependence_true', 'dependence_false',
            'process_precision', 'process_recall']]
        rows.append([label, cond(con)] + vals)
table('descriptive',
      r'Absolute outcomes in ticks 20--39: seed means $\pm$ sample standard '
      r'deviation (SD), with 20 DeepSeek seeds and 10 each for Haiku and Luna. '
      r'All defined observations are used without matching across packages. '
      r'$E$: environmental fidelity, or true-driver citation; $d_g$ and '
      r'$d_{\neg g}$: true-driver and opposite-driver sign-flip sensitivity; '
      r'$P$ and $Q$: restricted process alignment precision and recall. Citation '
      r'requires valid bases; the other outcomes require complete probes, with '
      r'nonempty cited sets for $P$ and action-changing sets for $Q$.',
      tabular('llXXXXX', r'Model & Package & $E$ & $d_g$ & $d_{\neg g}$ & $P$ & $Q$', rows))

rows = []
for mid, label in MODELS:
    for reg in ['news', 'momentum']:
        if rows:
            rows.append(r'\midrule')
        d = R['models'][mid]['D_regime']['overall']['naive'][reg]['discrimination']
        delta = est(d)
        if reg == 'news' and label in {'DeepSeek', 'Haiku'}:
            delta += r'$^{\dagger}$'
        rows.append([label, reg, 'Naive discrimination', delta, '--', str(d['n_common_decisions'])])
        for i, key in enumerate(KEYS):
            d = R['models'][mid]['D_primary_by_regime'][reg][key]
            delta = est(d)
            if label == 'Luna' and i == 3:
                delta += r'$^{\dagger}$'
            rows.append(['', '', 'P' + str(i + 1), delta,
                         p(d['paired_t_p']), str(d['n_common_decisions'])])
table('regime',
      r'Registered regime summaries (20 DeepSeek seeds, 10 Haiku, 10 Luna). '
      r'Naive discrimination is true-driver minus opposite-driver sign-flip '
      r'sensitivity in ticks 0--39; $n_j$ counts naive complete-probe decisions. '
      r'P1--P4 use matched eligible ticks 20--39; their $n_j$ counts matched '
      r'decisions per arm. P1/P2 (H1) compare evidence minus naive precision '
      r'and true-driver sensitivity; P3 (H3) and P4 (H4) give label current-driver '
      r'and false-label opposite-driver citation--sensitivity differences '
      r'(CSD: citation change minus sensitivity change relative to naive). '
      r'Estimates are equal-seed means; CI denotes a descriptive 95\% '
      r'paired-seed bootstrap confidence interval. Raw $p$ values are diagnostic. '
      r'$\dagger$ marks failed news discrimination or Luna P4 sign reversal.',
      tabular('lllXrr', r'Model & Regime & Outcome & Estimate [95\% CI] & Raw $p$ & $n_j$', rows))

rows = []
for mid, label in MODELS:
    for con in CONDS:
        d = R['models'][mid]['E_null_rates'][con]

        def rate(window, reg):
            a = d[window][reg]['flip_rate']
            return f"{int(a['sum'])}/{a['n']} ({100 * a['mean']:.2f})"

        rows.append([label, cond(con), rate('overall', 'news'),
                     rate('overall', 'momentum'), rate('primary', 'news'),
                     rate('primary', 'momentum')])
body = r'\textit{A. Null action changes / valid re-asks (percentage)}\par' + '\n'
body += tabular('llXXXX',
                r'Model & Package & All news & All momentum & Primary news & Primary momentum', rows)
rows = []
for mid, label in MODELS:
    m = C['models'][mid]
    for i, key in enumerate(KEYS):
        raw = R['models'][mid]['primary_reproduced'][key]
        raw_delta = f(raw['mean_delta'])
        if raw['holm_p'] < .05:
            raw_delta = bold(raw_delta)
        raw_cell = stack(raw_delta + '; ' + p(raw['paired_t_p']), ci(raw))
        adjusted = R['models'][mid]['E_null_adjusted'].get(key)
        adjusted_cell = (stack(f(adjusted['mean_delta']) + '; ' + p(adjusted['paired_t_p']),
                               ci(adjusted)) if adjusted else '--')
        wide = m['secondary_contrasts']['sensitivity'].get(key)
        if wide is None:
            candidates = [v for v in m['secondary_contrasts']['sensitivity'].values()
                          if v['target'] == ('evidence' if i < 2 else 'label' if i == 2 else 'placebo')
                          and v['metric'] == ('process_precision' if i == 0 else 'dependence_true'
                                              if i == 1 else 'gap_true' if i == 2 else 'gap_false')]
            if len(candidates) != 1:
                raise RuntimeError((mid, key, len(candidates)))
            wide = candidates[0]
        wide_cell = stack(f(wide['mean_delta']) + '; ' + p(wide['paired_t_p']), ci(wide))
        d = m['sensitivity'][key]
        rg = d['cluster_regression']
        coef = rg['terms'][rg['target_coefficient']]
        checks = stack(f(coef['estimate']) + '; ' + p(coef['p_t_cluster_df']),
                       p(d['sign_flip']['p']) + ' / ' + p(rg['wild_bootstrap']['p']))
        rows.append([stack(label, 'P' + str(i + 1)), raw_cell, adjusted_cell, wide_cell, checks])
body += r'\par\smallskip\textit{B. Raw, noise-adjusted and wider-window estimates; registered checks}\par' + '\n'
body += tabular('lXXXX',
                r'Model/test & Raw $\Delta$; $p$ [CI] & Adjusted $\Delta$; $p$ [CI] & Wider $\Delta$; $p$ [CI] & Registered checks', rows)
table('robustness',
      r'Null variability and sensitivity checks. Panel A gives action changes / '
      r'valid identical-prompt re-asks (percentage), for all ticks 0--39 and primary '
      r'ticks 20--39. All selected valid-base nulls were valid; one invalid-base '
      r'Haiku evidence null is excluded. Panel B uses 20 DeepSeek seed pairs and 10 '
      r'each for Haiku and Luna. P1--P4, matched support, equal-seed $\Delta$ '
      r'and descriptive 95\% paired-seed bootstrap confidence intervals (CIs) '
      r'follow Table~\ref{tab:primary}. Let $\delta_{0s}$ be the target-minus-naive '
      r'null-rate difference within each seed and package over ticks 0--39. '
      r'Adjusted seed sensitivity contrasts subtract $\delta_{0s}$; adjusted '
      r'citation--sensitivity differences (CSDs) add it, before equal-seed averaging. '
      r'This differs from the registered model-by-package adjustment; no clipping '
      r'or fallback cells occur. P1 has no identified adjustment. Wider window: '
      r'10--39. Registered checks show the seed-clustered coefficient and '
      r'cluster-$t$ $p$ above the permutation and wild-bootstrap $p$ values. '
      r'Bold marks primary contrasts significant after Holm correction (raw '
      r'estimates shown); other $p$ values are diagnostic.', body)

rows = []
for mid, label in MODELS:
    m = W['models'][mid]
    usage = m['all_calls']
    s = m['sampling_and_multipliers']
    rows.append([
        label,
        f(s['full_audit_expected_calls_per_decision_at_realized_null_share']),
        f(s['realized_ledger_attempts_per_assigned_decision']),
        f"{usage['mean_prompt_tokens_reported_usage_calls']:.1f} / "
        f"{usage['mean_completion_tokens_reported_usage_calls']:.1f}",
        f"{1000 * s['ledger_cost_usd_per_assigned_decision']:.2f}",
        f(s['measured_recorded_token_multiplier_vs_base_calls']),
        f(s['measured_ledger_cost_multiplier_vs_base_calls']),
    ])
body = tabular('lXXXXXX',
               'Model & ' + stack('Calls per', 'fully probed', 'decision') + ' & '
               + stack('Attempts per', 'assigned', 'decision') + ' & '
               + stack('Mean tokens', 'input / output', 'per call') + ' & '
               + stack('USD per', '1,000 assigned', 'decisions') + ' & '
               + stack('Token', 'multiplier') + ' & '
               + stack('Cost', 'multiplier'), rows)
attempts = ', '.join(f"{W['models'][mid]['all_calls']['ledger_attempts']:,}" for mid, _ in MODELS)
per_decision = ', '.join(
    f"{W['models'][mid]['sampling_and_multipliers']['ledger_cost_usd_per_assigned_decision']:.8f}"
    for mid, _ in MODELS)
luna = W['models'][MODELS[-1][0]]['all_calls']
body += (r'\par\smallskip\raggedright\textit{Note.} All ticks and packages; '
         r'fully probed calls are expected counts at the realized null share, '
         r'before retries and invalid bases. Attempts, token and request-log cost '
         r'multipliers are measured at the realized half-decision sampling; '
         r'multipliers use original calls alone as the denominator. Attempt '
         r'totals were ' + attempts + r' for DeepSeek, Haiku and Luna, respectively; '
         r'USD per assigned decision was ' + per_decision + r', in the same order. '
         r'Traffic and request-log costs include all attempts. Token means exclude '
         + str(luna['usage_missing_calls']) + r' Luna rows with missing usage and '
         + str(luna['error_attempts']) + r' zero-usage Hypertext Transfer Protocol '
         r'(HTTP) 503 Service Unavailable attempts with conservative charges; '
         r'recorded token totals are lower bounds. Request-log costs are not invoices: '
         r'DeepSeek uses recorded cache counts and configured rates, with cache '
         r'pricing lowering its cost multiplier; OpenRouter uses returned cost '
         r'where available and configured token rates otherwise. Missing usage '
         r'and failed attempts use conservative reservations.\par' + '\n')
table('workload',
      r'Networked audit-sidecar workload from the request log. USD: US dollars. Token means use calls with reported usage. '
      r'Full probing includes the original call, both sign-flip re-asks and '
      r'the conditional identical-prompt re-ask.', body)


# Delete only known superseded generated inputs; preserve unrelated files.
for name in OBSOLETE:
    (OUT / (name + '.tex')).unlink(missing_ok=True)
print('Generated', len(GENERATED), 'input tables (seven including inline conditions)')
