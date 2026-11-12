"""Sequential, courteous, raw-response cache. Standard library only.

The notebook NEVER uses this module to fetch; only scripts/collect.py may
explicitly opt in to allow_network=True.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import time
from datetime import datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

_LAST_REQUEST_AT: float | None = None


def local_date() -> str:
    return datetime.now(ZoneInfo('Europe/Tirane')).date().isoformat()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_manifest(root: Path) -> dict[str, Any]:
    p = Path(root) / 'raw' / 'manifest.json'
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else {'entries': {}}


def load_cached(root: Path, cache_key: str) -> bytes:
    """Load and verify the exact cached response; NO network fallback."""
    root = Path(root)
    entry = read_manifest(root)['entries'].get(cache_key)
    if not entry:
        raise FileNotFoundError(
            f'Cache entry {cache_key!r} absent. Run scheduled collection first; '
            'the notebook cannot access the network.'
        )
    relative = Path(entry['file'])
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError(f'Unsafe manifest path for {cache_key}')
    cache_file = root / relative
    if not cache_file.exists():
        raise FileNotFoundError(f'Cached response missing: {cache_file}')
    raw = cache_file.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != entry['sha256']:
        raise ValueError(f'Cache SHA256 mismatch for {cache_key}: expected {entry["sha256"]}, got {actual}')
    return raw


def fetch_cached(
    root: Path,
    cache_key: str,
    url: str,
    *,
    user_agent: str,
    extension: str,
    allow_network: bool = False,
    min_interval_seconds: float = 1.0,
    timeout_seconds: float = 45.0,
) -> bytes:
    """Read an existing named cache, or explicitly fetch once and persist it.

    Raw filename: <cache_key>_<YYYY-MM-DD>_<URL-hash>.<extension>
    Cached entries are pinned to their original URL across future runs.
    All requests are serial; an elapsed-time throttle enforces >=1s between
    requests made by this process. This helper NEVER retries automatically.
    """
    global _LAST_REQUEST_AT
    root = Path(root)
    manifest = read_manifest(root)
    entry = manifest['entries'].get(cache_key)
    if entry:
        if entry['url'] != url:
            raise ValueError(
                f'{cache_key} is already pinned to a different URL. '
                'Do not silently change the date range or replace raw data.'
            )
        return load_cached(root, cache_key)

    if not allow_network or os.getenv('OFFLINE', '0') == '1':
        raise FileNotFoundError(f'{cache_key} is not cached. Network access disabled.')
    if not user_agent or ('[' in user_agent or ']' in user_agent or 'TEAM EMAIL' in user_agent):
        raise ValueError('Set a real, descriptive User-Agent containing a team contact before fetching.')
    if not extension.isalnum():
        raise ValueError('Use a simple file extension, such as json or html.')
    if _LAST_REQUEST_AT is not None:
        elapsed = time.monotonic() - _LAST_REQUEST_AT
        if elapsed < min_interval_seconds:
            time.sleep(min_interval_seconds - elapsed)

    req = Request(url, headers={'User-Agent': user_agent, 'Accept': '*/*'}, method='GET')
    _LAST_REQUEST_AT = time.monotonic()
    try:
        with urlopen(req, timeout=timeout_seconds) as response:
            status = response.status
            content_type = response.headers.get('Content-Type', '')
            raw = response.read()
    except HTTPError as exc:
        raise RuntimeError(f'HTTP {exc.code} from {url}; no automatic retry.') from exc
    except URLError as exc:
        raise RuntimeError(f'Connection failed for {url}; no automatic retry: {exc.reason}') from exc
    if status >= 400:
        raise RuntimeError(f'HTTP {status} for {url}; no automatic retry.')
    if not raw:
        raise RuntimeError(f'Empty response from {url}; no cache entry made.')

    folder = root / 'raw'
    folder.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(url.encode('utf-8')).hexdigest()[:12]
    name = f'{cache_key}_{local_date()}_{digest}.{extension}'
    path = folder / name
    # Exclusive creation protects against accidental replacement.
    with path.open('xb') as f:
        f.write(raw)
    manifest['entries'][cache_key] = {
        'url': url,
        'file': str(path.relative_to(root)),
        'access_date_tirane': local_date(),
        'http_status': status,
        'content_type': content_type,
        'size_bytes': len(raw),
        'sha256': hashlib.sha256(raw).hexdigest(),
        'user_agent': user_agent,
    }
    manifest_path = folder / 'manifest.json'
    tmp_path = folder / 'manifest.json.tmp'
    tmp_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    tmp_path.replace(manifest_path)
    return raw
