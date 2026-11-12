# How sure are you? — Group C: Has summer actually got hotter?

Ready-to-run, **not-yet-collected** three-person student project. No real data, statistics, plots or conclusions have been invented. The sealed prediction, three team names, User-Agent and Wikipedia normal-period confirmation are intentionally unfinished.

## Start here (Europe/Tirane dates)

1. **Sat–Sun 7–8 November 2026:** open `config/team.json`; replace `[NAME 1]`, `[NAME 2]`, `[NAME 3]`, the actual **contact-bearing User-Agent** and your **true pre-data prediction**. The User-Agent should be something like `Project3Weather/1.0 (contact: real-team-address@example.edu)` — not the placeholder. Run:
   ```sh
   python scripts/seal_prediction.py
   git add config scripts notebooks data_contract.csv README.md TEAM_CHECKLIST.md KNOWN_GAPS.md SLIDES_OUTLINE.md OFFLINE_CHECKLIST.md raw
   git commit -m "Prepare Group C and seal pre-data prediction"
   ```
   Never reseal after viewing source data. Follow `TEAM_CHECKLIST.md`.

2. **Mon 9 November — only authorized access check:**
   ```sh
   python scripts/collect.py --stage access
   git add raw processed/access_check_report.json
   git commit -m "Cache one access-check request for each source"
   ```
   This sends **one short seven-day ERA5 probe** and **one Wikipedia Tirana HTML** request, sequentially, with a descriptive User-Agent. It does not request the full archive yet. The API probe is an access check, not an analysis dataset. If either source is inaccessible or unusable: **stop and ask for help that day.** No retry loop.

3. **Tue 10 November — one complete archive request:**
   ```sh
   python scripts/collect.py --stage full
   git add raw processed/collection_report.json
   git commit -m "Cache single full-range ERA5 response"
   ```
   The script requests `https://archive-api.open-meteo.com/v1/archive`, coordinates `41.3275,19.8187`, `start_date=1940-01-01`, `end_date=yesterday` calculated in Tirana at execution, `daily=temperature_2m_max,temperature_2m_min,precipitation_sum`, `timezone=Europe/Tirane`, `models=era5`, Celsius and mm. **Explicit `models=era5` avoids silently substituting an automatically selected model.** The full-range archive response is *one request*, not a series of time chunks. The cache is keyed to the original URL and cannot silently change its end date on later offline runs.

4. **Wed–Sat 11–14 November — analysis, entirely from cache:**
   ```sh
   python -m pip install -r requirements.txt
   jupyter lab notebooks/01_how_sure_are_you.ipynb
   ```
   Run top to bottom. This notebook **never** sends HTTP requests. It writes daily data, summer-year coverage, computed CSVs and talk charts into `processed/` and `outputs/`. On Wednesday inspect `processed/wiki_metadata.json` and `processed/wiki_normals.csv`. If the Wikipedia mean-daily-maximum normal period can be proven from cached page caption / source note, copy `config/wiki_period_confirmation.example.json` to `config/wiki_period_confirmation.json`, set `confirmed=true`, the *actual* years and an evidence quote. Do not guess them. Without confirmation, the notebook **withholds** the sanity comparison, but completes the two main analyses.

5. **Sun 15 November — someone else's independent offline run:** install packages first; turn off Wi-Fi, restart the kernel and Run All. Or, with Wi-Fi physically disabled:
   ```sh
   OFFLINE=1 python scripts/offline_check.py
   ```
   The script checks cache SHA-256 integrity and executes all notebook cells, writing `outputs/verified_offline_run.ipynb`. See `OFFLINE_CHECKLIST.md`. You must have collected the raw responses first; the initial notebook intentionally fails fast if caches are missing.

## Directory layout

