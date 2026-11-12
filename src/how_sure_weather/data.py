"""Parse archived ERA5 weather without filling absent days."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from .cache import load_cached, read_manifest

DAILY_FIELDS = ('temperature_2m_max', 'temperature_2m_min', 'precipitation_sum')
PERIODS = (('1961-1990', 1961, 1990), ('1991-2020', 1991, 2020))


def validate_weather_response(payload: dict, *, minimum_days: int = 1) -> None:
    if payload.get('error'):
        raise ValueError(f'Open-Meteo returned an error: {payload.get("reason", "unknown")}')
    daily = payload.get('daily')
    if not isinstance(daily, dict):
        raise ValueError('Open-Meteo response has no daily data object')
    days = daily.get('time')
    if not isinstance(days, list) or len(days) < minimum_days:
        raise ValueError(f'Open-Meteo returned fewer than {minimum_days} daily dates')
    if len(days) != len(set(days)):
        raise ValueError('Open-Meteo returned duplicate dates')
    for key in DAILY_FIELDS:
        if key not in daily or not isinstance(daily[key], list) or len(daily[key]) != len(days):
            raise ValueError(f'Unexpected missing/unaligned daily variable: {key}')
    units = payload.get('daily_units', {})
    for key in ('temperature_2m_max', 'temperature_2m_min'):
        if units.get(key) not in ('°C', 'degC', 'celsius'):
            raise ValueError(f'Expected Celsius for {key}; got {units.get(key)!r}')
    if units.get('precipitation_sum') != 'mm':
        raise ValueError(f'Expected millimetres for precipitation; got {units.get("precipitation_sum")!r}')
    if payload.get('timezone') not in ('Europe/Tirane', None):
        raise ValueError(f'Unexpected timezone {payload.get("timezone")}')


def load_daily_json(raw: bytes | str | Path) -> pd.DataFrame:
    """Convert cached Open-Meteo JSON to typed daily data; no imputation."""
    if isinstance(raw, Path):
        payload = json.loads(raw.read_text(encoding='utf-8'))
    elif isinstance(raw, bytes):
        payload = json.loads(raw)
    else:
        payload = json.loads(raw)
    validate_weather_response(payload)
    daily = payload['daily']
    df = pd.DataFrame({'date': pd.to_datetime(daily['time'], errors='raise')})
    for field in DAILY_FIELDS:
        df[field] = pd.to_numeric(pd.Series(daily[field]), errors='coerce').astype('float64')
    if df['date'].isna().any() or df['date'].duplicated().any():
        raise ValueError('Null or duplicated dates in Open-Meteo data')
    df = df.sort_values('date').reset_index(drop=True)
    df['year'] = df['date'].dt.year.astype('int64')
    df['month'] = df['date'].dt.month.astype('int64')
    df['is_summer'] = df['month'].isin([6, 7, 8])
    df['is_hot'] = (df['temperature_2m_max'] > 35.0).astype('boolean')
    df.loc[df['temperature_2m_max'].isna(), 'is_hot'] = pd.NA
    period = pd.Series(pd.NA, index=df.index, dtype='string')
    for label, first, last in PERIODS:
        period.loc[df['year'].between(first, last)] = label
    df['period'] = period
    return df


def read_cached_daily(root: Path) -> pd.DataFrame:
    return load_daily_json(load_cached(root, 'open_meteo_full'))


def source_request_dates(root: Path) -> tuple[str, str]:
    """Get the pinned original full request dates from the recorded URL."""
    from urllib.parse import urlparse, parse_qs
    entry = read_manifest(root)['entries'].get('open_meteo_full')
    if not entry:
        raise FileNotFoundError('No full archive request in manifest')
    params = parse_qs(urlparse(entry['url']).query)
    return params['start_date'][0], params['end_date'][0]


def data_coverage(df: pd.DataFrame, first_date: str, last_date: str) -> dict:
    dates = pd.date_range(first_date, last_date, freq='D')
    day_set = pd.DatetimeIndex(df['date'])
    missing_dates = dates.difference(day_set)
    relevant = df.loc[df['date'].isin(dates)]
    null_max = int(relevant['temperature_2m_max'].isna().sum())
    null_min = int(relevant['temperature_2m_min'].isna().sum())
    null_precip = int(relevant['precipitation_sum'].isna().sum())
    return {
        'start_date_requested': first_date,
        'end_date_requested': last_date,
        'expected_calendar_days': len(dates),
        'returned_date_rows': int(day_set.isin(dates).sum()),
        'missing_date_rows': len(missing_dates),
        'null_max_among_returned': null_max,
        'null_min_among_returned': null_min,
        'null_precip_among_returned': null_precip,
        'missing_date_list': [d.strftime('%Y-%m-%d') for d in missing_dates],
    }


def summer_year_table(df: pd.DataFrame) -> pd.DataFrame:
    summer = df.loc[df['is_summer']]
    rows = []
    for period, start, end in PERIODS:
        for year in range(start, end + 1):
            selected = summer.loc[summer['year'].eq(year)]
            valid = selected['temperature_2m_max'].dropna()
            rows.append({
                'year': year,
                'period': period,
                'expected_days': 92,
                'returned_date_rows': len(selected),
                'valid_max_days': len(valid),
                'missing_or_null_max_days': 92 - len(valid),
                'hot_days': int((valid > 35.0).sum()),
                'summer_mean_max_c': float(valid.mean()) if not valid.empty else float('nan'),
                'summer_q95_max_c': float(valid.quantile(0.95)) if not valid.empty else float('nan'),
            })
    result = pd.DataFrame(rows)
    if (result['missing_or_null_max_days'] < 0).any():
        raise ValueError('Unexpected >92 valid summer days in a year')
    return result
