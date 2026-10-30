# Customer retention & revenue | portfolio case study

Explore the [live interactive demo](https://hmantovani.github.io/customer-retention-analysis/) or open [index.html](index.html) locally or [report.html](report.html) for the decision brief. This is an analysis of real historical transactions, not synthetic data. The audience is sales and finance: the aim is to identify questions for investigation and experiments, not estimate causal effects or predict churn.

## Data choice and provenance

Chen, D. (2015), [Online Retail](https://doi.org/10.24432/C5BW33), UCI Machine Learning Repository, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The source describes invoice lines for a UK-based online retailer, 1 December 2010–9 December 2011; many customers are wholesalers. Source file: https://archive.ics.uci.edu/static/public/352/online+retail.zip. The analysis transforms the source into customer/invoice orders and monthly aggregates. `output/summary.json` records the source workbook SHA-256.

We considered UCI Online Retail II, with two years of history, and synthetic transactions. Online Retail II offers longer follow-up, while this smaller, directly downloadable source is manageable and still permits 90-day follow-up and complete-month cohorts. Synthetic data would give precise control over edge cases but fabricated patterns would not support real-world observations. Synthetic examples are used only in tests. Neither dataset makes a customer's true acquisition date observable; the study is historical and not representative of current retail generally.

## Definitions and scope

- Window: 2010-12-01 through 2011-11-30 inclusive; December 2011 is partial and excluded. Source dates are treated as recorded, without a timezone conversion.
- A purchase order is a distinct identified customer and invoice with at least one positive-quantity, positive-price line on a non-`C` invoice. Invoice date is the earliest qualifying line timestamp; same-time invoices are ordered by invoice ID. Free/zero-price lines, negative non-cancellation adjustments and anonymous lines do not count as purchases or gross value. No deduplication is attempted: duplicate lines may be legitimate and can inflate value.
- One-time share is customers with exactly one observed order divided by all observed purchasers. It is not lifetime one-time share. The first observed purchase may be a repeat of an earlier purchase, and customers may buy after the window.
- 90-day repeat is customers with a second order within 90 elapsed days of first observed order divided by customers whose first order is at least 90 days before the exclusive cutoff. The boundary is inclusive. The conditional median time to second order excludes customers without an observed second order and is not a survival estimate.
- Cohort activity is distinct purchasers active in calendar month M0, M1, etc., divided by first-observed-month cohort size. It does not require consecutive purchases. Future or incomplete months are masked; zero observed activity in a mature month is zero. Left censoring affects every cohort, especially the first.
- Monthly active customers are distinct purchasers in a complete month. Activity is not a churn classification.
- Concentration ranks identified purchasers by positive purchase-line value plus negative quantity cancellation (`C`) lines with positive unit price for that customer within the window. The top ceiling(10% of purchasers) share uses the sum of purchaser net values as denominator. Refunds are not matched to original orders, can relate to earlier purchases, and may arrive after the cutoff. Refund-only customers and anonymous transactions are excluded from this share; cancellation totals and exclusions are disclosed in the report. This is transaction value, not profit or recognized accounting revenue.

## Reproduce

Requires Python 3.10+ and the pinned packages. From this folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
New-Item -ItemType Directory -Force data | Out-Null
Invoke-WebRequest 'https://archive.ics.uci.edu/static/public/352/online+retail.zip' -OutFile data/source.zip
Expand-Archive data/source.zip -DestinationPath data -Force
python src/analyze.py
python src/build_demo.py
python -m unittest discover -s tests -v
```

The pipeline creates `report.html`, `output/summary.json`, monthly/cohort CSVs and `output/analysis.sqlite`; `sql/metrics.sql` contains executable SQLite checks. The source file and database are local generated artifacts. Excel parsing can take a few minutes. Calculations have no network dependency after download.

## Acceptance and validation

The report must include repeat purchase, cohort activity, time to second order, revenue concentration and monthly activity, plus business questions and caveats. One-time buyers, missing histories, refunds and cohort maturity must remain explicit. A deterministic fixture tests order sequencing, anonymous records, refund exclusion, cutoff and immature cohort masking; SQL checks the 90-day and monthly aggregates independently. Source values are historical observations and should not be presented as causal effects. The data lack margin, marketing exposure and identifiers for anonymous shoppers.

## Interactive demo and GitHub Pages

The demo is a static, self-contained `index.html`: it embeds aggregates from `output/summary.json`, `output/monthly.csv`, `output/cohorts.csv`, and the locally generated SQLite orders table. `python src/build_demo.py` regenerates it after `python src/analyze.py`. Cohort sizes and the order-count distribution are aggregated from the same orders table; no individual customer records are embedded. Both pages work locally without a server. The data are a fixed historical snapshot and do not update automatically.

To publish, commit and push `index.html`, `report.html`, the source files and aggregate outputs to the repository. In GitHub repository **Settings → Pages**, select **Deploy from a branch**, choose `main` and `/ (root)`, and save. GitHub will provide the Pages URL once built. This project is not currently configured for automatic data refresh. Re-run both scripts and commit the resulting files to change the published snapshot. The project-hub `.project/` records, source download, and local SQLite database should remain excluded from the remote repository.
