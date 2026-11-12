# Sunday 15 November: independent offline proof

- [ ] Person who **did not implement the notebook** checks out the committed project from Git. Confirm `raw/` contains the original JSON and HTML responses, plus `raw/manifest.json`.
- [ ] Confirm Monday's `processed/access_check_report.json`, Tuesday's `processed/collection_report.json`, the sealed prediction and real User-Agent are committed.
- [ ] Install dependencies **before disconnecting**: `python -m pip install -r requirements.txt` and ensure the `python3` Jupyter kernel exists.
- [ ] **Turn Wi-Fi/network off** at the operating-system level (not only `OFFLINE=1`). Restart Jupyter kernel, clear outputs and use **Restart & Run All** on `notebooks/01_how_sure_are_you.ipynb`.
- [ ] Or run `OFFLINE=1 python scripts/offline_check.py` while the network is physically off; this validates SHA-256 hashes and runs every cell, writing `outputs/verified_offline_run.ipynb`.
- [ ] Check all cells complete without error; the notebook never calls a URL. Confirm period-rate, permutation and mean-vs-tail plots are generated from the cached response.
- [ ] Check 1991–2020 coverage flag and missing-day totals; check the Wikipedia years are explicitly verified **or** the sanity comparison says **withheld**.
- [ ] Confirm the data contract lists all exported fields, units, provenance and gaps; never hide missing values.
- [ ] Open the generated CSVs and charts; make sure slide placeholders are replaced only by actual calculated estimates and intervals.
- [ ] Save a screenshot or copy of the executed notebook and record the verifier's name, date, OS/kernel and `git rev-parse HEAD` in the team log. Commit evidence and final materials.

**Pass criterion:** the entire notebook runs without network access or fetch code, using only committed raw files. If not, stop and fix before presentation; do not claim the offline test passed.
