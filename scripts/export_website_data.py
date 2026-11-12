#!/usr/bin/env python3
"""Export ONLY verified notebook results into the static website (no HTTP).

Requires the notebook's true processed CSVs and the original cached JSON/HTML.
Safe to execute with all network access disabled. Deliberately fails if data has
not been collected; NEVER creates fictional weather data.
"""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re
import sys
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from how_sure_weather.cache import load_cached
from how_sure_weather.statistics import permutation_null, DRAWS, SEEDS


def row_as_numbers(row, cols):
    output = {}
    for field in cols:
        value = row[field]
        if pd.isna(value):
            raise ValueError(f'Invalid missing metric in {field}')
        if isinstance(value, (np.integer, int)):
            output[field] = int(value)
        elif isinstance(value, (np.floating, float)):
            value = float(value)
            if not np.isfinite(value):
                raise ValueError(f'Nonfinite value in {field}')
            output[field] = value
        else:
            output[field] = str(value)
    return output


def main() -> None:
    processed = ROOT / 'processed'
    required = ['period_rates.csv', 'rate_difference.csv', 'summer_year.csv',
                'permutation_summary.csv', 'question_two_changes.csv']
    missing = [name for name in required if not (processed / name).is_file()]
    if missing:
        raise SystemExit('Website results are NOT ready. Complete scheduled collection and '
                         f'execute the notebook first. Missing: {", ".join(missing)}')

    # Verification uses only the existing raw cache. Never fetch or update it.
    load_cached(ROOT, 'open_meteo_full')
    load_cached(ROOT, 'wikipedia_tirana')
    for path in ['coverage.json', 'access_check_report.json', 'collection_report.json']:
        if not (processed / path).is_file():
            raise SystemExit(f'Missing notebook/collection validation file: processed/{path}')

    rates = pd.read_csv(processed / 'period_rates.csv')
    rates = rates.set_index('period').loc[['1961-1990', '1991-2020']].reset_index()
    diff = pd.read_csv(processed / 'rate_difference.csv').iloc[0]
    shuffle_summary = pd.read_csv(processed / 'permutation_summary.csv').iloc[0]
    shifts = pd.read_csv(processed / 'question_two_changes.csv')
    shifts = shifts.set_index('metric').loc[['mean_daily_summer_max', 'p95_daily_summer_max']].reset_index()
    years = pd.read_csv(processed / 'summer_year.csv')

    if not (rates[['rate','ci_lower','ci_upper']].notna().all().all()):
        raise ValueError('Unusable observed rate or bootstrap range')
    if not ((rates['start_year'].tolist() == [1961, 1991]) and
            (rates['end_year'].tolist() == [1990, 2020])):
        raise ValueError('Unexpected comparison years; refuse to publish')
    if not (int(diff['draws']) == DRAWS and int(shuffle_summary['draws']) == DRAWS
            and (shifts['draws'] == DRAWS).all()):
        raise ValueError('A calculation does not have the predeclared 10,000 draws')
    if int(shuffle_summary['seed']) != SEEDS['permutation']:
        raise ValueError('Unexpected permutation seed')

    # Recreate the exact permutation distribution from the notebook's year table;
    # summary outputs do not preserve its 10k raw values, so use the same code
    # and fixed seed, then cross-check the notebook's stored summary.
    shuffle = permutation_null(years, float(diff['observed_difference']),
                               draws=DRAWS, seed=SEEDS['permutation'])
    for field in ['observed_difference', 'null_ci_lower', 'null_ci_upper',
                  'extreme_fraction', 'extreme_fraction_ci_lower', 'extreme_fraction_ci_upper']:
        if not np.isclose(float(shuffle_summary[field]), float(shuffle[field]), rtol=1e-8, atol=1e-10):
            raise ValueError(f'Permutation reconstruction disagrees with notebook: {field}')

    counts, edges = np.histogram(np.asarray(shuffle['distribution']) * 100, bins=42)
    prediction = None
    seal = ROOT / 'config' / 'SEALED_PREDICTION.md'
    if seal.exists() and 'SEALED, do not edit' in seal.read_text(encoding='utf-8'):
        text = seal.read_text(encoding='utf-8')
        found = re.search(r'^\*\*Text:\*\*\s*(.+)$', text, re.M)
        if found:
            prediction = found.group(1).strip()

    rate_fields = ['period', 'start_year', 'end_year', 'hot_days', 'valid_max_days',
                   'expected_days', 'missing_or_null_max_days', 'rate', 'ci_lower', 'ci_upper']
    change_fields = ['metric', 'period_a_value', 'period_b_value', 'observed_change',
                     'ci_lower', 'ci_upper']
    permutation_fields = ['observed_difference', 'null_ci_lower', 'null_ci_upper',
                          'extreme_fraction', 'extreme_fraction_ci_lower', 'extreme_fraction_ci_upper',
                          'draws', 'seed']
    result = {
        'status': 'computed',
        'generated_at': datetime.now(ZoneInfo('Europe/Tirane')).strftime('%d %b %Y, %H:%M Europe/Tirane'),
        'source': 'Validated cached Open-Meteo ERA5; no live web requests by website',
        'periods': ['1961-1990', '1991-2020'],
        'summer_months': [6, 7, 8],
        'strict_temperature_threshold_c': 35,
        'rates': [row_as_numbers(r, rate_fields) for _,r in rates.iterrows()],
        'difference': row_as_numbers(diff, ['observed_difference', 'ci_lower', 'ci_upper']),
        'permutation': {
            **row_as_numbers(shuffle_summary, permutation_fields),
            'histogram': {'edges': edges.tolist(), 'counts': counts.tolist()},
        },
        'changes': [row_as_numbers(r, change_fields) for _,r in shifts.iterrows()],
        'prediction': prediction,
    }
    out = ROOT / 'site' / 'results.js'
    out.write_text('/* Computed from verified, locally cached responses. No synthetic values. */\n'
                   'window.WEATHER_RESULTS = '+json.dumps(result, ensure_ascii=False, allow_nan=False,
                                                           indent=2)+';\n',encoding='utf-8')
    print(f'Wrote {out} from validated offline results. No HTTP requests were made.')


if __name__ == '__main__':
    main()
