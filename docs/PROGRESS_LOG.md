# Progress and evidence log

_Last reviewed: 12 November 2026. This is a truthful status record; mark tasks complete only after checking actual files and commits._

| Workstream | Status | Evidence / blocker | Intended contributor |
|---|---|---|---|
| Research design and two fixed period definitions | **Prepared** | `README.md`, `src/how_sure_weather/data.py` | Team review |
| Caching scripts, hash/URL provenance and validation code | **Prepared, unexecuted against live sources** | `scripts/collect.py`, `src/how_sure_weather/cache.py` | Name 1 |
| Access check (9 Nov) | **No archived response supplied** | Need `raw/manifest.json`, `processed/access_check_report.json`; do not backdate | Name 1 |
| Full Open-Meteo response (10 Nov) | **No archived response supplied** | Need dated raw JSON, verified units/date coverage | Name 1 |
| Wikipedia HTML and monthly normal period | **Unverified / uncollected in package** | Need original cached HTML and evidence for normal-years selection | Name 2 |
| CSV data contract | **Drafted; owner review pending** | `data_contract.csv` | Name 2 |
| Notebook and statistical methods | **Code prepared; real run pending** | `notebooks/01_how_sure_are_you.ipynb`, `src/how_sure_weather/statistics.py` | Name 3 |
| Project tests | **Run in this build on synthetic fixtures only** | Unit tests check code behavior, not climate results | Name 3 independent review |
| Annual heat stripes | **Visual placeholder** | `site/results.js` has no validated `year_stripes` export | Name 2/3 design agreement |
| Website | **Prepared, local preview** | `site/index.html` + static assets | Front-end integrator |
| Offline independent notebook run | **Not verified** | Actual raw cache + peer runner required | Team |
| Live GitHub Pages URL | **Not published** | Run manual Pages workflow after data/peer review | Team |
| Final README and study conclusion | **Requires verified metrics and names** | Do not invent figures or individual contribution credit | Team |

When complete, add the **real PR number, reviewer, commit SHA, timestamp, and validation artifacts** to each relevant entry. A planned task is not a completed contribution.
