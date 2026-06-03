"""
ESG Data Loader — reads from the SAME master CSV as the Streamlit app.
All paths resolve relative to the python-service root so both apps share
the same data files on disk.
"""
import os, json, glob, csv
from pathlib import Path
from datetime import datetime

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE     = Path(__file__).resolve().parent.parent  # python-service/
_DATA_DIR = _HERE.parent / "data_storage"           # esg-v2/data_storage/
_MASTER_GLOB = str(_DATA_DIR / "master" / "ESG_MASTER_WIDE_ALL_COMPANIES_*.csv")
_VERIF_CSV   = _DATA_DIR / "verifications.csv"

# Hard-coded demo companies (10 TIP members)
_COMPANIES = [
    {"id": "verdatyres",   "name": "VerdaTyres Corp",  "email": "verdatyres@tip-reporting.com",  "role": "client"},
    {"id": "alphatread",   "name": "AlphaTread Ltd",   "email": "alphatread@tip-reporting.com",  "role": "client"},
    {"id": "betarubber",   "name": "BetaRubber Inc",   "email": "betarubber@tip-reporting.com",  "role": "client"},
    {"id": "gammatire",    "name": "GammaTire SA",     "email": "gammatire@tip-reporting.com",   "role": "client"},
    {"id": "deltagrip",    "name": "DeltaGrip GmbH",  "email": "deltagrip@tip-reporting.com",   "role": "client"},
    {"id": "epsilonwheel", "name": "EpsilonWheel Co",  "email": "epsilonwheel@tip-reporting.com","role": "client"},
    {"id": "zetatrac",     "name": "ZetaTrac LLC",     "email": "zetatrac@tip-reporting.com",    "role": "client"},
    {"id": "etaroad",      "name": "EtaRoad AG",       "email": "etaroad@tip-reporting.com",     "role": "client"},
    {"id": "thetadrive",   "name": "ThetaDrive NV",    "email": "thetadrive@tip-reporting.com",  "role": "client"},
    {"id": "iotawheel",    "name": "IotaTire PLC",     "email": "iotawheel@tip-reporting.com",   "role": "client"},
    {"id": "dss_analyst",  "name": "dss+ Analyst",     "email": "employee@consultdss.com",       "role": "dss"},
]

# ── Column aliases — maps CSV column names to canonical field names ────────────
_COL_MAP = {
    "Production":                          "production",
    "Water withdrawals (m3)":              "water_withdrawals",
    "Renewable electricity purchased (GJ)":"renew_elec_purchased",
    "Non-renewable electricity purchased": "nonrenew_elec_purchased",
    "Self-generated renewable electricity":"self_gen_elec",
    "Purchased Steam (GJ)":               "purchased_steam",
    "Sold Electricity (GJ)":              "sold_electricity",
    "Natural Gas (GJ LHV)":              "nat_gas",
    "Coal (GJ LHV)":                     "coal_sub",
    "Diesel (GJ LHV)":                   "diesel",
    "Biomass (GJ LHV)":                  "biomass",
    "Total no. of sites":                 "total_sites",
    "ISO 14001 certified sites":          "iso_sites",
    "Total amount of waste (T)":          "waste_total",
    "Amount of waste sent to recovery (T)":"waste_recovery",
    "CO2 Scope 2 Steam (T.CO2)":         "co2_scope2_steam",
    # Computed KPI columns (may be pre-computed in the CSV)
    "Total CO2 - KPI":                    "co2_kpi",
    "Total energy - KPI":                 "energy_kpi",
    "Water intake - KPI":                 "water_kpi",
    "Renewable_Electricity_Share_%":      "renewable_share_pct",
    "Waste_Recovery_Rate_%":              "waste_recovery_pct",
    "Total CO2 (T.CO2)":                  "total_co2",
    "Total Energy (GJ)":                  "total_energy",
}


