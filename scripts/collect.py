#!/usr/bin/env python3
"""Only network-enabled entrypoint. Exactly one request per source on access day.

Monday 2026-11-09: one seven-day ERA5 probe + one Tirana page request.
Tuesday 2026-11-10: one full-range archive request; no more Wikipedia calls.
Raw files and manifest are retained and must be committed to git.
"""
from __future__ import annotations
import argparse
import hashlib
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from how_sure_weather.cache import fetch_cached, read_manifest, local_date
from how_sure_weather.data import validate_weather_response
from how_sure_weather.wiki import scrape_wiki_normals, WIKI_URL

API = 'https://archive-api.open-meteo.com/v1/archive'
FIELDS = 'temperature_2m_max,temperature_2m_min,precipitation_sum'
REPORT = ROOT / 'processed' / 'access_check_report.json'
COLLECTION_REPORT = ROOT / 'processed' / 'collection_report.json'


def weather_url(start: str, end: str) -> str:
    # Explicit ERA5 model: do NOT trust Open-Meteo's automatic "best match".
    query = [
        ('latitude', '41.3275'), ('longitude', '19.8187'),
        ('start_date', start), ('end_date', end),
        ('daily', FIELDS), ('timezone', 'Europe/Tirane'),
        ('models', 'era5'), ('temperature_unit', 'celsius'),
        ('precipitation_unit', 'mm'),
    ]
    return API + '?' + urlencode(query)


def actual_team() -> dict:
    team = json.loads((ROOT / 'config' / 'team.json').read_text(encoding='utf-8'))
    ua = team.get('user_agent', '')
    if not ua or any(p in ua for p in ('[', ']', 'USER-AGENT', 'TEAM EMAIL')) or ('@' not in ua and 'http' not in ua):
        raise ValueError('Before fetching, replace the placeholder User-Agent with a descriptive name and a team email or URL.')
    seal = (ROOT / 'config' / 'SEALED_PREDICTION.md').read_text(encoding='utf-8')
    if '**SHA-256:** [NOT SEALED]' in seal or 'SEALED, do not edit' not in seal:
        raise ValueError('Seal your actual written prediction before requesting any source.')
    expected_hash = hashlib.sha256(team.get('prediction', '').strip().encode('utf-8')).hexdigest()
    if expected_hash not in seal:
        raise ValueError('Sealed prediction does not match config/team.json; do not edit after sealing.')
    if len(team.get('members', [])) != 3 or any('[' in m.get('name','') for m in team['members']):
        raise ValueError('Fill in all three team names before collecting data.')
    return team


def record(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def access_check(ua: str) -> None:
    if REPORT.exists():
        print('Access report already saved; checking existing caches only.')
        from how_sure_weather.cache import load_cached
        validate_weather_response(json.loads(load_cached(ROOT, 'open_meteo_probe')), minimum_days=7)
        scrape_wiki_normals(load_cached(ROOT, 'wikipedia_tirana'))
        print('Existing access-check responses verified. No requests sent.')
        return
    if local_date() != '2026-11-09':
        raise ValueError('Access check is scheduled for Monday 2026-11-09 in Europe/Tirane. Do not request early.')
    print('Checking Open-Meteo once (seven-day probe), then Wikipedia once. No retries.')
    weather = fetch_cached(
        ROOT, 'open_meteo_probe', weather_url('2020-08-01', '2020-08-07'),
        user_agent=ua, extension='json', allow_network=True,
    )
    validate_weather_response(json.loads(weather), minimum_days=7)
    html = fetch_cached(ROOT, 'wikipedia_tirana', WIKI_URL, user_agent=ua, extension='html', allow_network=True)
    _, wiki_meta = scrape_wiki_normals(html)
    record(REPORT, {
        'access_date_tirane': local_date(),
        'open_meteo_probe': 'successful and usable',
        'wikipedia_tirana': 'successful and climate box readable',
        'wikipedia_climate_caption': wiki_meta['chosen_caption'],
        'request_count_on_first_run': {'open_meteo': 1, 'wikipedia': 1},
    })
    print('Both access checks passed. Commit raw/ and processed/access_check_report.json.')


def collect_full(ua: str) -> None:
    if not REPORT.exists():
        raise ValueError('STOP: Monday access check not marked successful for both sources. Ask for help.')
    if not {'open_meteo_probe', 'wikipedia_tirana'}.issubset(read_manifest(ROOT)['entries']):
        raise ValueError('Missing Monday source caches. Do not collect full archive.')
    if local_date() < '2026-11-10':
        raise ValueError('Full collection starts Tuesday 2026-11-10, not before.')
    if 'open_meteo_full' in read_manifest(ROOT)['entries']:
        from how_sure_weather.cache import load_cached
        print('Already collected: reading existing full cache without sending a request.')
        weather = load_cached(ROOT, 'open_meteo_full')
    else:
        end = (datetime.now(ZoneInfo('Europe/Tirane')).date() - timedelta(days=1)).isoformat()
        url = weather_url('1940-01-01', end)
        print(f'Collecting ERA5 1940-01-01 through {end} in ONE archive request.')
        weather = fetch_cached(ROOT, 'open_meteo_full', url, user_agent=ua, extension='json', allow_network=True)
    payload = json.loads(weather)
    validate_weather_response(payload, minimum_days=1000)
    days = payload['daily']['time']
    if not any('1961-06-01' <= d <= '1990-08-31' for d in days) or not any('1991-06-01' <= d <= '2020-08-31' for d in days):
        raise ValueError('Full response does not appear to cover both comparison periods; STOP and ask for help.')
    record(COLLECTION_REPORT, {
        'collection_date_tirane': read_manifest(ROOT)['entries']['open_meteo_full']['access_date_tirane'],
        'first_returned_date': min(days),
        'last_returned_date': max(days),
        'returned_date_rows': len(days),
        'note': 'Returned dates may not match full requested dates. Assess missing days without filling them.',
        'full_archive_http_requests': 1,
    })
    print('Full archive cached. Commit raw/ and processed/collection_report.json.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=('access', 'full'), required=True)
    args = parser.parse_args()
    try:
        ua = actual_team()['user_agent']
        if args.stage == 'access':
            access_check(ua)
        else:
            collect_full(ua)
    except Exception as exc:
        raise SystemExit(f'STOP AND ASK FOR HELP: {type(exc).__name__}: {exc}') from exc


if __name__ == '__main__':
    main()
