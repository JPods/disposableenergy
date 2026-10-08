#!/usr/bin/env python3
"""Current diesel shock: price record, Disposable Energy now, and the unemployment lag window.

Companion to disposable_energy.py (run that first; this reads its annual output for the 1986 base).
Run:  python3 diesel_check.py [--refresh]
"""
import argparse
import json

import pandas as pd

from disposable_energy import OUT, fred, lag_corr

SERIES = {
    "diesel": "GASDESW",      # US No 2 diesel retail, $/gal, weekly (1994+)
    "gas": "GASREGW",         # US regular gasoline retail, $/gal, weekly (1990+)
    "income_pc": "A229RC0",   # Disposable personal income per capita, $ SAAR, monthly
    "unrate": "UNRATE",
    "cpi": "CPIAUCSL",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()
    s = {k: fred(v, args.refresh) for k, v in SERIES.items()}

    dw = s["diesel"].dropna()
    dm = dw.resample("MS").mean()
    gm = s["gas"].resample("MS").mean()
    cpi = s["cpi"].dropna()
    to_today = lambda when: round(float(dm[when] * cpi.iloc[-1] / cpi[when]), 2)

    ann = pd.read_csv(OUT / "disposable_energy_annual.csv", index_col=0)
    base = ann.loc[1986, "dpi_pc"] / ann.loc[1986, "gas_price"]
    de = (s["income_pc"] / gm.reindex(s["income_pc"].index) / base - 1).dropna()

    x = dm.pct_change(12) * 100
    y = s["unrate"].diff(12)
    m = pd.concat([x, y], axis=1, sort=True).dropna()
    m = m[m.index.year < 2020]
    rows, best = lag_corr(m.iloc[:, 0], m.iloc[:, 1], 36)

    # last complete month: drop the current month if the latest week is early in it
    yoy_month = dm.index[-2] if dw.index[-1].day < 22 else dm.index[-1]
    result = {
        "diesel_latest_week": {"date": str(dw.index[-1].date()), "usd": float(dw.iloc[-1])},
        "diesel_record_week": {"date": str(dw.idxmax().date()), "usd": float(dw.max())},
        "prior_record_week": {"date": str(dw[dw.index < "2026-01-01"].idxmax().date()),
                              "usd": float(dw[dw.index < "2026-01-01"].max())},
        "in_todays_dollars_cpi_through": str(cpi.index[-1].date()),
        "monthly_peaks_in_todays_dollars": {"2008-06": to_today("2008-06-01"),
                                            "2022-06": to_today("2022-06-01")},
        "diesel_12_month_change_pct": {str(yoy_month.date()): round(float(x[yoy_month]), 1)},
        "gasoline_12_month_change_pct": {str(yoy_month.date()):
                                         round(float((gm[yoy_month] / gm[yoy_month - pd.DateOffset(years=1)] - 1) * 100), 1)},
        "DE_per_capita_monthly_1986_0": {str(k.date()): round(float(v), 3) for k, v in de.tail(14).items()},
        "diesel_leads_unemployment_1995_2019": {"best": best, "r_at_12": rows[12]["r"], "r_at_24": rows[24]["r"]},
        "unemployment_latest": {"date": str(s["unrate"].dropna().index[-1].date()),
                                "pct": float(s["unrate"].dropna().iloc[-1])},
    }
    (OUT / "diesel_check.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
