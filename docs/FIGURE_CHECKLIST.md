# Figure sign-off checklist (teammate review)

- [ ] Original source JSON and HTML files are cached, hash-verified, and named with collection dates.
- [ ] Counts and valid-day denominators on website match `processed/period_rates.csv` (including missing days).
- [ ] Hot threshold is **> 35 °C**, never **>= 35 °C**; months are exactly 6, 7, 8.
- [ ] Period A is 1961–1990 and B is 1991–2020; each summer year appears as a block even if incomplete.
- [ ] Website percentage-point labels match `processed/rate_difference.csv`; not mislabeled relative percent.
- [ ] Rate chart is a **dot and 95% bootstrap-range** chart; label rate scale.
- [ ] Permutation histogram uses shuffled whole-year labels with a real observed difference marker; includes 10k draws and fixed seed.
- [ ] Permutation extreme fraction is a shuffle-tail statistic, **not** a climate confidence interval.
- [ ] Mean vs P95 chart uses °C changes (late minus early), each with a 95% bootstrap range and zero marker.
- [ ] Every yes/no claim follows whether corresponding interval excludes zero; absence of evidence ≠ evidence of no change.
- [ ] Colored annual stripes are not published without a fully specified baseline, annual coverage policy, validated values and legend; otherwise neutral.
- [ ] Wikipedia sanity check matches metric, years and month; otherwise withheld and explained.
- [ ] Hero is labelled **illustrative** and is never presented as literal temperature measurement.
- [ ] Captions, source links, accessibility labels and mobile display reviewed by another teammate.
- [ ] Final screenshot and verified offline notebook included in reviewed PR.
