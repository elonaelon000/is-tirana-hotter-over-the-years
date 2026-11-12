# Design notes — Tirana / Dajti cinematic editorial

## Visual direction

A scientific story introduced through the place being studied. The first screen pairs a dark-navy research masthead with a cinematic **illustrative composition of Tirana and Mount Dajti**, then shifts to a bright, accessible research journal for the actual statistics. Scarlet marks heat-themed emphasis; cool teal supports navigation and measurement details. The hero illustration and its scroll haze are **not** evidence of warming.

The Dajti background is cropped from an earlier AI-generated design-concept image supplied in this conversation. It is not a site photograph, map, forecast, or source of observations. Baked-in mockup labels and year-strip artifacts have been removed in the reviewed asset.

## Navigation and sections

1. Mountain hero and explicit research status
2. Predeclared question: JJA, >35°C, two 30-year periods
3. Annual stripe visual index, neutral until year-specific verified values exist
4. Question 1: rates, 95% ranges, null permutation histogram
5. Question 2: mean and 95th-percentile shifts with 95% ranges
6. Methods, reproducibility commands, source credits
7. Original project schedule and figure-reading guide
8. Study limitations, inconclusive verdict as an acceptable result
9. **Additional local `science.html`**: a human-readable guide to the dataset, JSON→Pandas cleaning, year-block statistics, individual figures and independent verification

## Preservation rules

- No changes to the source collection, calculations or notebook.
- `results.js`, `data-view.js` and `data_contract.csv` are unchanged from the supplied site.
- Original result element IDs and chart selectors remain in place.
- No statistic, verdict, map color or annual stripe is displayed unless it comes from the validated exporter.
- The years in the hero are an **illustrative timeline**, not measured temperature values.

## Interaction and accessibility

- Subtle scroll-linked hero haze and archive year; decorative only, not linked to weather data.
- Tap, hover and keyboard access to annual stripe positions; aria-valuetext explains whether actual values exist.
- Download dialog presents the contract; analyzed results become available only after verified export.
- Mobile menu, 44px-or-larger primary controls, reduced-motion support, system font fallbacks.
- Standalone method guide works with no external scripts and is bundled for offline inspection.

## Asset and provenance

`img/dajti-concept.webp` is an edited **illustrative design asset**; no external image provider or data source is required to render the site. It must not be captioned as a 1940, 2020, or 2026 climate photograph. If the team chooses a real photographer's image instead, replace the file only after confirming rights and adding an appropriate attribution line.
