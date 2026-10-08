# Third-Party Notices

## Software (analysis/)

| Library | Version | License | Purpose |
|---|---|---|---|
| pandas | 3.0.3 | BSD-3-Clause | Time-series assembly and correlation |
| NumPy | 2.5.0 | BSD-3-Clause | Numerics (pandas dependency) |
| Matplotlib | 3.11.0 | Matplotlib License (PSF-style, BSD-compatible) | Charts |
| xlrd | 2.0.1 | BSD-3-Clause | Reading EIA .xls history files |
| openpyxl | 3.1.5 | MIT | Reading the EIA DUC .xlsx file |

GitHub Actions used by `.github/workflows/monthly.yml`: `actions/checkout`, `actions/setup-python` (MIT).

## Data (analysis/data/raw/)

| Source | Series | Terms |
|---|---|---|
| Federal Reserve Bank of St. Louis, FRED | CES0500000030, W055RC1, PI, B228RC1A027NBEA, A067RC1A027NBEA, A229RC0A052NBEA, B230RC0A052NBEA, PCTR, APU000074714, UNRATE, GDPC1, GFDEBTN, WALCL, CPIAUCSL, GASDESW, GASREGW, A229RC0, IPN213111N | Underlying data from BLS, BEA, Treasury, and the Federal Reserve — US government works, public domain |
| US Energy Information Administration | Monthly Energy Review Table 9.4; weekly SPR stocks (WCSSTUS1), crude production (WCRFPUS2), distillate stocks (WDISTUS1) and distillate product supplied (WDIUPUS2); DUC data (Drilling Productivity Report) | US government work, public domain |

## License compatibility

All libraries are permissive (BSD/MIT-style); no GPL or LGPL components.
