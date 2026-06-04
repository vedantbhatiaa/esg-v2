"""
ESG Data Loader — reads from the master CSV.
Column names match the ACTUAL CSV headers exactly.
"""
import os, glob, csv, statistics
from pathlib import Path
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────────────────────────
_HERE     = Path(__file__).resolve().parent.parent   # python-service/
_DATA_DIR = _HERE.parent / "data_storage"             # esg-v2/data_storage/
_MASTER_GLOB = str(_DATA_DIR / "master" / "ESG_MASTER_WIDE_ALL_COMPANIES_*.csv")
_VERIF_CSV   = _DATA_DIR / "verifications.csv"

# ── Companies ──────────────────────────────────────────────────────────────────
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

# ── Exact CSV column → canonical field name mapping ────────────────────────────
# Column names taken directly from CSV header row
_COL_MAP = {
    # Identity
    "Company":                                        "company",
    "Year":                                           "year",
    # Sites
    "Total no. of sites":                             "total_sites",
    "ISO 14001 sites":                                "iso_sites",
    "% certified sites":                              "iso_certified_pct_raw",
    # Production
    "Production":                                     "production_t",
    # Water
    "Water intake":                                   "total_water_m3",
    "Water intake - KPI":                             "water_kpi",
    # Electricity
    "Total Electricity":                              "total_elec_gj",
    "Renewable Electricity Purchased":                "renew_elec_gj",
    "Non-Renewable Electricity Purchased":            "nonrenew_elec_gj",
    "Self-generated AND consumed electricity on-site":"self_gen_elec_gj",
    "Purchased Steam":                                "purchased_steam_gj",
    "Sold Electricity":                               "sold_elec_gj",
    # Fuels
    "Natural Gas":                                    "nat_gas_gj",
    "Coal":                                           "coal_gj",
    "Propane":                                        "propane_gj",
    "Fuel Oil":                                       "fuel_oil_gj",
    "Diesel":                                         "diesel_gj",
    "Petrol":                                         "petrol_gj",
    "Biomass":                                        "biomass_gj",
    "Waste tires":                                    "waste_tires_gj",
    "LPG":                                            "lpg_gj",
    "Other":                                          "other_fuel_gj",
    # Energy totals
    "Total energy":                                   "total_energy_gj",
    "Total energy - KPI":                             "energy_kpi",
    # CO2
    "Total CO2 - Scope 1":                            "scope1_co2_t",
    "Total CO2 - Scope 2":                            "scope2_co2_t",
    "Total CO2":                                      "total_co2_t",
    "Total CO2 - KPI":                                "co2_kpi",
    # Waste
    "Total Waste":                                    "waste_total_t",
    "Waste Recovered":                                "waste_recovered_t",
    "Recovery Rate":                                  "waste_recovery_pct",
    # Pre-computed %
    "Renewable_Electricity_Share_%":                  "renewable_share_pct",
    "Scope1_Share_%":                                 "scope1_share_pct",
    "Scope2_Share_%":                                 "scope2_share_pct",
    "Fossil_Energy_Share_%":                          "fossil_share_pct",
    "ISO_Certification_%":                            "iso_certified_pct",
    "Waste_Recovery_Rate_%":                          "waste_recovery_pct2",
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def _num(v, default=0.0):
    try:
        return float(str(v).replace(",", "").strip()) if v not in (None, "", "—", "N/A") else default
    except Exception:
        return default

def _int(v, default=0):
    try:
        return int(float(str(v).strip())) if v not in (None, "") else default
    except Exception:
        return default

def _load_master_df():
    """Load the most-complete master CSV by row count."""
    files = sorted(glob.glob(_MASTER_GLOB), key=os.path.getmtime, reverse=True)
    best = []
    for f in files:
        try:
            with open(f, newline="", encoding="utf-8-sig") as fh:
                rows = list(csv.DictReader(fh))
            if len(rows) > len(best):
                best = rows
        except Exception:
            pass
    return best

def _row_to_dict(row: dict) -> dict:
    """Convert raw CSV row → canonical field dict using exact column names."""
    out = {}
    for csv_col, field in _COL_MAP.items():
        if csv_col in row:
            out[field] = _num(row[csv_col])
    out["Company"] = row.get("Company", "")
    out["Year"]    = _int(row.get("Year", 0))
    # Prefer iso_certified_pct from ISO_Certification_% (0-100 scale)
    # If it was stored as 0-1 fraction, convert
    if "iso_certified_pct" in out and out["iso_certified_pct"] <= 1.0:
        out["iso_certified_pct"] = round(out["iso_certified_pct"] * 100, 1)
    # Normalize waste_recovery_pct to 0-100 scale
    # "Recovery Rate" CSV column stores 0-1 fraction; "Waste_Recovery_Rate_%" stores 0-100
    # Prefer waste_recovery_pct2 (0-100) if available and non-zero
    if "waste_recovery_pct2" in out and out.get("waste_recovery_pct2", 0) > 0:
        out["waste_recovery_pct"] = out["waste_recovery_pct2"]
    elif "waste_recovery_pct" in out and out["waste_recovery_pct"] <= 1.0 and out["waste_recovery_pct"] > 0:
        out["waste_recovery_pct"] = round(out["waste_recovery_pct"] * 100, 2)
    # Normalize renewable_share_pct: always 0-100
    if "renewable_share_pct" in out and out["renewable_share_pct"] <= 1.0 and out["renewable_share_pct"] > 0:
        out["renewable_share_pct"] = round(out["renewable_share_pct"] * 100, 2)
    return out

# ── Public API ─────────────────────────────────────────────────────────────────
def get_all_companies() -> list:
    return _COMPANIES

def get_company(name: str) -> dict | None:
    name_l = name.lower()
    for c in _COMPANIES:
        if c["name"].lower() == name_l or c["id"].lower() == name_l:
            return c
    return None

def authenticate(email: str, password: str) -> dict | None:
    if password != "demo1234":
        return None
    email_l = email.strip().lower()
    for c in _COMPANIES:
        if c["email"].lower() == email_l:
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

def get_historical_series(company_name: str, year_from: int = 2009, year_to: int = 2030) -> list:
    """
    Return [{year, co2_kpi, energy_kpi, water_kpi, ...}] using PRE-COMPUTED
    values from CSV — no recalculation needed, values are already verified.
    """
    rows = get_master_rows(company_name)
    result = []
    for row in sorted(rows, key=lambda r: _int(r.get("Year", 0))):
        yr = _int(row.get("Year", 0))
        if not (year_from <= yr <= year_to):
            continue
        d = _row_to_dict(row)
        # Use pre-computed CSV values directly — these match the Streamlit app exactly
        entry = {
            "year":               yr,
            "production_t":       d.get("production_t", 0),
            "co2_kpi":            d.get("co2_kpi", 0),
            "energy_kpi":         d.get("energy_kpi", 0),
            "water_kpi":          d.get("water_kpi", 0),
            "renewable_share_pct":d.get("renewable_share_pct", 0),
            "waste_recovery_pct": d.get("waste_recovery_pct", d.get("waste_recovery_pct2", 0)),
            "iso_certified_pct":  d.get("iso_certified_pct", 0),
            # Absolutes
            "total_co2_t":        d.get("total_co2_t", 0),
            "scope1_co2_t":       d.get("scope1_co2_t", 0),
            "scope2_co2_t":       d.get("scope2_co2_t", 0),
            "total_energy_gj":    d.get("total_energy_gj", 0),
            "total_elec_gj":      d.get("total_elec_gj", 0),
            "renew_elec_gj":      d.get("renew_elec_gj", 0),
            "nonrenew_elec_gj":   d.get("nonrenew_elec_gj", 0),
            "total_water_m3":     d.get("total_water_m3", 0),
            "waste_total_t":      d.get("waste_total_t", 0),
            "waste_recovered_t":  d.get("waste_recovered_t", 0),
            # Fuels
            "nat_gas_gj":         d.get("nat_gas_gj", 0),
            "coal_gj":            d.get("coal_gj", 0),
            "diesel_gj":          d.get("diesel_gj", 0),
            "biomass_gj":         d.get("biomass_gj", 0),
            "total_fossil_gj":    (d.get("total_energy_gj", 0)
                                   - d.get("total_elec_gj", 0)
                                   - d.get("purchased_steam_gj", 0)),
        }
        result.append(entry)
    return result

def get_sector_series(year_from: int = 2009, year_to: int = 2030) -> list:
    """Sector AVERAGE KPIs per year across all companies."""
    rows = _load_master_df()
    by_year: dict[int, list] = {}
    for row in rows:
        yr = _int(row.get("Year", 0))
        if year_from <= yr <= year_to:
            by_year.setdefault(yr, []).append(_row_to_dict(row))
    result = []
    KPI_FIELDS = ["co2_kpi","energy_kpi","water_kpi","renewable_share_pct",
                  "waste_recovery_pct","iso_certified_pct","total_co2_t",
                  "scope1_co2_t","scope2_co2_t","total_energy_gj","total_water_m3"]
    for yr in sorted(by_year):
        entry = {"year": yr, "n_companies": len(by_year[yr])}
        for field in KPI_FIELDS:
            vals = [d.get(field, 0) for d in by_year[yr] if (d.get(field) or 0) > 0]
            entry[field] = round(sum(vals) / len(vals), 4) if vals else 0
        result.append(entry)
    return result

def get_sector_quartiles(year: int) -> dict:
    """Q1/median/Q3 for each KPI across all companies for a given year."""
    rows = get_master_rows(year=year)
    KPI_FIELDS = ["co2_kpi","energy_kpi","water_kpi","renewable_share_pct",
                  "waste_recovery_pct","iso_certified_pct"]
    kpi_lists: dict[str, list] = {}
    for row in rows:
        d = _row_to_dict(row)
        for f in KPI_FIELDS:
            v = d.get(f) or 0
            if v > 0:
                kpi_lists.setdefault(f, []).append(v)
    result = {}
    for k, vals in kpi_lists.items():
        vals_s = sorted(vals)
        n = len(vals_s)
        if n >= 2:
            result[k] = {
                "q10":    round(vals_s[max(0, int(n*0.10))], 4),
                "q25":    round(vals_s[max(0, int(n*0.25))], 4),
                "median": round(statistics.median(vals_s), 4),
                "q75":    round(vals_s[min(n-1, int(n*0.75))], 4),
                "q90":    round(vals_s[min(n-1, int(n*0.90))], 4),
                "min":    round(vals_s[0], 4),
                "max":    round(vals_s[-1], 4),
                "n":      n,
            }
    return result

def get_verification_status(company_name: str, year: int) -> str:
    if not _VERIF_CSV.exists():
        return "Pending"
    try:
        with open(_VERIF_CSV, newline="") as f:
            for row in csv.DictReader(f):
                if (row.get("Company","").strip() == company_name and
                        str(row.get("Year","")).strip() == str(year)):
                    return row.get("Status", "Pending")
    except Exception:
        pass
    return "Pending"

def set_verification_status(company_name: str, year: int, status: str) -> None:
    rows = []
    if _VERIF_CSV.exists():
        try:
            with open(_VERIF_CSV, newline="") as f:
                for row in csv.DictReader(f):
                    if not (row.get("Company","").strip() == company_name and
                            str(row.get("Year","")).strip() == str(year)):
                        rows.append(row)
        except Exception:
            pass
    rows.append({"Company": company_name, "Year": str(year), "Status": status,
                 "UpdatedAt": datetime.utcnow().isoformat()})
    _VERIF_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(_VERIF_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Company","Year","Status","UpdatedAt"])
        w.writeheader()
        w.writerows(rows)

def save_submission(company_name: str, year: int, data: dict) -> dict:
    """Save/update a row in the master CSV."""
    import pandas as pd
    from .calculations import calculate_all_kpis
    kpis = calculate_all_kpis(data)
    new_row = {
        "Company":                                        company_name,
        "Year":                                           year,
        "Total no. of sites":                             int(data.get("total_sites", 0)),
        "ISO 14001 sites":                                int(data.get("iso_sites", 0)),
        "% certified sites":                              round(int(data.get("iso_sites",0)) / max(1, int(data.get("total_sites",1))), 4),
        "Production":                                     data.get("production_t", 0),
        "Water intake":                                   data.get("total_water_m3", 0),
        "Water intake - KPI":                             kpis.get("water_kpi", 0),
        "Total Electricity":                              kpis.get("total_elec_gj", 0),
        "Renewable Electricity Purchased":                data.get("renew_elec_gj", 0),
        "Non-Renewable Electricity Purchased":            data.get("nonrenew_elec_gj", 0),
        "Self-generated AND consumed electricity on-site":data.get("self_gen_elec_gj", 0),
        "Purchased Steam":                                data.get("purchased_steam_gj", 0),
        "Natural Gas":                                    data.get("nat_gas_gj", 0),
        "Coal":                                           data.get("coal_gj", 0),
        "Diesel":                                         data.get("diesel_gj", 0),
        "Biomass":                                        data.get("biomass_gj", 0),
        "Total energy":                                   kpis.get("total_energy_gj", 0),
        "Total energy - KPI":                             kpis.get("energy_kpi", 0),
        "Total CO2 - Scope 1":                            kpis.get("scope1_co2_t", 0),
        "Total CO2 - Scope 2":                            kpis.get("scope2_co2_t", 0),
        "Total CO2":                                      kpis.get("total_co2_t", 0),
        "Total CO2 - KPI":                                kpis.get("co2_kpi", 0),
        "Total Waste":                                    data.get("waste_total_t", 0),
        "Waste Recovered":                                data.get("waste_recovered_t", 0),
        "Recovery Rate":                                  kpis.get("waste_recovery_pct", 0),
        "Renewable_Electricity_Share_%":                  kpis.get("renewable_share_pct", 0),
        "ISO_Certification_%":                            kpis.get("iso_certified_pct", 0),
        "Waste_Recovery_Rate_%":                          kpis.get("waste_recovery_pct", 0),
        "submitted_at":                                   datetime.utcnow().isoformat(),
    }
    files = sorted(glob.glob(_MASTER_GLOB), key=os.path.getmtime, reverse=True)
    if files:
        df = pd.read_csv(files[0])
    else:
        df = pd.DataFrame()
    if not df.empty and "Company" in df.columns and "Year" in df.columns:
        df = df[~((df["Company"] == company_name) & (df["Year"] == year))]
    combined = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    combined = combined.sort_values(["Company","Year"]).reset_index(drop=True)
    yr_min = int(combined["Year"].min())
    yr_max = int(combined["Year"].max())
    save_path = _DATA_DIR / "master" / f"ESG_MASTER_WIDE_ALL_COMPANIES_{yr_min}_{yr_max}.csv"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(save_path, index=False)
    return {"saved": True, "n_records": len(combined), "kpis": kpis}

# ── Compatibility aliases (old __init__.py files use these names) ──────────────
def _id_to_name(company_id: str) -> str:
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
    """Compat shim — used by get_companies, get_benchmarks, get_analytics."""
    rows = get_master_rows(
        company_name=_id_to_name(company_id) if company_id else None,
        year=year,
    )
    result = []
    for row in rows:
        d = _row_to_dict(row)
        if not d.get("Company") or not d.get("Year"):
            continue
        result.append({
            "company_id":   _name_to_id(d["Company"]),
            "company_name": d["Company"],
            "year":         d["Year"],
            "status":       "submitted",
            "submitted_at": row.get("submitted_at", ""),
            "kpis": {
                "co2_kpi":            d.get("co2_kpi", 0),
                "energy_kpi":         d.get("energy_kpi", 0),
                "water_kpi":          d.get("water_kpi", 0),
                "renewable_share_pct":d.get("renewable_share_pct", 0),
                "waste_recovery_pct": d.get("waste_recovery_pct", 0),
                "iso_certified_pct":  d.get("iso_certified_pct", 0),
                "total_co2_t":        d.get("total_co2_t", 0),
                "scope1_co2_t":       d.get("scope1_co2_t", 0),
                "scope2_co2_t":       d.get("scope2_co2_t", 0),
            },
            "flags": [],
        })
    return result

def get_historical_kpi_series(company_id: str, kpi: str, years: list) -> list:
    """Compat shim — used by get_analytics."""
    name   = _id_to_name(company_id) or company_id
    if not years:
        return []
    series = get_historical_series(name, min(years), max(years))
    series_map = {e["year"]: e.get(kpi) for e in series}
    return [{"year": yr, "value": series_map.get(yr)} for yr in years]

def get_sector_benchmarks(year: int) -> dict:
    """Compat shim — used by get_benchmarks."""
    return {"year": year, "kpis": get_sector_quartiles(year)}

def get_prior_year_kpis(company_id: str, year: int) -> dict:
    """Compat shim — used by submit_data."""
    name = _id_to_name(company_id) or company_id
    sub  = get_submission(name, year - 1)
    if not sub:
        return {}
    return {
        "co2_kpi":            sub.get("co2_kpi", 0),
        "energy_kpi":         sub.get("energy_kpi", 0),
        "water_kpi":          sub.get("water_kpi", 0),
        "renewable_share_pct":sub.get("renewable_share_pct", 0),
        "waste_recovery_pct": sub.get("waste_recovery_pct", 0),
        "total_co2_t":        sub.get("total_co2_t", 0),
        "total_energy_gj":    sub.get("total_energy_gj", 0),
    }