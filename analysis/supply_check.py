#!/usr/bin/env python3
"""Future oil supply: production, drilling, drilled-uncompleted wells (DUCs), and the SPR.

Rig count leads oil output by years (Bill James, 2021). DUCs are wells already drilled but not
yet completed; drawing them down lets output rise while drilling falls, delaying the rig-count
signal. The Strategic Petroleum Reserve (SPR) is the national buffer against supply shocks.

Run:  python3 supply_check.py [--refresh]
"""
import argparse
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from disposable_energy import OUT, RAW, fetch, fred

EIA = {
    "spr": ("eia_WCSSTUS1w.xls", "https://www.eia.gov/dnav/pet/hist_xls/WCSSTUS1w.xls"),
    "production": ("eia_WCRFPUS2w.xls", "https://www.eia.gov/dnav/pet/hist_xls/WCRFPUS2w.xls"),
    "distillate": ("eia_WDISTUS1w.xls", "https://www.eia.gov/dnav/pet/hist_xls/WDISTUS1w.xls"),
    "distillate_supplied": ("eia_WDIUPUS2w.xls", "https://www.eia.gov/dnav/pet/hist_xls/WDIUPUS2w.xls"),
    "duc": ("eia_duc-data.xlsx", "https://www.eia.gov/petroleum/drilling/xls/duc-data.xlsx"),
}
START = "2007-01-01"
# Rule of thumb (Bill James): 19-20 days of distillate supply are needed just to fill the supply chain.
OPERATING_FLOOR_DAYS = (19, 20)


def eia_weekly(key, refresh):
    name, url = EIA[key]
    path = fetch(name.rsplit(".", 1)[0], url, refresh) if refresh else RAW / name
    if refresh:
        path.rename(RAW / name)
        path = RAW / name
    d = pd.read_excel(path, sheet_name="Data 1", skiprows=2, engine="xlrd")
    d.columns = ["date", "v"]
    return d.dropna().set_index("date")["v"].astype(float)


