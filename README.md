# Disposable Energy

[DisposableEnergy.com](https://www.disposableenergy.com) — how much energy people can buy with
their take-home pay. A living, open metric of the input to the economic flywheel (Bill James).

```
take-home pay  = average weekly earnings × (1 − income and payroll tax rate)
gallons(month) = take-home pay / retail gasoline price      ← actual dollars; no inflation index
DE(month)      = gallons(month) / gallons(1986) − 1          (1986 = 0)
```

- `index.html`, `style.css` — the site. Static; reads `analysis/output/current.json` for the latest month.
- `analysis/` — method, data, code, results, and open questions for reviewers. Start with
  [analysis/README.md](analysis/README.md).
- `.github/workflows/monthly.yml` — re-downloads the data and recomputes on the 12th of each month.

Open for review. Check it, break it, improve it: Bill James, bill.james@jpods.com
