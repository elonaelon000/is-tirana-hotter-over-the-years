# Review package and current publishing status

Originally prepared for inspection only; the user later explicitly requested publication to GitHub. The project source and mountain-view website have now been committed to `main`. **GitHub Pages is not yet enabled**, so there is no verified public live-site URL; raw climate data and final conclusions are still pending.

## Preview

- Open `site/index.html` to see the Mount Dajti cinematic hero and data-story structure.
- Open `site/science.html` for the visitor-friendly explanation of every dataset transformation, statistical method and chart.
- Compare the desktop and 375px mobile PNG previews included alongside the ZIP.

## What was changed locally

- Mountain hero uses an edited illustrative scene (AI-generated concept, **not documentary photography**); the old baked-in text has been removed.
- Website styling and presentation-only motion maintain a truthful pending-result state.
- New local science guide replaces a link to an as-yet-unpublished GitHub Markdown file, avoiding a broken public link.
- README/design notes updated to accurately describe the current site and approval workflow.

## What is untouched

- No changes to source API requests, Python statistics, notebook methods, raw-data checks, result schema, `site/results.js`, `site/data-view.js` or the original data contract.
- No synthetic climate results or unverified hot/cool annual colors were introduced.

## Before any approval to publish

- [ ] Review the homepage and science guide on your own device.
- [ ] Confirm the exact sealed prediction, contact-bearing User-Agent, contributor names and actual completed tasks.
- [ ] Collect sources; verify raw manifest hashes, coverage and Wikipedia's normal years.
- [ ] Independent teammate runs notebook top to bottom **offline** and checks every figure.
- [ ] Fill README with actual measured values and ranges from verified outputs; don't claim a warming verdict prematurely.
- [ ] Review teammates' genuine separate PRs under their own GitHub accounts.
- [ ] Enable GitHub Pages from Settings → Pages → GitHub Actions and rerun the `Publish Group C website` workflow. Verify the live link.

## Existing GitHub state

A separate earlier step created an initial README commit and three task Issues in the user's public repository. This review package did **not** change those. The user should separately approve any decision to keep, edit, close or revert them.
