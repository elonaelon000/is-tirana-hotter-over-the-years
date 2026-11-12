# Science and figure guide — Has summer actually got hotter?

> **Status (12 November 2026):** analysis software and display templates exist, but no real Open-Meteo archive response, cached Wikipedia climate box or validated study outputs are present in the provided project package. The repository must not claim that the answer is yes, no or statistically detected until the offline notebook has been run on actual cached responses and independently verified.

## What the project asks

**Q1 (frequency):** Did the observed probability that a June–August day has an ERA5 grid-cell daily maximum **strictly greater than 35 °C** change between **1961–1990** and **1991–2020**?

**Q2 (distribution):** Did the **pooled mean** and the **pooled 95th percentile** of June–August daily maximum temperature shift by different amounts?

The 1940–2026 archive is collected for provenance and possible context. The two fixed 30-year periods are the **only** primary statistical comparison. The incomplete current summer is not included. The sealed prediction must be recorded before looking at results; `config/SEALED_PREDICTION.md` must not be retroactively altered.

## Source provenance and matching observations

- **Primary:** Open-Meteo Historical Weather API, **explicit `models=era5`**, one point at **41.3275° N, 19.8187° E**, timezone `Europe/Tirane`. ERA5 is approximately **0.25° / ~25 km gridded reanalysis**, not a thermometer at an urban weather station; the representativeness of extremes is limited. Daily `temperature_2m_max` and `temperature_2m_min` are in °C; `precipitation_sum` is in mm. Source: https://open-meteo.com/en/docs/historical-weather-api
- **Secondary:** English Wikipedia page *Tirana*, climate table, **monthly published normals**. It is a sanity check **only**, never part of the daily denominator or trend estimator. Its caption and *specific normal years* must be verified in `config/wiki_period_confirmation.json`; otherwise label the check **WITHHELD**. Source: https://en.wikipedia.org/wiki/Tirana#Climate
- Every raw HTTP response goes to `raw/` with access date and SHA-256 provenance in `raw/manifest.json`. Only `scripts/collect.py` contacts sources. Subsequent notebooks and site exports must work from cache.

## Data contract, data types, and cleaning

The canonical column-by-column, typed contract is [`../data_contract.csv`](../data_contract.csv). The steps are:

1. Read `raw/manifest.json`, pin request URL, check SHA-256 and read the cached JSON bytes.
2. `json.loads()` converts the outer JSON text to Python mappings and lists; read `payload['daily']` containing equal-length arrays of dates, maxima, minima, and precipitation.
3. `pd.DataFrame` puts each set of daily values into a row. Convert `time` to Pandas `datetime64`; numerical variables to `float64`. Preserve source units.
4. Reject duplicates and misaligned arrays. Verify weather response, timezone, date coverage and data types; record **missing dates** and **null temperatures** separately.
5. Derive `year`, `month`, `is_summer = month ∈ {6,7,8}`, `period` and `is_hot = temperature_2m_max > 35`. If a day's maximum is missing, `is_hot = <NA>`, **not False**.
6. Retain **exactly** summer days in 1961–2020 for period comparisons; include all 30 year slots per period, even if they have missing values. Do not fill, interpolate, or delete missing months without reporting the change in denominators.
7. Write transformed data to `processed/`, preserving unchanged raw responses. The website consumes `site/results.js` **only after** `scripts/export_website_data.py` verifies outputs against the cache.

Short illustrative snippet (logic from the existing project):

```python
import json
import pandas as pd
with open("raw/<dated-response-file>.json", encoding="utf-8") as file:
    payload = json.load(file)
df = pd.DataFrame(payload["daily"])
df["time"] = pd.to_datetime(df["time"], errors="raise")
df["year"] = df["time"].dt.year
df["month"] = df["time"].dt.month
summer = df[df["month"].isin([6, 7, 8]) & df["year"].between(1961, 2020)].copy()
summer["is_hot"] = summer["temperature_2m_max"].gt(35.0)
summer.loc[summer["temperature_2m_max"].isna(), "is_hot"] = pd.NA
```

For the **actual notebook**, use `src/how_sure_weather/data.py` and `read_cached_daily(root)`, not a guessed raw filename. `JSON → DataFrame → CSV` is a transformation; it does not add new weather readings.

## Table: every figure and what it proves (or does not prove)

| Website location | What is plotted | Underlying processed output | How to read it | Essential caveat |
|---|---|---|---|---|
| `#stripes` annual index | One placeholder position per year 1940–2026. Neutral unless verified `year_stripes` are exported | **Not yet connected** to verified annual anomalies | Annual anomaly relative to a **declared** reference period, after teammate implements and documents aggregation | **Do not color from guesswork**. Missing ≠ cool. Do not substitute this for the primary comparison. |
| `#rate-chart` | Observed percentage of valid June–August days with daily max > 35 °C in each period; horizontal 95% intervals | `processed/period_rates.csv` | Dot = observed rate; bar = percentile bootstrap interval for that estimate | The unit resampled is **the whole year**, not independent days. Denominators must be shown. |
| `#null-chart` | Histogram of 10,000 differences after year-label shuffling; vertical line = observed difference | `processed/permutation_summary.csv` and reconstructed shuffle values from `processed/summer_year.csv` | Compare observed difference to the shuffled reference distribution | No-change null reference is conditional on exchangeability; **not a forecast**. |
| `#tail-chart` | 1991–2020 minus 1961–1990 pooled mean and P95 daily maximum changes (°C), with year-block 95% intervals | `processed/question_two_changes.csv` | Zero is the reference. If the **interval includes zero**, do not claim the statistic changed | Mean and 95th percentile describe different characteristics, do not conflate them. |
| Wikipedia sanity check | Monthly ERA5 mean-daily-maximum vs published matching-month normals | `processed/wiki_monthly_comparison.csv` **only if verified** | Difference conditional on exactly matched source years | Different locations, instruments, sources and reference periods can explain gaps; do not call it a warming trend. |

