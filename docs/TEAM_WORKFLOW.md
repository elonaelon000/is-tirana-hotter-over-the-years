# Three real contributors — branch, pull request and review workflow

**Do not create commits with invented names or claim somebody completed work they have not done.** GitHub's contribution history should reflect the people who actually wrote, checked and committed each part.

## Work allocation (fill real names/GitHub usernames before invites)

| Owner | Role | Tasks to finish themselves | Evidence to attach to PR |
|---|---|---|---|
| **[NAME 1 / @handle]** | Collector and data-quality owner | Confirm contact-bearing User-Agent and access-check logs. Run the ONE full archive collection when authorized; commit `raw/` dated files and manifest; verify timezone, units, dates, nulls and coverage. Verify real missingness table. Review Q2 mean-vs-tail interpretation in presentation. | API URL, fetch date, SHA-256, counts of missing dates vs null maxima, successful reproduction commands |
| **[NAME 2 / @handle]** | Data contract and Wikipedia owner | Review types/units/known gaps in `data_contract.csv`. Read cached Wikipedia climate table (not manually transcribed numbers), confirm climate normal years and metric from cited caption, document any station mismatch; produce `wiki_period_confirmation.json` only with evidence; make sanity chart/check if justified. Present framing/prediction/data contract. | Table/source link, normal-year quote from cached page, clean `wiki_normals.csv`, join by **month after same-year aggregation**, contract changes |
| **[NAME 3 / @handle]** | Statistics and figures owner | Run/inspect full notebook offline on genuine cache. Audit base rates, year-block resampling and permutation null for 10k draws; check bootstrap tails, figure text and zero-crossing conclusions. Export website result object when real data is ready; verify figure captions and live demo; present Q1. | Notebook Run All log, counted rates and denominators with ranges, 10k seed checks, permutation screenshot, P95/mean chart screenshot |

**Front-end and documentation integration** may be maintained by the person preparing the website and README, but this does **not** replace the three tasks above. Agree who owns the final integration PR and credits before publishing.

## Branch procedure

```sh
git clone https://github.com/elonaelon000/is-tirana-hotter-over-the-years.git
cd is-tirana-hotter-over-the-years
git switch -c data/source-cache     # NAME 1
# or: git switch -c docs/wiki-contract  # NAME 2
# or: git switch -c analysis/validation  # NAME 3
# edit only your work and test locally
git status
git add <your-reviewed-files>
git commit -m "Document verified [specific task]"
git push -u origin <branch-name>
```

Open a pull request **from each person's actual GitHub account**. Request a review by someone else. Use at least one clear commit per meaningful stage, not fake activity/no-op commits. Merge after checks and verified evidence. GitHub counts authenticated commits using configured author email; check `git config user.email` before committing.

## Suggested work boundaries

- `main`: reproducible code + website scaffold + honest pending states.
- `data/source-cache`: the actual source cache, manifest, coverage audit.
- `docs/wiki-contract`: verified climate-normal source notes + monthly join/documentation.
- `analysis/validation`: notebook review, real computed tables and figures, verified web export.
- Optional later `site/polish`: README/screenshot/live site changes with credit to actual editor.

## Shared final definition of done

- All three PRs linked in `docs/PROGRESS_LOG.md`; no contribution is credited without the person's real work.
- `README.md` names the actual authors and specifically states which files or analysis each edited.
- README states observed results **with their ranges** only after verification. No guessed p-values or charts.
- Notebook runs top-to-bottom offline. Cache manifest hashes match. No direct API requests in notebook or site.
- 6-minute talk identifies the method, assumptions and limitations, not a premature yes/no.
- GitHub Pages **published only after** the team approves and checks rendered results.