```text
how_sure_weather/
├── README.md, TEAM_CHECKLIST.md, KNOWN_GAPS.md
├── SLIDES_OUTLINE.md, OFFLINE_CHECKLIST.md
├── data_contract.csv                # one contract: 87 field entries / table, dtype, unit, source, gaps
├── config/
│   ├── team.json                    # REPLACE placeholders before Monday
│   ├── SEALED_PREDICTION.md         # seal with script before looking at data
│   └── wiki_period_confirmation.example.json
├── raw/                             # original files + SHA-256 manifest (commit all)
├── scripts/
│   ├── seal_prediction.py
│   ├── collect.py                   # the ONLY code that can go online
│   └── offline_check.py
├── src/how_sure_weather/
│   ├── cache.py, data.py, wiki.py, statistics.py, sanity.py, charts.py
├── notebooks/01_how_sure_are_you.ipynb
├── processed/                       # created from the cached responses
├── outputs/                         # figures and auto-filled talk numbers
└── tests/                           # local synthetic UNIT TESTS only, not findings
```

## What the analysis actually does

**Question one (chance above 35°C):** June–August with a **strict** daily-max threshold. For each period, show exact observed hot-day counts and denominators (and the missing/expected-day gap), the observed conditional hot-day base rate and its **95% year-block bootstrap range** (10,000 draws). Difference = rate in **1991–2020 minus 1961–1990**; independently resample whole summer years within each period. Separately shuffle the labels of 60 whole summer years 10,000 times to show the no-change reference histogram; label its observed difference and central shuffled 95% range. The shuffled extreme fraction has an interval for *finite Monte Carlo error*, not for climate variability.

**Question two (mean versus tail):** Compare pooled means and pooled 95th percentiles of all observed June–August daily maximum temperatures, difference late minus early in °C. Bootstrap both shifts **by whole year**, not by day. **No interval excluding zero → no claim of a detected change.** Use the resulting `outputs/mean_vs_tail_change.png`.

**Sanity check:** Wikipedia Tirana monthly climate normals are not daily observations. Confirm the precise normal years and row/source first; create ERA5 monthly normals from **the same years**, join by month, and compare. ERA5 year-block bootstrap ranges are conditional on Wikipedia's published normal point values. If source years are ambiguous, the sanity check says **WITHHELD**. It cannot establish a climate trend.

**Small-event risk:** a gridded ERA5 location may have very few days above 35°C. Keep the original strict threshold; do not optimize it. Flag fewer than 10 observed hot days in a period as a descriptive warning, show intervals and avoid treating zero-event bootstrap intervals as physical proof of zero risk. “We cannot tell” is an acceptable answer.

## Data contract and provenance

- `data_contract.csv` provides **every exported column** with table, expected type, unit, source and known gaps. `processed/coverage.json` reports missing *calendar dates*, while `processed/summer_year.csv` reports missing-or-null *summer maximum temperatures* (distinct concepts).
- All network requests use the real User-Agent, at least one second between requests within the sequential collector, no automatic retries. `raw/manifest.json` stores original URL, access date (Tirana), response hash and actual raw filename. Every later run opens those files by manifest key and verifies hashes.
- The API coordinates are one grid point, not a weather station. The period comparison uses only the ERA5 archive; outside years, including 2026, are excluded. ERA5 is approximately 25 km gridded reconstruction, so extreme highs may be smoothed. Wikipedia normals may refer to a different station/product.
- Credit **Open-Meteo ERA5 archive (ERA5 ECMWF/Copernicus; CC BY 4.0 per brief)** and **Wikipedia contributors, Tirana climate box and its cited underlying source**. Verify applicable attribution terms before publishing. See `KNOWN_GAPS.md` for limits.

## Reproducibility and correctness checks

Run `python -m unittest discover -s tests -v` before the Sunday execution. Tests use deliberately **synthetic in-memory fixtures** only to check cache and algorithm behavior; they are **not** project observations or findings. Real response files will appear only after their authorized collection days. The SHA-256 manifest makes corruption or accidental edits detectable. Keep the internet off for Sunday’s final test; setting `OFFLINE=1` alone is not a replacement for disconnecting.

For slide texts, use `SLIDES_OUTLINE.md`, replacing numeric placeholders solely from `outputs/talk_numbers.md` **after the notebook finishes**. The specified time slots are not exactly equal speaking time; rehearse the six-minute total. Share collection *problems* with Group D if useful, but **not analysis**.