**Display contract:** no colored annual stripes, no filled numerical panels, no positive/negative verdict and no computed charts unless the offline export has validated real results. The printed results must match the notebook output, not manually entered website values. `site/data-view.js` renders three charts; `scripts/export_website_data.py` writes the verified data object.

## Probability methods and uncertainty — equations

Let `h_y` be the count of observed days above 35 °C in summer year `y`, and `n_y` the count of days with nonmissing summer maximums. For period `P`:

`p(P) = (Σ_y∈P h_y) / (Σ_y∈P n_y)`.

Report **hot-day counts / valid-day counts**, the observed rate, and a 95% interval. Difference: `Δp = p(1991–2020) − p(1961–1990)` in **percentage points**, not relative percent.

**Year-block bootstrap, 10,000 draws.** Within each period, sample 30 whole summers **with replacement**. Recalculate pooled rates using the sampled sums of `h_y` and `n_y`; separately recalculate the pooled summer maximum mean and pooled P95. Use the 2.5th and 97.5th percentiles as the reported **bootstrap ranges**. Seeds live in `src/how_sure_weather/statistics.py` (`SEEDS`). Resampling days would understate dependence within a summer. A 95% bootstrap range does not make ERA5 or Wikipedia perfect.

**Year-label permutation, 10,000 draws.** Pool 60 annual summer records, randomly divide them into two 30-year groups, and recompute the rate difference. The histogram is a **no-period-difference reference**; mark the actual observed `Δp`. Its two-sided extreme fraction can be estimated with `(extreme_count + 1) / (draws + 1)`. The finite Monte Carlo range of that fraction is **not** a climate-confidence interval.

**Mean versus tail.** `Δmean = mean_late − mean_early`; `ΔP95 = quantile(late, .95) − quantile(early, .95)` where each quantile is over all valid summer daily maxima pooled within a period. Bootstrap differences by resampling **years**, not days. Never call a shift statistically resolved if its corresponding bootstrap range covers zero.

## More limits reviewers should know

1. **Spatial scale:** ERA5's grid size (~25 km) can smooth local heat extremes, especially around terrain and urban microclimates. The result describes a grid cell; it is not a measured station trend.
2. **Temporal grouping:** bootstrap whole summers captures within-year clustering but does not fully address autocorrelation across nearby years; the year-label permutation assumes exchangeability under its reference.
3. **Rare events:** if `>35 °C` events are scarce, uncertainty is broad. A zero event count is not proof that heat never occurs.
4. **Missingness:** missing dates and null daily maxima must be listed by period; don't silently count missing days as non-hot.
5. **Wikipedia normals:** published station normals may be from airport/other location and cover different decades; only compare same years and same metric, or withhold comparison.
6. **Observational scope:** a descriptive difference across two periods does not attribute warming to a specific cause, nor does it forecast future heat.
7. **No model:** no ML training, predictions, scikit-learn or accuracy; ERA5 itself is a preexisting reanalysis dataset, not a model fitted by this student project.
8. **Site vs analysis:** CSS heat colors and hero haze are illustration; they are not data visualization. Numerical results must come from the verified notebook.

## Checklist before publishing any result

- [ ] Genuine source responses saved under `raw/`, URLs and SHA-256 recorded, and requests respectful.
- [ ] Prediction truly predeclared before anyone observed the outcome.
- [ ] Full 1961–2020 summer coverage checked; missing dates and nulls separately reported.
- [ ] All intervals and counts in the notebook and website match exactly.
- [ ] Source of every plot visible in notebook, README, and site.
- [ ] Wikipedia years confirmed or sanity check explicitly WITHHELD.
- [ ] No result described as a *fact* if its uncertainty interval includes zero.
- [ ] A teammate who did not write the analysis runs the notebook offline from a clean kernel.
- [ ] `python -m unittest discover -s tests -v` and `python scripts/offline_check.py` pass **with cached files**.
- [ ] `scripts/export_website_data.py` validates exported results; site is checked in desktop and mobile views.

## Sources

- [Open-Meteo Historical Weather API and ERA5 details](https://open-meteo.com/en/docs/historical-weather-api)
- [ERA5 data and licence (Open-Meteo API OpenAPI)](https://github.com/open-meteo/open-meteo/blob/main/openapi/historical-weather.yml)
- [Wikipedia: Tirana — Climate](https://en.wikipedia.org/wiki/Tirana#Climate)
- [Project data contract](../data_contract.csv)
- [Reproducible notebook](../notebooks/01_how_sure_are_you.ipynb)
