import azure.functions as func
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.data_loader import get_historical_series, get_company_years, get_submission, get_verification_status
from shared.calculations import calculate_all_kpis

CORS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

# Template row definitions: (section, label, unit, field, formula_field)
TEMPLATE_ROWS = [
    ("ISO 14001",   "Total no. of sites",          "no.",     "total_sites",    None),
    ("ISO 14001",   "ISO 14001 certified sites",   "no.",     "iso_sites",      None),
    ("ISO 14001",   "% certified sites",           "%",       None,             "iso_certified_pct"),
    ("Production",  "Production",                  "metric T","production",     None),
    ("Water",       "Water withdrawals",           "m³",      "water_withdrawals",None),
    ("Water",       "Water Intensity KPI",         "m³/T",    None,             "water_kpi"),
    ("Energy",      "Total Electricity",           "GJ",      None,             "total_elec_gj"),
    ("Energy",      "— Renewable electricity purchased","GJ", "renew_elec_purchased",None),
    ("Energy",      "— Non-renewable electricity","GJ",       "nonrenew_elec_purchased",None),
    ("Energy",      "Natural Gas",                 "GJ LHV",  "nat_gas",        None),
    ("Energy",      "Coal (all types)",            "GJ LHV",  "coal_sub",       None),
    ("Energy",      "Diesel",                      "GJ LHV",  "diesel",         None),
    ("Energy",      "Biomass",                     "GJ LHV",  "biomass",        None),
    ("Energy",      "Total Energy",                "GJ",      None,             "total_energy_gj"),
    ("Energy",      "Energy Intensity KPI",        "GJ/T",    None,             "energy_kpi"),
    ("CO2",         "CO₂ Scope 2 from Steam",      "T.CO₂",   "co2_scope2_steam",None),
    ("CO2",         "Total CO₂ (Scope 1+2)",       "T.CO₂",   None,             "total_co2_t"),
    ("CO2",         "CO₂ Intensity KPI",           "T.CO₂/T", None,             "co2_kpi"),
    ("CO2",         "Scope 1 CO₂",                 "T.CO₂",   None,             "scope1_co2_t"),
    ("CO2",         "Scope 2 CO₂",                 "T.CO₂",   None,             "scope2_co2_t"),
    ("Waste",       "Total amount of waste",       "metric T","waste_total",    None),
    ("Waste",       "Waste sent to recovery",      "metric T","waste_recovery",  None),
    ("Waste",       "Waste Recovery Rate",         "%",       None,             "waste_recovery_pct"),
]

def _fmt(v, unit):
    if v is None or v == 0:
        return "—"
    if unit in ("%",):
        return f"{v:.1f}%"
    if unit in ("T.CO₂/T", "m³/T", "GJ/T"):
        return f"{v:.3f}"
    return f"{v:,.0f}"

def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=CORS)
    try:
        company  = req.params.get("company", "VerdaTyres Corp")
        sel_year = int(req.params.get("year", 2023))

        years    = get_company_years(company)
        yr_from  = min(years) if years else 2009
        series   = get_historical_series(company, yr_from, sel_year)
        all_years = [e["year"] for e in series]

        # Build raw data per year
        raw_by_year: dict[int, dict] = {}
        for yr in all_years:
            sub   = get_submission(company, yr)
            kpis  = calculate_all_kpis(sub or {})
            raw_by_year[yr] = {**(sub or {}), **kpis}

        # Build template rows
        rows = []
        for section, label, unit, raw_field, kpi_field in TEMPLATE_ROWS:
            row = {
                "section": section,
                "label": label,
                "unit": unit,
                "type": "input" if raw_field else "formula",
            }
            values = {}
            for yr in all_years:
                d = raw_by_year.get(yr, {})
                if raw_field:
                    v = d.get(raw_field)
                else:
                    v = d.get(kpi_field)
                values[str(yr)] = _fmt(v, unit)
            row["values"] = values
            # YoY for last two years
            if len(all_years) >= 2:
                last   = raw_by_year.get(all_years[-1], {})
                before = raw_by_year.get(all_years[-2], {})
                field  = raw_field or kpi_field
                v_last = last.get(field, 0) or 0
                v_prev = before.get(field, 0) or 0
                if v_prev and v_prev != 0:
                    pct = (v_last - v_prev) / abs(v_prev) * 100
                    row["yoy"] = f"{pct:+.1f}%"
                else:
                    row["yoy"] = "—"
            rows.append(row)

        # Verification status
        verif = get_verification_status(company, sel_year)

        result = {
            "company": company,
            "selected_year": sel_year,
            "available_years": sorted(set(years + [sel_year])),
            "next_year": max(years) + 1 if years else sel_year + 1,
            "all_years": all_years,
            "rows": rows,
            "verification_status": verif,
        }
        return func.HttpResponse(json.dumps(result), mimetype="application/json", headers=CORS)
    except Exception as ex:
        return func.HttpResponse(json.dumps({"error": str(ex)}), status_code=500,
                                 mimetype="application/json", headers=CORS)
