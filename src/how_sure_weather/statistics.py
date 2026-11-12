"""Descriptive probability methods; resampling unit is the WHOLE summer year.

No ML, fitting, training, prediction, scikit-learn, day-level bootstrap, or
model-based forecast. Intervals are descriptive bootstrap / shuffle ranges.
"""
from __future__ import annotations
from statistics import NormalDist
from typing import Any
import numpy as np
import pandas as pd
from .data import PERIODS, summer_year_table

SEEDS = {'hot_bootstrap': 20261109, 'permutation': 20261110, 'temp_bootstrap': 20261111, 'sanity_bootstrap': 20261112}
DRAWS = 10_000


def interval(samples: np.ndarray, level: float = .95) -> tuple[float, float]:
    clean = np.asarray(samples, dtype=float)
    clean = clean[np.isfinite(clean)]
    if len(clean) == 0:
        raise ValueError('No valid resamples: cannot form an uncertainty interval')
    low, high = np.quantile(clean, [(1 - level) / 2, 1 - (1 - level) / 2])
    return float(low), float(high)


def ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        raise ValueError('Cannot estimate rate with zero valid observed days')
    return float(numerator / denominator)


def _period_indices(yearly: pd.DataFrame, label: str) -> pd.DataFrame:
    block = yearly.loc[yearly['period'] == label].sort_values('year').reset_index(drop=True)
    if len(block) != 30:
        raise ValueError(f'Need exactly 30 year slots for {label}, including missing-year slots.')
    if block['valid_max_days'].sum() == 0:
        raise ValueError(f'No summer maximum temperatures available in {label}')
    return block


