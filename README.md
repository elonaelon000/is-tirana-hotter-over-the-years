# Has Summer Actually Gotten Hotter? — Group C

A transparent, reproducible study of **summer heat in Tirana**. We compare ERA5 gridded daily maximum temperatures in **1961–1990** versus **1991–2020** (June–August; a hot day is **strictly above 35°C**).

> **Research status (12 November 2026):** the design, research plan and offline analysis scaffold have been prepared, but the public repository does not yet contain a verified raw archive, executed results or final conclusions. No temperatures, intervals or findings are claimed here.

## Data and methods
- **Primary data:** [Open-Meteo historical ERA5 API](https://open-meteo.com/en/docs/historical-weather-api), point 41.3275° N / 19.8187° E, gridded reanalysis rather than station observations.
- **Sanity source:** [Wikipedia Tirana climate normals](https://en.wikipedia.org/wiki/Tirana#Climate), compared only after matching the exact years and metric.
- **Question 1:** hot-day numerator / valid summer-day denominator; 10,000 bootstrap resamples of **whole summer years** and 10,000 shuffled **year labels** as a no-change reference.
- **Question 2:** change in pooled summer daily maximum **mean** versus **95th percentile**, each with a year-block bootstrap interval.
- **No machine learning.** Cached original responses are required for offline notebook execution. Every reported number must carry its uncertainty range.

## Real team contributions
This is an **initial planning README**, not evidence that teammates finished work. Contributors will work under their **own GitHub accounts** on separate branches and pull requests:

| Role | Open task |
|---|---|
| Collector | Cache Open-Meteo and Wikipedia source responses with timestamps, original URL, hash manifest and missingness audit. |
| Contract / explorer | Confirm Wikipedia normal years and metrics, review the data contract, document the month-level same-period comparison. |
| Analyst | Independently execute the notebook offline; review rates, bootstrap/permutation assumptions, mean/P95 chart and conclusions; export verified website results. |

No fake commits or invented contributor credit. Please use the repository Issues to coordinate the actual work and include a peer review before merging.

## Coming after verified data collection
- Complete website with the cinematic Tirana/Dajti visual and scientific chart guide.
- Offline Jupyter notebook, original caches, contract CSV, evidence checklist, tests and figure-by-figure notes.
- README with **actual computed** results and ranges, original source provenance, real contributor PR links, and a confirmed GitHub Pages live-demo URL.

**Current status:** No live demo has been published; all research results remain pending. This README is the repository's collaboration starting point.