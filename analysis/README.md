# Disposable Energy — Open for Review

**Disposable Energy** (Bill James): how much energy people can buy with their take-home pay.
GDP measures the speed of the economic flywheel. Disposable Energy tries to measure the
*input* to it — labor applying affordable energy — which shows up in outcomes only after a
time delay.

This folder is a first, reproducible attempt to test the idea against public data. **It is
not finished science.** Both the concept of Disposable Energy and the correlation of oil
imports and oil wars with national debt need review. We invite economists, energy
researchers, and students to check the method, break it, and improve it.

Contact: Bill James, bill.james@jpods.com · Live: [DisposableEnergy.com](https://www.disposableenergy.com)

**Current:** [Record Diesel, Disposable Energy, and Unemployment — October 2026](DIESEL-2026.md)

## Run it

```bash
pip install -r requirements.txt
python3 disposable_energy.py            # uses cached data in data/raw/
python3 disposable_energy.py --refresh  # re-downloads from FRED and EIA
```

Outputs go to `output/`: `current.json` (the latest month, read by the website), `results.json` (all numbers), `disposable_energy_annual.csv`, `disposable_energy_monthly.csv`, and charts. A GitHub Action re-runs everything with `--refresh` on the 12th of each month.

## Method

```
gallons(y) = income(y) / retail gasoline price(y)     ← actual dollars, same period; no inflation index
DE(y)      = gallons(y) / gallons(1986) - 1          (1986 = 0)
```

| Variant | Income | Why |
|---|---|---|
| **`take_home`** | BLS average weekly earnings, production and nonsupervisory workers (`CES0500000030`), × (1 − average rate of personal income tax and employee payroll tax: `W055RC1`, `PI`, `B228RC1A027NBEA`) | **Headline.** Take-home pay from work. 1964+ |
| `wages` | The same weekly earnings, before tax | Shows what taxes do to the measure |
| `original` | Aggregate disposable personal income (FRED `A067RC1A027NBEA`) | Reproduces Bill's 2022 workbook and 2023 chart |
| `per_capita` | Disposable personal income per person (`A229RC0A052NBEA`) | "People can buy" — removes population growth |
| `ex_transfers` | Per person, minus personal current transfer receipts (`PCTR`) | Removes stimulus checks, so money printing is not counted as income |

Gasoline: EIA Monthly Energy Review Table 9.4, leaded regular through 1975, unleaded regular from
1976 (the two differ by about 4% in 1976).

## First results (annual data through 2025; monthly through August 2026)

**Disposable Energy, 1986 = 0**

| | 1973 | 1980 | 1998 | 2008 | 2012 | 2020 | 2022 | 2025 |
|---|---|---|---|---|---|---|---|---|
| **take-home pay** | +0.19 | −0.43 | +0.24 | **−0.45** | **−0.44** | +0.16 | −0.34 | −0.04 |
| per capita income | −0.17 | −0.52 | +0.52 | −0.26 | −0.27 | +0.63 | −0.06 | +0.40 |

A week's take-home pay bought more gasoline in 1973 than in any year since 2000 except 2020.
Per-capita income tells a rosier story because it includes government transfers, interest, and
dividends; the aggregate (`original`) series is rosier still because it counts population growth.

**Test 1 — Gasoline price leads unemployment (monthly, 1977–2019).** The 12-month change in
gasoline price correlates most strongly with the 12-month change in unemployment **18 months
later** (r = 0.33, n = 498). Every lag from **16 to 24 months** has r ≥ 0.30 — the response is
spread across that window, matching Bill's 2022 chart, *"Less affordable energy correlates with
rising unemployment in 12–24 months"* (JPods, EIA and BLS data), and the 18-month lag he reported
in 2008. Using the inflation-adjusted gasoline price (÷ CPI) gives the same shape, strongest at
19 months (r = 0.29).

Out of sample: gasoline peaked in mid-2022. Unemployment bottomed at 3.4% in April 2023 and rose
to 4.2% by July 2024 — about two years later, a modest rise.

**Test 2 — Change in Disposable Energy leads real GDP growth (annual).** Strongest at a
**1-year lead** for all five variants; take-home pay is strongest
(r = 0.44, 1961–2007; r = 0.34, 1961–2019).

**Test 3 — Flywheel time constant.** Treating momentum as an exponentially weighted sum of
Disposable Energy changes, the best-fitting time constant is about **2–3 years** before 2008 and
**7–15 years** when 2008–2025 is included (take-home pay: 3 and 15). The flywheel appears to have slowed — or money
printing after 2008 and COVID changed the relationship. That is an open question.

## Open questions for reviewers

1. **Energy scope.** Gasoline is one energy carrier. Should Disposable Energy include
   electricity, heating fuel, diesel, and food energy — weighted by household budget shares?
2. **Take-home pay.** `take_home` applies the economy-wide average tax rate (income tax plus
   employee payroll tax) to production workers, whose income-tax rate is lower than average.
   A worker-level calculation (e.g. NBER TAXSIM for a representative worker each year) would
   be more exact.
3. **Money printing.** Government money printing changed radically in 2008 and with COVID.
   How should Federal Reserve balance-sheet expansion and Federal borrowing enter the model —
   as a separate input that adds near-term growth and longer-term drag?
4. **Oil imports and debt after 2005.** Federal debt tracked oil imports from 1970 to about
   2005, then separated as imports fell. Candidate explanations — net energy decline of
   fracked oil, private credit expansion (2001–07), the crisis transfer of private debt to the
   Federal balance sheet (2008–09), Fed money printing and near-zero interest (2008–22) — are
   not yet tested here. Total debt of all sectors may be the better measure.
5. **Prior work.** How does Disposable Energy relate to energy-affordability indices, EROI /
   net-energy research, and models where useful work (exergy) explains growth? Where is it
   new?
6. **Statistics.** Annual data give about 60 points per test; correlations around 0.3 are
   modest. Monthly and regional data (the economy is a confederation of upside-down pyramids,
   not one national average) would sharpen the signal.

## Files

| File | |
|---|---|
| `disposable_energy.py` | The whole analysis |
| `data/raw/` | Cached source data exactly as downloaded |
| `output/results.json` | Every number, every lag, every variant |
| `output/*.png` | Charts |
