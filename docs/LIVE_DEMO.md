# Live-demo script and publishing checklist

## Current public state

The repository and web design scaffold are **not automatically a published live demo**. Until real cached Open-Meteo observations have been analyzed and verified, the site must keep **results pending** labels and its scientific stripes neutral. The mountain visual is **an illustrative design composite**, not a temperature map or photograph.

## Prepare the project

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
# Collector must first fetch the two actual raw source responses with the agreed User-Agent.
# Then open notebooks/01_how_sure_are_you.ipynb and Run All OFFLINE.
OFFLINE=1 python scripts/offline_check.py
python scripts/export_website_data.py
```

**Do not run the last two commands expecting success before the source files have been collected.** The exporter explicitly refuses to publish missing/invalid results.

## Live demo in roughly two minutes

1. **00:00–00:20 — Question/scene.** Show Tirana/Dajti hero; clarify this is editorial illustration and the research question is not answered by an image. State fixed JJA definition and strict max > 35 °C.
2. **00:20–00:45 — Provenance/contract.** Open Open-Meteo link, explain ERA5 gridded reanalysis and show the contract CSV. Point to the raw cache manifest with date and hash.
3. **00:45–01:15 — Question 1.** Scroll to rate chart, read valid-day denominators, observed rate + 95% range. Show the permutation histogram and its observed marker. Explain why years are the units in both methods.
4. **01:15–01:40 — Question 2.** Show mean-versus-95th-percentile graph. Explain what zero means and whether each interval includes zero; do not claim a detected change if it does.
5. **01:40–02:00 — Verification.** Show tests, copied commands, README's exact steps and notebook offline execution. Acknowledge limits and whether Wikipedia period matching was verified or withheld.

Replace spoken numeric placeholders only after completed, verified outputs exist. The presenter should be able to navigate to each output CSV from the README.

## GitHub Pages: static `site/` folder

1. The initial reviewed project source is committed to `main` (do not fabricate teammates' future commits).
2. Open repository **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. In **Actions**, select **Publish Group C website** and choose **Run workflow**. The first push-triggered deployment failed because GitHub Pages was not yet enabled; rerun after switching on Pages.
4. Wait for a successful deployment; use the **Visit site** link in GitHub Pages settings. Copy the **actual** confirmed URL to README, not an imagined link.
5. Test the homepage and every internal anchor. Confirm `styles.css`, `data-view.js`, `motion.js`, `results.js`, and `img/dajti-concept.webp` load without 404 errors, and that the mobile menu and download panel work.
6. If any values appear, compare them to verified `processed/period_rates.csv`, `processed/rate_difference.csv`, `processed/permutation_summary.csv`, and `processed/question_two_changes.csv`.

The workflow in `.github/workflows/pages.yml` publishes `site/` on relevant `main` changes or when manually dispatched, **but requires Pages enabled under Settings first**. Publishing the website scaffold does not certify any climate findings; all results remain pending until verified source data is available.

## Scientific screenshots

Recommended final README images (take them *after* verified data is loaded): `docs/media/hero.png`, `docs/media/observed_rates.png`, `docs/media/permutation_histogram.png`, `docs/media/mean_vs_p95.png`, `docs/media/mobile.png`. Do not use the concept drawing or synthetic fixtures as evidence of climate findings.
