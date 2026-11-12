#!/usr/bin/env python3
"""Check provenance then execute notebook with OFFLINE=1; Wi-Fi should be off."""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from how_sure_weather.cache import load_cached, read_manifest


def main():
    expected = ('open_meteo_probe', 'wikipedia_tirana', 'open_meteo_full')
    manifest = read_manifest(ROOT)
    for name in expected:
        raw = load_cached(ROOT, name)
        print(f'OK {name}: sha256 verified ({len(raw)} bytes)')
    assert (ROOT / 'processed' / 'access_check_report.json').exists(), 'Missing Monday access report'
    assert (ROOT / 'processed' / 'collection_report.json').exists(), 'Missing Tuesday collection report'
    if not (ROOT / 'config' / 'SEALED_PREDICTION.md').read_text(encoding='utf-8').startswith('# Pre-registered prediction — SEALED'):
        raise RuntimeError('No sealed prediction')
    env = os.environ.copy()
    env['OFFLINE'] = '1'
    env['PYTHONPATH'] = str(ROOT / 'src') + os.pathsep + env.get('PYTHONPATH', '')
    command = [
        sys.executable, '-m', 'jupyter', 'nbconvert', '--to', 'notebook', '--execute',
        '--ExecutePreprocessor.timeout=600',
        '--output', 'verified_offline_run.ipynb', '--output-dir', 'outputs',
        'notebooks/01_how_sure_are_you.ipynb',
    ]
    print('Run with Wi-Fi/network physically OFF. Running notebook against cache only...')
    subprocess.run(command, cwd=ROOT, env=env, check=True)
    print('PASS: cache hashes checked and notebook executed without opting into network.')
    print('Evidence: outputs/verified_offline_run.ipynb')


if __name__ == '__main__':
    main()
