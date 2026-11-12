"""Extract Tirana monthly climate normals from the CACHED Wikipedia HTML.

No assumption is made about which normal years apply: an explicit, sourced
manual confirmation is required before comparing the two datasets.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
from .cache import load_cached

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
WIKI_URL = 'https://en.wikipedia.org/wiki/Tirana'


def identify_metric(label: str) -> tuple[str, str] | None:
    # Match specific labels, not record-high temperatures or rain-day counts.
    lower = re.sub(r'\s+', ' ', label.lower().replace('−', '-'))
    if re.search(r'average high|mean daily maximum|average daily maximum|average maximum|mean maximum', lower):
        return ('mean_daily_max_c', 'C')
    if re.search(r'average low|mean daily minimum|average daily minimum|average minimum|mean minimum', lower):
        return ('mean_daily_min_c', 'C')
    if re.search(r'daily mean|mean temperature|average mean', lower):
        return ('mean_daily_c', 'C')
    if re.search(r'average precipitation|mean precipitation|precipitation amount', lower) and not re.search(r'days|rainy days', lower):
        return ('mean_precip_mm', 'mm')
    return None


def first_numeric(text: str) -> float | None:
    # Wikipedia often shows Celsius followed by Fahrenheit: "11.2 (52.2)".
    # Wikipedia footnote numbers should be removed by BeautifulSoup first.
    cleaned = text.replace('−', '-').replace('–', '-').replace(',', '.')
    if cleaned.strip().lower() in ('-', '—', 'n/a', 'na', 'no data'):
        return None
    match = re.search(r'[-+]?\d+(?:\.\d+)?', cleaned)
    return float(match.group(0)) if match else None


def _extract_normal_period_candidates(text: str) -> list[str]:
    matches = re.findall(r'(?<!\d)((?:18|19|20)\d{2})\s*[-–—]\s*((?:18|19|20)\d{2})(?!\d)', text)
    return sorted(set(f'{start}-{end}' for start, end in matches))


def scrape_wiki_normals(html_bytes: bytes) -> tuple[pd.DataFrame, dict]:
    """Return tidy monthly values and provenance for a Tirana climate box.

    If a metric or its years cannot be established from the cached HTML, retain
    the uncertainty. Do not invent an implied station observation or period.
    """
    soup = BeautifulSoup(html_bytes, 'html.parser')
    candidates = []
    for table in soup.select('table'):
        caption_element = table.find('caption')
        if caption_element is None:
            continue
        caption = caption_element.get_text(' ', strip=True)
        if 'climate data' not in caption.lower() or 'tirana' not in caption.lower():
            continue
        extracted = []
        for tr in table.find_all('tr'):
            header = tr.find('th')
            if header is None:
                continue
            label = header.get_text(' ', strip=True)
            metric_info = identify_metric(label)
            if metric_info is None:
                continue
            # Direct TD cells: 12 months, optionally a Year column.
            cells = tr.find_all('td', recursive=False)
            if len(cells) < 12:
                continue
            metric, unit = metric_info
            for i, cell in enumerate(cells[:12]):
                clone = BeautifulSoup(str(cell), 'html.parser')
                for unwanted in clone.select('sup, .reference, .sortkey'):
                    unwanted.decompose()
                value = first_numeric(clone.get_text(' ', strip=True))
                extracted.append({
                    'month': i + 1,
                    'metric': metric,
                    'value': value,
                    'unit': unit,
                    'row_label': label,
                    'caption': caption,
                })
        source_lines = []
        for tr in table.find_all('tr'):
            line = tr.get_text(' ', strip=True)
            if re.search(r'\bsource\s*:', line, re.IGNORECASE):
                source_lines.append(line[:600])
        score = len({row['metric'] for row in extracted})
        if score:
            candidates.append((score, caption, extracted, source_lines))
    if not candidates:
        raise ValueError(
            'No Tirana climate table with recognized monthly labels found. '
            'Inspect cached HTML manually, document a parser correction, and rerun offline.'
        )
    candidates.sort(key=lambda c: c[0], reverse=True)
    if len(candidates) > 1 and candidates[0][0] == candidates[1][0]:
        raise ValueError(
            'More than one equally matching Tirana climate table. '
            'Choose deliberately and document the choice; do not guess.'
        )
    score, caption, rows, source_lines = candidates[0]
    df = pd.DataFrame(rows).drop_duplicates(['month', 'metric'], keep='first')
    df['source_url'] = WIKI_URL
    df['source_note'] = ' | '.join(source_lines)
    caption_periods = _extract_normal_period_candidates(caption)
    df['normals_period_candidate'] = caption_periods[0] if len(caption_periods) == 1 else pd.NA
    df['period_status'] = 'UNVERIFIED - manual evidence required'
    metadata = {
        'chosen_caption': caption,
        'caption_period_candidates': caption_periods,
        'source_note': ' | '.join(source_lines),
        'row_labels': sorted(df['row_label'].unique().tolist()),
        'parsed_metrics': sorted(df['metric'].unique().tolist()),
        'other_candidate_tables': [x[1] for x in candidates[1:]],
        'period_status': 'UNVERIFIED - manual confirmation required for sanity check',
        'note': 'Inspect caption, relevant metric row, source notes and their years; they may differ by metric.',
    }
    df = df.sort_values(['metric', 'month']).reset_index(drop=True)
    return df, metadata


def read_cached_wiki(root: Path) -> tuple[pd.DataFrame, dict]:
    return scrape_wiki_normals(load_cached(root, 'wikipedia_tirana'))


def load_period_confirmation(root: Path, metadata: dict) -> tuple[int, int] | None:
    """Only use manually confirmed years backed by an exact cached page quote."""
    p = Path(root) / 'config' / 'wiki_period_confirmation.json'
    if not p.exists():
        return None
    record = json.loads(p.read_text(encoding='utf-8'))
    if not record.get('confirmed'):
        return None
    start = record.get('start_year')
    end = record.get('end_year')
    evidence = record.get('evidence_quote', '')
    metric = record.get('metric', '')
    if not isinstance(start, int) or not isinstance(end, int) or start < 1940 or end > 2025 or start > end:
        raise ValueError('Invalid manually confirmed Wikipedia normal years')
    if metric != 'mean_daily_max_c':
        raise ValueError('Confirmation must explicitly apply to mean_daily_max_c, not an unrelated Wikipedia row.')
    if len(evidence.strip()) < 12:
        raise ValueError('Document the wording proving the Wikipedia normal years in evidence_quote')
    # Validate that the asserted quote appears in the *cached* page text,
    # not an invented or externally sourced summary. This still requires
    # human verification that the years apply to the correct weather row.
    page = BeautifulSoup(load_cached(root, 'wikipedia_tirana'), 'html.parser').get_text(' ', strip=True)
    normalized_page = ' '.join(page.split()).casefold().replace('–', '-').replace('—', '-')
    normalized_quote = ' '.join(evidence.split()).casefold().replace('–', '-').replace('—', '-')
    if normalized_quote not in normalized_page:
        raise ValueError('The evidence_quote is not present in the locally cached Wikipedia page')
    if str(start) not in evidence or str(end) not in evidence:
        raise ValueError('Evidence quote must explicitly identify both normal-period years')
    return start, end
