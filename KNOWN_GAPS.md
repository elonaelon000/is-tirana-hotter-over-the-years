# Known gaps, decisions and limits

Every item is documented **before** analysis and audited again after collection. The corresponding issues appear in `data_contract.csv` in its `known_gaps` column.

| Known gap or decision | Precommitted treatment | What to verify / record |
|---|---|---|
| Comparison periods | Use 1961–1990 vs 1991–2020, inclusive (30 summers each). | Verify returned dates and actual maximum-temperature coverage of **all** summer days, especially 1991–2020. |
| Summer definition | Only June, July, August; 92 calendar days per summer year. | Record raw date rows and nonnull daily maxima versus expected. |
| Hot-day definition | Strictly `temperature_2m_max > 35.0` °C. | Do not change to `>=35` after looking at counts. |
| Missing dates and null daily maxima | Count both; never interpolate, extrapolate or treat missing maximum as a non-hot day. | `processed/coverage.json`, `processed/summer_year.csv`; show denominators. |
| Incomplete/current summer | Exclude 2026 from ALL main period comparisons even if its summer has already passed; avoid mixing partial most-recent years into trends. | Period label is `NA` for 2026; the main comparison ends in 2020. |
| ERA5 is not a thermometer | The archive represents a coarse (~25 km) reanalysis grid, not a Tirana station. Extremes may be muted. | Cite provider and ERA5; treat 35°C threshold with special caution. |
| Very few hot days | Keep threshold, report exact observed counts and wide year-block bootstrap ranges; if events are zero, state bootstrap cannot rule out unseen rare events. | Flag either period with fewer than 10 observed hot days as a **descriptive** sparsity warning (not a new statistical test). |
| Wikipedia climate normals period | A candidate year range is **not** verification. Check caption, row, source note, station and years. | Person 2 documents quote and correct dates in `config/wiki_period_confirmation.json`. If uncertain, **withhold** sanity comparison. |
| Different observation types | ERA5 grid daily-max averages can differ from station-published monthly normals. | Compare only overlapping years and matching monthly mean daily maximum units; do not infer a climate trend from this difference alone. |
| Autocorrelation within seasons | Entire summer-year is the bootstrap/permutation unit. | 10,000 draws with fixed seeds; no random daily reordering. |
| Dependence across years | Year-block bootstrap handles same-year dependence, not all multi-year persistence or changing measurement error. | Limit causal and certainty claims. |
| Permutation-world assumption | Exchange year labels between two groups of 30 under an exchangeable no-period-difference baseline. | The shuffled 95% range is a null **reference**, not a forecast or confidence interval for a future temperature. |
| Source availability and courtesy | Mon: one source access each. Tue: one full archive request. Reuse local cache indefinitely. | Request URLs, responses, access dates, `User-Agent`, hashes in `raw/manifest.json`; no automatic retries. |
| Source licensing | Credit Open-Meteo ERA5 and the original ERA5 source; attribute the Wikipedia Tirana climate box. | Keep citations and access dates; obey source terms and attribution requirements. |

## Put on the final slide: limits (choose 4–6)

- These are **ERA5 reconstructed grid temperatures**, not local station thermometer readings; the spatial grid can smooth rare extreme heat.
- A small number of days above 35°C makes tail estimates unstable; a zero-width empirical bootstrap interval following zero events is **not** proof of zero underlying risk.
- Missing daily values are counted but not filled, and unequal coverage may affect the denominator.
- Year-block resampling captures clustering within summers; it does **not** resolve every long-term dependency or measurement bias.
- The permutation histogram shows what happens when **year labels** are exchangeable under no period effect; it is not a physical weather simulation.
- Wikipedia monthly normals may describe a different station, climatological period, or observation product; sanity comparisons need verified matching years and cannot establish a trend by themselves.
- An interval crossing zero means **"we cannot tell"** from this dataset and method. Even an interval excluding zero does not prove a cause.

**Status now:** No live sources have been contacted and no results exist in this template. All counts, years of Wikipedia normals and findings are **[PENDING CACHE]**.
