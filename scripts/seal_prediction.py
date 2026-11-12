#!/usr/bin/env python3
"""Seal the actual pre-registered statement before touching source data."""
import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TEAM = ROOT / 'config' / 'team.json'
SEAL = ROOT / 'config' / 'SEALED_PREDICTION.md'


def main():
    team = json.loads(TEAM.read_text(encoding='utf-8'))
    phrase = team['prediction'].strip()
    if len(team.get('members', [])) != 3 or any('[' in m.get('name','') or not m.get('name','').strip() for m in team['members']):
        raise SystemExit('Fill in all three real team names before sealing.')
    if not phrase or '[' in phrase or ']' in phrase:
        raise SystemExit('Replace [PREDICTION] in config/team.json with your pre-data statement first.')
    existing = SEAL.read_text(encoding='utf-8') if SEAL.exists() else ''
    if '**SHA-256:** [NOT SEALED]' not in existing:
        raise SystemExit('Prediction is already sealed; do not overwrite it.')
    manifest = ROOT / 'raw' / 'manifest.json'
    if manifest.exists() and json.loads(manifest.read_text(encoding='utf-8')).get('entries'):
        raise SystemExit('Raw responses already exist; cannot claim a new pre-data seal.')
    timestamp = datetime.now(ZoneInfo('Europe/Tirane')).isoformat(timespec='seconds')
    digest = hashlib.sha256(phrase.encode('utf-8')).hexdigest()
    members = ', '.join(member['name'] for member in team['members'])
    SEAL.write_text(
        '# Pre-registered prediction — SEALED, do not edit\n\n'
        f'**Text:** {phrase}\n\n'
        f'**Author/team:** {members}\n\n'
        f'**Sealed timestamp (Europe/Tirane):** {timestamp}\n\n'
        f'**SHA-256:** `{digest}`\n\n'
        'This is the team\'s pre-data hypothesis, not a model-generated forecast.\n',
        encoding='utf-8'
    )
    print(f'SEALED at {timestamp}, SHA-256 {digest}. Commit this file before the Monday access check.')


if __name__ == '__main__':
    main()