def rate_bootstrap(yearly: pd.DataFrame, draws: int = DRAWS, seed: int = SEEDS['hot_bootstrap']) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Bootstrap 30 summer YEAR blocks within each period, not 2,760 days."""
    rng = np.random.default_rng(seed)
    outputs = {}
    rows = []
    for label, start, end in PERIODS:
        p = _period_indices(yearly, label)
        hot = p['hot_days'].to_numpy(dtype=float)
        valid = p['valid_max_days'].to_numpy(dtype=float)
        indices = rng.integers(0, len(p), size=(draws, len(p)))
        sample_hot = hot[indices].sum(axis=1)
        sample_valid = valid[indices].sum(axis=1)
        boot = np.divide(sample_hot, sample_valid, out=np.full(draws, np.nan), where=sample_valid > 0)
        lo, hi = interval(boot)
        observed = ratio(hot.sum(), valid.sum())
        rows.append({
            'period': label,
            'start_year': start,
            'end_year': end,
            'hot_days': int(hot.sum()),
            'valid_max_days': int(valid.sum()),
            'expected_days': int(p['expected_days'].sum()),
            'missing_or_null_max_days': int(p['missing_or_null_max_days'].sum()),
            'rate': observed,
            'ci_lower': lo,
            'ci_upper': hi,
            'complete': bool(int(p['missing_or_null_max_days'].sum()) == 0),
        })
        outputs[label] = boot
    a, b = PERIODS[0][0], PERIODS[1][0]
    point = rows[1]['rate'] - rows[0]['rate']
    diff = outputs[b] - outputs[a]
    low, high = interval(diff)
    return pd.DataFrame(rows), {
        'observed_difference': point,
        'ci_lower': low,
        'ci_upper': high,
        'draws': draws,
        'seed': seed,
        'distribution': diff,
        'method': '95% year-block percentile bootstrap',
    }


def wilson_interval(k: int, n: int, confidence: float = .95) -> tuple[float, float]:
    """MC sampling error for the shuffled extreme fraction (not a weather CI)."""
    z = NormalDist().inv_cdf(0.5 + confidence / 2)
    p = k / n
    denominator = 1 + z ** 2 / n
    center = (p + z ** 2 / (2 * n)) / denominator
    half = z / denominator * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2))
    return max(0., center - half), min(1., center + half)


def permutation_null(yearly: pd.DataFrame, observed_difference: float, draws: int = DRAWS, seed: int = SEEDS['permutation']) -> dict[str, Any]:
    """Shuffle labels among 60 *year blocks* (30 slots per group)."""
    a = _period_indices(yearly, PERIODS[0][0])
    b = _period_indices(yearly, PERIODS[1][0])
    combined = pd.concat([a, b], ignore_index=True)
    hot = combined['hot_days'].to_numpy(dtype=float)
    valid = combined['valid_max_days'].to_numpy(dtype=float)
    rng = np.random.default_rng(seed)
    shuffled = np.empty(draws, dtype=float)
    for i in range(draws):
        indices = rng.permutation(len(combined))
        first, second = indices[:30], indices[30:]
        shuffled[i] = ratio(hot[second].sum(), valid[second].sum()) - ratio(hot[first].sum(), valid[first].sum())
    lo, hi = interval(shuffled)
    extreme = int(np.sum(np.abs(shuffled) >= abs(observed_difference) - 1e-12))
    # Add-one for a conservative permutation-tail estimate. Wilson range
    # describes finite Monte Carlo error, not the underlying climate process.
    probability = (extreme + 1) / (draws + 1)
    mc_lo, mc_hi = wilson_interval(extreme, draws)
    return {
        'observed_difference': observed_difference,
        'null_ci_lower': lo,
        'null_ci_upper': hi,
        'extreme_fraction': probability,
        'extreme_fraction_ci_lower': mc_lo,
        'extreme_fraction_ci_upper': mc_hi,
        'extreme_count': extreme,
        'draws': draws,
        'seed': seed,
        'distribution': shuffled,
    }


def _summer_temperatures_by_year(daily: pd.DataFrame, label: str) -> list[np.ndarray]:
    start, end = next((s, e) for p, s, e in PERIODS if p == label)
    summer = daily.loc[daily['is_summer']]
    return [
        summer.loc[(summer['year'] == year), 'temperature_2m_max'].dropna().to_numpy(dtype=float)
        for year in range(start, end + 1)
    ]


def mean_tail_bootstrap(daily: pd.DataFrame, draws: int = DRAWS, seed: int = SEEDS['temp_bootstrap']) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    """Mean and pooled 95th-percentile shift, bootstrap resampling by year."""
    rng = np.random.default_rng(seed)
    samples = {}
    points = {}
    for period, _, _ in PERIODS:
        blocks = _summer_temperatures_by_year(daily, period)
        pooled = np.concatenate(blocks)
        if len(pooled) == 0:
            raise ValueError(f'No temperatures in {period}')
        points[period] = (float(np.mean(pooled)), float(np.quantile(pooled, .95)))
        annual_sums = np.asarray([b.sum() for b in blocks])
        annual_counts = np.asarray([len(b) for b in blocks])
        idx = rng.integers(0, 30, size=(draws, 30))
        means = annual_sums[idx].sum(axis=1) / annual_counts[idx].sum(axis=1)
        tails = np.empty(draws)
        for i in range(draws):
            sampled = np.concatenate([blocks[j] for j in idx[i]])
            tails[i] = np.quantile(sampled, .95) if len(sampled) else np.nan
        samples[period] = {'mean': means, 'tail': tails}
    a, b = PERIODS[0][0], PERIODS[1][0]
    rows = []
    distributions = {}
    for name, idx, desc in (
        ('mean_daily_summer_max', 0, 'mean'),
        ('p95_daily_summer_max', 1, 'tail'),
    ):
        dist = samples[b][desc] - samples[a][desc]
        lo, hi = interval(dist)
        points_a, points_b = points[a][idx], points[b][idx]
        rows.append({
            'metric': name,
            'unit': 'C',
            'period_a_value': points_a,
            'period_b_value': points_b,
            'observed_change': points_b - points_a,
            'ci_lower': lo,
            'ci_upper': hi,
            'interval_excludes_zero': bool(lo > 0 or hi < 0),
            'method': '95% year-block percentile bootstrap',
            'draws': draws,
            'seed': seed,
        })
        distributions[name] = dist
    return pd.DataFrame(rows), distributions
