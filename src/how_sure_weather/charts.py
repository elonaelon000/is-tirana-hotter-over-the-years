"""Figures for the six-minute talk (strictly from computed results)."""
from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def permutation_histogram(null_result: dict, path: Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    values = np.asarray(null_result['distribution']) * 100
    observed = null_result['observed_difference'] * 100
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(values, bins=42, edgecolor='white', alpha=.88, label='Year-label shuffles (no-change baseline)')
    ax.axvline(observed, linewidth=2.5, label='Observed change')
    ax.axvline(null_result['null_ci_lower'] * 100, linestyle='--', alpha=.75, label='Central 95% of shuffles')
    ax.axvline(null_result['null_ci_upper'] * 100, linestyle='--', alpha=.75)
    ax.set(xlabel='Late minus early hot-day rate (percentage points)', ylabel='Number of shuffles',
           title='If there were no period difference, what changes arise by chance?')
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    return fig


def change_comparison(changes: pd.DataFrame, path: Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    order = ['mean_daily_summer_max', 'p95_daily_summer_max']
    frame = changes.set_index('metric').loc[order]
    vals = frame['observed_change'].to_numpy()
    low = frame['ci_lower'].to_numpy()
    high = frame['ci_upper'].to_numpy()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    yy = np.arange(len(frame))[::-1]
    # Percentile-bootstrap bounds need not surround the original point estimate.
    # Draw interval segments and point estimates separately, never a negative xerr.
    ax.hlines(yy, low, high, linewidth=3, label='95% year-block bootstrap range')
    ax.scatter(vals, yy, s=70, zorder=3, label='Observed change')
    ax.axvline(0, linestyle='--', linewidth=1.5, label='No change')
    ax.set_yticks(yy, ['Mean summer daily maximum', '95th-percentile summer daily maximum'])
    ax.set_xlabel('1991–2020 minus 1961–1990 (°C)')
    ax.set_title('Did the typical maximum or the hot tail shift?')
    ax.legend(fontsize=9, loc='best')
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    return fig


def period_rate_chart(rates: pd.DataFrame, path: Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    vals = 100 * rates['rate'].to_numpy()
    low = 100 * rates['ci_lower'].to_numpy()
    high = 100 * rates['ci_upper'].to_numpy()
    fig, ax = plt.subplots(figsize=(8, 4.2))
    yy = np.arange(len(vals))[::-1]
    ax.hlines(yy, low, high, linewidth=3, label='95% year-block bootstrap range')
    ax.scatter(vals, yy, s=70, zorder=3, label='Observed rate')
    ax.set_yticks(yy, rates['period'].tolist())
    ax.set(xlabel='P(max > 35°C | summer, period), percent',
           title='Hot-day base rates with 95% year-block bootstrap ranges')
    ax.set_xlim(left=0)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    return fig
