"""Tests use SYNTHETIC fixtures, NEVER real weather observations/results."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from how_sure_weather.cache import load_cached, fetch_cached
from how_sure_weather.data import load_daily_json, summer_year_table
from how_sure_weather.statistics import rate_bootstrap, permutation_null, mean_tail_bootstrap
from how_sure_weather.wiki import scrape_wiki_normals
from how_sure_weather.sanity import compare_monthly_normals


class TestPipeline(unittest.TestCase):
    def test_cache_never_fetches_without_permission(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                fetch_cached(Path(tmp), 'example', 'https://invalid.example/path',
                             user_agent='Example/1.0 contact@example.edu', extension='json')
            (Path(tmp) / 'raw').mkdir()
            sample = b'{"made_up_fixture":true}'
            (Path(tmp) / 'raw' / 'fake_2026-11-09_deadbeef.json').write_bytes(sample)
            (Path(tmp) / 'raw' / 'manifest.json').write_text(json.dumps({'entries': {'example': {
                'file': 'raw/fake_2026-11-09_deadbeef.json',
                'url': 'https://invalid.example/path',
                'sha256': hashlib.sha256(sample).hexdigest(),
            }}}))
            self.assertEqual(load_cached(Path(tmp), 'example'), sample)
            self.assertEqual(fetch_cached(Path(tmp), 'example', 'https://invalid.example/path',
                             user_agent='Example/1.0 contact@example.edu', extension='json'), sample)
            with self.assertRaises(ValueError):
                fetch_cached(Path(tmp), 'example', 'https://invalid.example/changed',
                             user_agent='Example/1.0 contact@example.edu', extension='json')

    def synthetic_weather(self):
        # NOT a historical archive, just known 1-day/year fake values testing threshold.
        dates = [f'{year}-07-01' for year in range(1961, 2021)]
        max_values = [35.0 if year <= 1990 else 35.1 for year in range(1961, 2021)]
        body = {
            'timezone': 'Europe/Tirane',
            'daily_units': {'temperature_2m_max': '°C', 'temperature_2m_min': '°C', 'precipitation_sum': 'mm'},
            'daily': {'time': dates, 'temperature_2m_max': max_values,
                      'temperature_2m_min': [15.0] * 60, 'precipitation_sum': [0] * 60}
        }
        return load_daily_json(json.dumps(body))

    def test_strict_hot_threshold_and_year_resampling(self):
        df = self.synthetic_weather()
        self.assertFalse(bool(df.loc[df.year.eq(1961), 'is_hot'].iloc[0]))
        self.assertTrue(bool(df.loc[df.year.eq(1991), 'is_hot'].iloc[0]))
        y = summer_year_table(df)
        self.assertEqual(len(y), 60)
        self.assertEqual(y.loc[y.period.eq('1991-2020'), 'hot_days'].sum(), 30)
        rate, diff = rate_bootstrap(y, draws=100, seed=123)
        self.assertEqual(float(rate.iloc[0]['rate']), 0)
        self.assertEqual(float(rate.iloc[1]['rate']), 1)
        self.assertEqual(diff['observed_difference'], 1)
        null = permutation_null(y, diff['observed_difference'], draws=200, seed=123)
        self.assertEqual(len(null['distribution']), 200)
        changes, _ = mean_tail_bootstrap(df, draws=50, seed=123)
        self.assertEqual(len(changes), 2)
        self.assertGreater(float(changes.loc[changes.metric.eq('mean_daily_summer_max'), 'observed_change'].iloc[0]), 0)

    def test_missing_max_stays_unknown(self):
        df = self.synthetic_weather()
        df.loc[df.year.eq(1961), 'temperature_2m_max'] = float('nan')
        # Recompute from JSON rather than edit flags to test parse contract.
        raw = {'timezone': 'Europe/Tirane',
               'daily_units': {'temperature_2m_max': '°C', 'temperature_2m_min': '°C', 'precipitation_sum': 'mm'},
               'daily': {'time': ['1991-06-01', '1991-06-02'],
                         'temperature_2m_max': [35.0, None],
                         'temperature_2m_min': [12, 13], 'precipitation_sum': [0, 0]}}
        parsed = load_daily_json(json.dumps(raw))
        self.assertFalse(bool(parsed['is_hot'].iloc[0]))
        self.assertTrue(parsed['is_hot'].isna().iloc[1])

    def test_wikipedia_parses_monthly_rows_but_does_not_verify_year(self):
        vals = ''.join(f'<td>{10 + i}.5 (50.0)</td>' for i in range(12))
        markup = ('<html><table class="wikitable"><caption>Climate data for Tirana (1991–2020 normals)</caption>'
                  '<tr><th>Month</th>' + ''.join(f'<th>{x}</th>' for x in ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']) + '</tr>'
                  '<tr><th>Average high °C (°F)</th>' + vals + '<td>20.0</td></tr>'
                  '<tr><td colspan="14">Source: synthetic fixture</td></tr></table></html>')
        normals, meta = scrape_wiki_normals(markup.encode())
        self.assertEqual(normals['month'].nunique(), 12)
        self.assertEqual(normals['metric'].unique().tolist(), ['mean_daily_max_c'])
        self.assertEqual(normals['normals_period_candidate'].iloc[0], '1991-2020')
        self.assertTrue(all(normals['period_status'].str.contains('UNVERIFIED')))
        self.assertEqual(meta['caption_period_candidates'], ['1991-2020'])


if __name__ == '__main__':
    unittest.main()