## Browser-ready research website

The **`site/`** folder contains a complete offline-compatible, responsive
single-page website (`site/index.html`, `site/results.js`, `site/README.md`).
Open the HTML file directly in a browser to present the question, methods,
source credits and known limits. The three chart panels initially say
**awaiting verified data**; no measurements are invented. After running the
scheduled collection and offline notebook, populate the site from the actual
computed results using:

```sh
python scripts/export_website_data.py
```

Refresh `site/index.html` to see the observed hot-day rates and ranges, the
permutation histogram, and the mean-versus-95th-percentile chart. Read
`site/README.md` for GitHub Pages hosting notes. **This is a local website,
not a publicly deployed URL.**

---

## Project status / team workflow (12 November 2026)

**This is a reproducible project scaffold, not a completed climate finding.** Verified raw source responses and observed results were not included with the original provided project files; the website therefore shows *Awaiting verified data*. The archived access dates of 9–10 November are the planned schedule, not confirmed retrieval dates. No simulated values should be published as observations.

**Repository:** https://github.com/elonaelon000/is-tirana-hotter-over-the-years

**Website:** `site/index.html`. The mountain-and-red hero is derived from an **illustrative design concept**. It is not a photographic or scientific record. The main analysis displays actual computed values only after `python scripts/export_website_data.py` passes its checks.

**Documentation index:**

- [Scientific methods and every figure](docs/SCIENCE_AND_FIGURES.md) — explains all 3 probability methods, derived columns, data provenance, chart meanings and honest caveats.
- [Real contributor workflow](docs/TEAM_WORKFLOW.md) — three independent roles, branch names, PR evidence and no fabricated commit attribution.
- [Live demo and Pages instructions](docs/LIVE_DEMO.md) — how to prepare a truthful 2-minute demonstration; manual deploy, no invented URL.
- [Figure QA checklist](docs/FIGURE_CHECKLIST.md) — each chart must match notebook CSVs, zero-crossing interpretation and counts.
- [Project status log](docs/PROGRESS_LOG.md) — what is actually prepared versus blocked by uncollected data.
- [Existing known gaps](KNOWN_GAPS.md) and [offline checklist](OFFLINE_CHECKLIST.md).

### The team still needs to complete

| Task | Assigned role | Current state |
|---|---|---|
| Source-access logs, dated raw responses, hash manifest, missingness checks | Collector | **Pending genuine collection** |
| Wikipedia climate-box period check, contract review and justified monthly join | Contract & explorer | **Pending genuine source check** |
| Run notebook offline, validate all charts, independent range and permutation review, verified site export | Analyst | **Pending real source cache** |
| Final README results/conclusions, member names, real PR links and confirmed live demo URL | All three | **Pending team review** |

### Publishing the static website

The existing HTML, CSS and JavaScript need no framework or build step. `.github/workflows/pages.yml` is **manually triggered** to publish `site/` through GitHub Pages once the team approves its content. Select **Settings → Pages → GitHub Actions**, then **Actions → Publish verified climate research website → Run workflow**, and confirm the actual URL before putting a live-demo link here. See [the live-demo guide](docs/LIVE_DEMO.md).

### Final README sections to fill after real results exist

- **Contributors:** `[NAME 1 / GitHub handle]` — source collection; `[NAME 2 / handle]` — contract/Wikipedia; `[NAME 3 / handle]` — analysis. Describe what each **actually committed**, linked to their PRs.
- **Data collection date and provenance:** `[actual raw filename]`, `[source URL]`, `[SHA-256]`, `[date]`, `[status]`.
- **Observed results with uncertainty:** `[counts, denominators, hot-day rates and 95% ranges]`, `[difference and 95% range]`, `[permutation extreme-fraction estimate + Monte Carlo range]`, `[mean/P95 shifts and 95% ranges]`.
- **Review:** `[teammate independent offline verification]`, `[commit ID]`, `[passed checks]`.
- **Live demo:** `[confirmed Pages URL after actual deployment]`.

**Do not fill missing values with placeholders that look like computed results.**