def eia_duc(refresh):
    name, url = EIA["duc"]
    path = RAW / name
    if refresh:
        fetch(name.rsplit(".", 1)[0], url, refresh).rename(path)
    d = pd.read_excel(path, sheet_name="Data", header=None)
    t = d.iloc[4:, [0, 29, 30, 31]]
    t.columns = ["month", "drilled", "completed", "duc"]
    t = t[pd.to_datetime(t["month"], errors="coerce").notna()].copy()
    t["month"] = pd.to_datetime(t["month"])
    return t.set_index("month").apply(pd.to_numeric, errors="coerce")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()

    spr = eia_weekly("spr", args.refresh) / 1e3            # million barrels
    prod = eia_weekly("production", args.refresh) / 1e3    # million barrels/day
    duc = eia_duc(args.refresh)
    drill = fred("IPN213111N", args.refresh)               # drilling oil & gas wells, 2017 = 100
    diesel = fred("GASDESW", args.refresh)
    dist = eia_weekly("distillate", args.refresh) / 1e3                 # million barrels
    dist_use = eia_weekly("distillate_supplied", args.refresh) / 1e3     # million barrels/day
    dist_days = (dist / dist_use.rolling(4).mean()).dropna()            # reported days of supply

    def same_week_rank(s):
        """Each year's last reading in the latest week's month on/after its day; sorted low to high."""
        last = s.index[-1]
        w = s[(s.index.month == last.month) & (s.index.day >= last.day - 6)]
        return w.groupby(w.index.year).last().sort_values()

    spr_low_before = spr[(spr <= spr.iloc[-1]) & (spr.index < "2026-01-01")]
    result = {
        "spr_million_bbl": {"latest": {"date": str(spr.index[-1].date()), "value": round(spr.iloc[-1], 1)},
                            "peak": {"date": str(spr.idxmax().date()), "value": round(spr.max(), 1)},
                            "last_this_low_before_2026": str(spr_low_before.index[-1].date()),
                            "change_in_2026": round(spr.iloc[-1] - spr["2026-01-01":].iloc[0], 1)},
        "production_mb_d": {"latest": {"date": str(prod.index[-1].date()), "value": round(prod.iloc[-1], 2)},
                            "record": {"date": str(prod.idxmax().date()), "value": round(prod.max(), 2)}},
        "drilling_index_2017_100": {str(k.date()): round(float(drill[k]), 1) for k in pd.to_datetime(
            ["2014-10-01", "2019-01-01", "2020-08-01", "2022-12-01", "2025-12-01"]).append(drill.index[-1:])},
        "duc_wells_eia_dpr_regions": {"peak": {"date": str(duc["duc"].idxmax().date()), "value": int(duc["duc"].max())},
                                      "latest_published": {"date": str(duc.index[-1].date()),
                                                           "value": int(duc["duc"].iloc[-1])},
                                      "note": "EIA stopped publishing the DUC series after April 2024"},
    }
    rank_st, rank_days = same_week_rank(dist), same_week_rank(dist_days)
    result["distillate_reported"] = {
        "stocks_million_bbl": {"date": str(dist.index[-1].date()), "value": round(dist.iloc[-1], 1),
                               "lowest_for_this_week_since": int(dist.index[0].year) if rank_st.index[0] == dist.index[-1].year else None,
                               "lowest_5_this_week": {str(k): round(v, 1) for k, v in rank_st.head(5).items()}},
        "days_of_supply": {"value": round(dist_days.iloc[-1], 1),
                           "lowest_5_this_week_since_1991": {str(k): round(v, 1) for k, v in rank_days.head(5).items()}},
        "usable_cushion_days_rule_of_thumb": {
            "floor_days": list(OPERATING_FLOOR_DAYS),
            "cushion_days": [round(dist_days.iloc[-1] - OPERATING_FLOOR_DAYS[1], 1),
                             round(dist_days.iloc[-1] - OPERATING_FLOOR_DAYS[0], 1)],
            "share_of_365_day_cycle_pct": [round((dist_days.iloc[-1] - f) / 365 * 100, 1)
                                           for f in OPERATING_FLOOR_DAYS[::-1]]},
        "note": ("Reported stocks include pipeline fill and minimum operating inventory that cannot be "
                 "withdrawn; usable inventory = reported - operational floor (floor not published)."),
    }
    (OUT / "supply_check.json").write_text(json.dumps(result, indent=2))

    fig, axes = plt.subplots(5, 1, figsize=(11, 13), sharex=True)
    panels = [
        (prod[START:], "#1e293b", "US crude production\nmillion bbl/day"),
        (drill[START:], "#b45309", "Drilling activity\n(index, 2017 = 100)"),
        (duc["duc"], "#7c3aed", "Drilled uncompleted\nwells (DUCs)"),
        (spr[START:], "#15803d", "Strategic Petroleum\nReserve, million bbl"),
        (dist_days[START:], "#0f766e", "Distillate stocks,\ndays of supply (reported)"),
    ]
    for ax, (series, color, label) in zip(axes, panels):
        ax.plot(series.index, series.values, color=color, lw=2)
        ax.set_ylabel(label, fontsize=9)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    d2 = axes[0].twinx()
    d2.plot(diesel[START:].index, diesel[START:].values, color="#9b1c1c", lw=1, alpha=0.7)
    d2.set_ylabel("diesel $/gal", color="#9b1c1c", fontsize=9)
    axes[2].text(duc.index[-1], duc["duc"].iloc[-1], "  EIA series ends Apr 2024", fontsize=8, va="center")
    axes[0].set_title("Future oil supply: production at record, drilling flat, DUCs drawn down, SPR at a 1982 low, diesel stocks thin")
    fig.tight_layout()
    fig.savefig(OUT / "oil_supply.png", dpi=150)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