def _load_master_df():
    """Load the most-complete master CSV found in data_storage/master/."""
    files = sorted(glob.glob(_MASTER_GLOB), key=os.path.getmtime, reverse=True)
    best_rows = []
    for f in files:
        try:
            with open(f, newline="", encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
            if len(rows) > len(best_rows):
                best_rows = rows
        except Exception:
            pass
    return best_rows


def _row_to_dict(row: dict) -> dict:
    """Convert CSV row dict → canonical field dict."""
    out = {"Company": row.get("Company", ""), "Year": _int(row.get("Year"))}
    for csv_col, field in _COL_MAP.items():
        if csv_col in row:
            out[field] = _num(row[csv_col])
    return out


def _num(v, default=0.0):
    try: return float(str(v).replace(",", "").strip()) if v not in (None, "", "—") else default
    except: return default

def _int(v, default=0):
    try: return int(float(str(v).strip())) if v not in (None, "") else default
    except: return default


# ── Public API ─────────────────────────────────────────────────────────────────

def get_all_companies() -> list:
    return _COMPANIES


def get_company(company_name: str) -> dict | None:
    nl = company_name.lower()
    for c in _COMPANIES:
        if c["name"].lower() == nl or c["id"].lower() == nl:
            return c
    return None


def authenticate(email: str, password: str) -> dict | None:
    """Simple demo auth — password is always 'demo1234'."""
    email = email.strip().lower()
    if password != "demo1234":
        return None
    for c in _COMPANIES:
        if c["email"].lower() == email:
            return c
    return None


def get_master_rows(company_name: str = None, year: int = None) -> list:
    rows = _load_master_df()
    if company_name:
        rows = [r for r in rows if r.get("Company", "").strip() == company_name.strip()]
    if year:
        rows = [r for r in rows if _int(r.get("Year")) == year]
    return rows


def get_company_years(company_name: str) -> list:
    rows = get_master_rows(company_name)
    return sorted({_int(r["Year"]) for r in rows if r.get("Year")})


def get_submission(company_name: str, year: int) -> dict | None:
    rows = get_master_rows(company_name, year)
    return _row_to_dict(rows[0]) if rows else None


def get_historical_series(company_name: str, year_from: int = 2009, year_to: int = 2025) -> list:
    """Return list of {year, ...kpis} for all years in range."""
    from .calculations import calculate_all_kpis, calculate_yoy_change
    rows = get_master_rows(company_name)
    result = []
    prev_kpis = None
    for row in sorted(rows, key=lambda r: _int(r.get("Year", 0))):
        yr = _int(row.get("Year", 0))
        if not (year_from <= yr <= year_to):
            continue
        d = _row_to_dict(row)
        kpis = calculate_all_kpis(d)
        entry = {"year": yr, **kpis}
        if prev_kpis:
            entry["yoy"] = calculate_yoy_change(kpis["co2_kpi"], prev_kpis["co2_kpi"])
        result.append(entry)
        prev_kpis = kpis
    return result


def get_sector_series(year_from: int = 2009, year_to: int = 2025) -> list:
    """Return sector AVERAGE KPIs per year across all companies."""
    from .calculations import calculate_all_kpis
    rows = _load_master_df()
    by_year: dict[int, list] = {}
    for row in rows:
        yr = _int(row.get("Year", 0))
        if year_from <= yr <= year_to:
            by_year.setdefault(yr, []).append(_row_to_dict(row))

    result = []
    for yr in sorted(by_year):
        kpi_lists: dict[str, list] = {}
        for d in by_year[yr]:
            kpis = calculate_all_kpis(d)
            for k, v in kpis.items():
                kpi_lists.setdefault(k, []).append(v)
        avg = {k: round(sum(vs) / len(vs), 4) for k, vs in kpi_lists.items() if vs}
        result.append({"year": yr, "n_companies": len(by_year[yr]), **avg})
    return result


def get_sector_quartiles(year: int) -> dict:
    """Return Q1/median/Q3 for each KPI for a given year across all companies."""
    from .calculations import calculate_all_kpis
    import statistics
    rows = get_master_rows(year=year)
    kpi_lists: dict[str, list] = {}
    for row in rows:
        d = _row_to_dict(row)
        kpis = calculate_all_kpis(d)
        for k, v in kpis.items():
            if v and v > 0:
                kpi_lists.setdefault(k, []).append(v)

    result = {}
    for k, vals in kpi_lists.items():
        vals_s = sorted(vals)
        n = len(vals_s)
        if n >= 3:
            result[k] = {
                "q10":    round(vals_s[max(0, int(n * 0.10) - 1)], 4),
                "q25":    round(vals_s[max(0, int(n * 0.25) - 1)], 4),
                "median": round(statistics.median(vals_s), 4),
                "q75":    round(vals_s[min(n-1, int(n * 0.75))], 4),
                "q90":    round(vals_s[min(n-1, int(n * 0.90))], 4),
                "min":    round(vals_s[0], 4),
                "max":    round(vals_s[-1], 4),
                "n":      n,
            }
    return result


def save_submission(company_name: str, year: int, data: dict) -> dict:
    """Save/update a submission row in the master CSV."""
    from .calculations import calculate_all_kpis
    from datetime import datetime
    import pandas as pd

    kpis = calculate_all_kpis(data)
    master_row = {
        "Company": company_name, "Year": year,
        "Production":                           round(data.get("production", 0), 0),
        "Water withdrawals (m3)":               round(data.get("water_withdrawals", 0), 0),
        "Renewable electricity purchased (GJ)": round(data.get("renew_elec_purchased", 0), 2),
        "Non-renewable electricity purchased":  round(data.get("nonrenew_elec_purchased", 0), 2),
        "Self-generated renewable electricity": round(data.get("self_gen_elec", 0), 2),
        "Purchased Steam (GJ)":                 round(data.get("purchased_steam", 0), 2),
        "Natural Gas (GJ LHV)":                round(data.get("nat_gas", 0), 2),
        "Coal (GJ LHV)":                       round(data.get("coal_sub", 0), 2),
        "Diesel (GJ LHV)":                     round(data.get("diesel", 0), 2),
        "Total no. of sites":                  int(data.get("total_sites", 0)),
        "ISO 14001 certified sites":           int(data.get("iso_sites", 0)),
        "Total amount of waste (T)":           round(data.get("waste_total", 0), 2),
        "Amount of waste sent to recovery (T)":round(data.get("waste_recovery", 0), 2),
        "CO2 Scope 2 Steam (T.CO2)":          round(data.get("co2_scope2_steam", 0), 2),
        "Total CO2 - KPI":                     kpis["co2_kpi"],
        "Total energy - KPI":                  kpis["energy_kpi"],
        "Water intake - KPI":                  kpis["water_kpi"],
        "Renewable_Electricity_Share_%":       kpis["renewable_share_pct"],
        "Waste_Recovery_Rate_%":               kpis["waste_recovery_pct"],
        "Total CO2 (T.CO2)":                   kpis["total_co2_t"],
        "Total Energy (GJ)":                   kpis["total_energy_gj"],
        "submitted_at": datetime.utcnow().isoformat(),
    }

    # Find best existing master CSV
    files = sorted(glob.glob(_MASTER_GLOB), key=os.path.getmtime, reverse=True)
    if files:
        df = pd.read_csv(files[0])
    else:
        df = pd.DataFrame()

    # Remove old row for same company+year
    if not df.empty and "Company" in df.columns and "Year" in df.columns:
        mask = ~((df["Company"] == company_name) & (df["Year"] == year))
        df   = df[mask]

    new_row = pd.DataFrame([master_row])
    combined = pd.concat([df, new_row], ignore_index=True).sort_values(["Company","Year"])

    # Save — use year range in filename
    yr_min = int(combined["Year"].min())
    yr_max = int(combined["Year"].max())
    save_path = _DATA_DIR / "master" / f"ESG_MASTER_WIDE_ALL_COMPANIES_{yr_min}_{yr_max}.csv"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(save_path, index=False)

    return {"saved": True, "n_records": len(combined), "kpis": kpis}


def get_verification_status(company_name: str, year: int) -> str:
    """Read DSS+ verification status for a company+year."""
    if not _VERIF_CSV.exists():
        return "Pending"
    with open(_VERIF_CSV, newline="") as f:
        for row in csv.DictReader(f):
            if row.get("Company","").strip() == company_name and str(row.get("Year","")).strip() == str(year):
                return row.get("Status", "Pending")
    return "Pending"


def set_verification_status(company_name: str, year: int, status: str) -> None:
    """Write DSS+ verification status."""
    rows = []
    if _VERIF_CSV.exists():
        with open(_VERIF_CSV, newline="") as f:
            for row in csv.DictReader(f):
                if not (row.get("Company","").strip() == company_name and
                        str(row.get("Year","")).strip() == str(year)):
                    rows.append(row)
    rows.append({"Company": company_name, "Year": str(year), "Status": status,
                 "UpdatedAt": datetime.utcnow().isoformat()})
    _VERIF_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(_VERIF_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Company","Year","Status","UpdatedAt"])
        w.writeheader(); w.writerows(rows)
# ── Compatibility aliases — the existing __init__.py files use these names ─────

def _id_to_name(company_id: str) -> str:
    """Convert company slug (verdatyres) → full name (VerdaTyres Corp)."""
    for c in _COMPANIES:
        if c["id"].lower() == (company_id or "").lower():
            return c["name"]
    return company_id or ""

def _name_to_id(name: str) -> str:
    for c in _COMPANIES:
        if c["name"].lower() == (name or "").lower():
            return c["id"]
    return (name or "").lower().replace(" ", "_")

def get_submissions(company_id: str = None, year: int = None) -> list:
    """
    Compatibility shim for get_companies, get_benchmarks, get_analytics.
    Old code expected JSON submissions; new code reads master CSV.
    Returns same shape: [{company_id, year, kpis, status, flags}]
    """
    from .calculations import calculate_all_kpis
    rows = get_master_rows(
        company_name=_id_to_name(company_id) if company_id else None,
        year=year,
    )
    result = []
    for row in rows:
        d = _row_to_dict(row)
        if not d.get("Company") or not d.get("Year"):
            continue
        kpis = calculate_all_kpis(d)
        result.append({
            "company_id":   _name_to_id(d["Company"]),
            "company_name": d["Company"],
            "year":         d["Year"],
            "status":       "submitted",
            "submitted_at": row.get("submitted_at", ""),
            "kpis":         kpis,
            "flags":        [],
        })
    return result

def get_historical_kpi_series(company_id: str, kpi: str, years: list) -> list:
    """
    Compatibility shim for get_analytics.
    Returns [{year, value}] for a specific KPI and company.
    """
    company_name = _id_to_name(company_id) or company_id
    if not years:
        return []
    series = get_historical_series(company_name, min(years), max(years))
    series_map = {e["year"]: e.get(kpi) for e in series}
    return [{"year": yr, "value": series_map.get(yr)} for yr in years]

def get_sector_benchmarks(year: int) -> dict:
    """
    Compatibility shim for get_benchmarks.
    Returns {"year": ..., "kpis": {kpi: {q25, median, q75, ...}}}
    """
    q = get_sector_quartiles(year)
    return {"year": year, "kpis": q}

def get_prior_year_kpis(company_id: str, year: int) -> dict:
    """
    Compatibility shim for submit_data.
    Returns computed KPIs for year-1 (used for YoY flags).
    """
    from .calculations import calculate_all_kpis
    company_name = _id_to_name(company_id) or company_id
    sub = get_submission(company_name, year - 1)
    if not sub:
        return {}
    return calculate_all_kpis(sub)