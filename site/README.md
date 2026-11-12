# Group C website — Tirana and Mount Dajti review edition

This is the **website source committed to GitHub** for the “How sure are you?” project; its initial public Pages deployment is **not yet enabled**. Open `index.html` in a modern browser. The site has no build step, API key or runtime weather-network request; fonts fall back to installed system fonts if the Google Fonts service is inaccessible.

## Files

- `index.html` — cinematic mountain homepage plus the original research sections and unchanged chart/result selectors.
- `science.html` — **new accessible method-by-method explanation**, including data lineage, cleaning, three probability methods, each graph and offline QA.
- `styles.css` — full responsive design for both pages, dark hero and light research sections.
- `motion.js` — visual-only scroll effects, mobile menu, stripe interaction and download dialog.
- `data-view.js` — **unchanged** result and chart renderer from the original supplied project.
- `results.js` — **unchanged** placeholder until the verified notebook output exists.
- `data_contract.csv` — **unchanged** project contract.
- `img/dajti-concept.webp` — visual **illustration**, not evidence of climate observations.
- `DESIGN_NOTES.md` — layout rationale and integrity rules.

## Reproducible scientific workflow

From the **full project root**, configure real names, User-Agent and the genuine sealed prediction; collect the authorized source responses to `raw/` using the respectful collector, then run the notebook offline with network disabled. The site initially says “Awaiting verified data”; it never invents weather values or conclusions.

Only after real, reviewed results exist:

```sh
python -m unittest discover -s tests -v
OFFLINE=1 python scripts/offline_check.py
python scripts/export_website_data.py
```

The exporter writes verified values into the existing `site/results.js` object. The website’s existing renderer then fills the rate comparison, permutation histogram and mean-versus-tail chart without changing formulas.

A user-friendly explanation is linked inside the site as **“FULL METHOD NOTES”** (`science.html`). For full source-level details, read `docs/SCIENCE_AND_FIGURES.md` in the complete project.

## Publishing

**Repository source is public, but a live Pages deployment has not yet succeeded.** Enable Pages via repository Settings → Pages → GitHub Actions, then rerun the `Publish Group C website` workflow. Raw climate data, completed analysis and teammate contributions are still pending; the site must not display unverified findings. See `docs/LIVE_DEMO.md` and `docs/TEAM_WORKFLOW.md`.
