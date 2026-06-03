"""
ESG Data Loader
Reads from CSV files (same source as original Streamlit app).
When Azure SQL is ready, swap out the CSV reads here — nothing else changes.
"""

import os
import json
import csv
from datetime import datetime

# Path to your existing data files
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
SUBMISSIONS_FILE = os.path.join(DATA_DIR, "submissions.json")
COMPANIES_FILE   = os.path.join(DATA_DIR, "companies.json")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_json(filepath: str, default):
    if not os.path.exists(filepath):
        return default
    with open(filepath, "r") as f:
        return json.load(f)


def _save_json(filepath: str, data):
    _ensure_data_dir()
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ── Companies ──────────────────────────────────────────────────────────────────

def get_all_companies() -> list:
    """Returns list of all TIP member companies."""
    return _load_json(COMPANIES_FILE, [
        {"id": "verdatyres",   "name": "VerdaTyres Corp",  "region": "Europe"},
        {"id": "alphatread",   "name": "AlphaTread Ltd",   "region": "Europe"},
        {"id": "betarubber",   "name": "BetaRubber Inc",   "region": "Americas"},
        {"id": "gammatire",    "name": "GammaTire SA",     "region": "Europe"},
        {"id": "deltagrip",    "name": "DeltaGrip GmbH",  "region": "Europe"},
        {"id": "epsilonwheel", "name": "EpsilonWheel Co", "region": "Asia"},
        {"id": "zetatrac",     "name": "ZetaTrac LLC",    "region": "Americas"},
        {"id": "etakomp",      "name": "EtaKomp AG",      "region": "Europe"},
        {"id": "thetarubber",  "name": "ThetaRubber KK",  "region": "Asia"},
        {"id": "iotawheel",    "name": "IotaWheel Ltd",   "region": "Asia"},
    ])


# ── Submissions ────────────────────────────────────────────────────────────────

def get_submissions(company_id: str = None, year: int = None) -> list:
    """Get all submissions, optionally filtered."""
    all_subs = _load_json(SUBMISSIONS_FILE, [])
    if company_id:
        all_subs = [s for s in all_subs if s.get("company_id") == company_id]
    if year:
        all_subs = [s for s in all_subs if s.get("year") == year]
    return all_subs


def get_submission(company_id: str, year: int) -> dict | None:
    """Get a specific submission."""
    subs = get_submissions(company_id, year)
    return subs[0] if subs else None


def save_submission(submission: dict) -> dict:
    """Save or update a submission."""
    _ensure_data_dir()
    all_subs = _load_json(SUBMISSIONS_FILE, [])

    # Remove existing submission for same company+year
    all_subs = [
        s for s in all_subs
        if not (s.get("company_id") == submission["company_id"]
                and s.get("year") == submission["year"])
    ]

    submission["submitted_at"] = datetime.utcnow().isoformat()
    all_subs.append(submission)
    _save_json(SUBMISSIONS_FILE, all_subs)
    return submission


def get_prior_year_kpis(company_id: str, year: int) -> dict | None:
    """Get KPIs from the previous year for YoY comparison."""
    prior = get_submission(company_id, year - 1)
    if prior:
        return prior.get("kpis", {})
    return None


# ── Historical series (for charts) ─────────────────────────────────────────────

def get_historical_kpi_series(company_id: str, kpi_key: str, years: list = None) -> list:
    """
    Returns [{year, value}, ...] for charting.
    Uses submitted data if available, falls back to CSV baseline data.
    """
    all_subs = get_submissions(company_id)
    sub_map  = {s["year"]: s.get("kpis", {}).get(kpi_key) for s in all_subs}

    if years is None:
        years = list(range(2009, 2024))

    # Baseline sector averages (from original app.py data)
    BASELINE = {
        "energy_kpi":          [10.8,10.5,10.2,10.0,9.8,9.6,9.5,9.4,9.3,9.2,9.1,9.7,9.7,9.1,8.7],
        "co2_kpi":             [0.82,0.79,0.76,0.74,0.72,0.71,0.69,0.67,0.66,0.64,0.63,0.60,0.58,0.576,0.551],
        "renewable_share_pct": [2,2,3,3,4,5,6,7,9,12,16,22,20,31,38.8],
        "water_kpi":           [7.2,7.0,6.8,6.6,6.5,6.4,6.3,6.2,6.1,6.0,5.9,5.85,5.71,5.73,5.78],
        "waste_recovery_pct":  [78,79,80,80,81,81,82,82,82,83,83,83,83,85,85.8],
        "total_co2_t":         [3100000,3000000,2900000,2850000,2800000,2780000,2720000,2650000,2600000,2550000,2500000,2420000,2270000,2060000,2050000],
        "total_energy_gj":     [26000000,25500000,25000000,24800000,24500000,24200000,24000000,23800000,23500000,23200000,22900000,24500000,24500000,23000000,22000000],
    }

    result = []
    base_years = list(range(2009, 2024))

    for i, yr in enumerate(years):
        if yr in sub_map and sub_map[yr] is not None:
            val = sub_map[yr]
        elif kpi_key in BASELINE and yr in base_years:
            idx = base_years.index(yr)
            val = BASELINE[kpi_key][idx]
        else:
            val = None
        result.append({"year": yr, "value": val})

    return result


# ── Benchmarking data ──────────────────────────────────────────────────────────

def get_sector_benchmarks(year: int) -> dict:
    """
    Returns sector-wide quartile stats for each KPI.
    In V2 this will be computed from all submissions — for now uses baseline.
    """
    return {
        "year": year,
        "kpis": {
            "energy_kpi": {
                "q25": 7.9, "median": 8.8, "q75": 9.6,
                "unit": "GJ/T", "lower_is_better": True,
            },
            "co2_kpi": {
                "q25": 0.52, "median": 0.64, "q75": 0.76,
                "unit": "T.CO2/T", "lower_is_better": True,
            },
            "water_kpi": {
                "q25": 5.20, "median": 5.90, "q75": 6.60,
                "unit": "m3/T", "lower_is_better": True,
            },
            "renewable_share_pct": {
                "q25": 45, "median": 30, "q75": 18,
                "unit": "%", "lower_is_better": False,
            },
            "iso_certified_pct": {
                "q25": 100, "median": 88, "q75": 76,
                "unit": "%", "lower_is_better": False,
            },
            "waste_recovery_pct": {
                "q25": 90, "median": 85.5, "q75": 78,
                "unit": "%", "lower_is_better": False,
            },
        }
    }
