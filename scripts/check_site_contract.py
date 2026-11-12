#!/usr/bin/env python3
"""Non-scientific static integrity check: expected charts, assets, IDs exist."""
from pathlib import Path
from html.parser import HTMLParser
ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'

class Inspect(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids = set(); self.local_refs = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            if a['id'] in self.ids: raise AssertionError('Duplicate HTML ID: '+a['id'])
            self.ids.add(a['id'])
        for key in ('src','href'):
            ref = a.get(key,'')
            if ref and not ref.startswith(('#','http:', 'https:', 'data:', 'mailto:','../')):
                self.local_refs.append(ref.split('#')[0].split('?')[0])

v = Inspect(); v.feed((SITE/'index.html').read_text(encoding='utf-8'))
required = {'early-rate','late-rate','diff-rate','rate-chart','null-chart','tail-chart',
            'mean-summary','tail-summary','shuffle-note','q1-conclusion','q2-conclusion',
            'coverage-note','stripe-track','stripe-readout','status-label','download-data'}
assert not required.difference(v.ids), f'Missing required renderer IDs: {required.difference(v.ids)}'
for ref in v.local_refs:
    assert (SITE/ref).is_file(), f'Missing local website reference: {ref}'
print(f'OK: {len(required)} renderer IDs and {len(v.local_refs)} local file references verified')
