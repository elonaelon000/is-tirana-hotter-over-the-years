"""Same-year, same-month comparison of ERA5 mean daily maximum with Wikipedia.

Wikipedia's published monthly normal is a point statistic WITHOUT a supplied
uncertainty interval; uncertainty limits below cover ERA5 resampling only.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from .statistics import DRAWS, SEEDS, interval


def compare_monthly_normals(
    daily: pd.DataFrame,
    wiki: pd.DataFrame,
    year_start: int,
    year_end: int,
    *,
    draws: int = DRAWS,
    seed: int = SEEDS['sanity_bootstrap'],
) -> pd.DataFrame:
    if year_start > year_end:
        raise ValueError('Invalid Wikipedia normal date range')
    subset = wiki.loc[wiki['metric'].eq('mean_daily_max_c')].copy()
    if len(subset) != 12 or subset['month'].nunique() != 12:
        raise ValueError('Cannot compare: Wikipedia maximum-temperature normal is missing months')
    if subset['value'].isna().any():
        raise ValueError('Cannot compare: Wikipedia has missing maximum-temperature normal values')
    rng = np.random.default_rng(seed)
    rows = []
    years = range(year_start, year_end + 1)
    for month in range(1, 13):
        sums, counts, expected = [], [], 0
        for year in years:
            days = pd.Period(f'{year}-{month:02d}').days_in_month
            expected += days
            d = daily.loc[daily['year'].eq(year) & daily['month'].eq(month), 'temperature_2m_max'].dropna()
            sums.append(float(d.sum()))
            counts.append(len(d))
        annual_sums = np.asarray(sums, dtype=float)
        annual_counts = np.asarray(counts, dtype=float)
        valid = int(annual_counts.sum())
        if not valid:
            raise ValueError(f'No ERA5 observations for Wikipedia normal month {month}')
        observed = annual_sums.sum() / valid
        idx = rng.integers(0, len(annual_sums), size=(draws, len(annual_sums)))
        numer = annual_sums[idx].sum(axis=1)
        denom = annual_counts[idx].sum(axis=1)
        boot = np.divide(numer, denom, out=np.full(draws, np.nan), where=denom > 0)
        era_lo, era_hi = interval(boot)
        norm = float(subset.loc[subset['month'].eq(month), 'value'].iloc[0])
        rows.append({
            'month': month,
            'wiki_mean_max_c': norm,
            'era5_mean_max_c': float(observed),
            'era5_ci_lower_c': era_lo,
            'era5_ci_upper_c': era_hi,
            'difference_c': float(observed - norm),
            'difference_ci_lower_c': float(era_lo - norm),
            'difference_ci_upper_c': float(era_hi - norm),
            'wiki_normals_start_year': year_start,
            'wiki_normals_end_year': year_end,
            'valid_max_days': valid,
            'expected_calendar_days': expected,
            'missing_or_null_max_days': int(expected - valid),
        })
    return pd.DataFrame(rows)
