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

TEMPLATE_ROWS = [
    ("ISO 14001",  "Total no. of sites",               "no.",     "total_sites",       None),
    ("ISO 14001",  "ISO 14001 certified sites",        "no.",     "iso_sites",         None),
    ("ISO 14001",  "% certified sites",                "%",       None,                "iso_certified_pct"),
    ("Production", "Production",                       "metric T","production_t",      None),
    ("Water",      "Water withdrawals",                "m3",      "total_water_m3",    None),
    ("Water",      "Water Intensity KPI",              "m3/T",    None,                "water_kpi"),
    ("Energy",     "Total Electricity",                "GJ",      None,                "total_elec_gj"),
    ("Energy",     "Renewable electricity purchased",  "GJ",      "renew_elec_gj",     None),
    ("Energy",     "Non-renewable electricity",        "GJ",      "nonrenew_elec_gj",  None),
    ("Energy",     "Self-generated electricity",       "GJ",      "self_gen_elec_gj",  None),
    ("Energy",     "Purchased Steam",                  "GJ",      "purchased_steam_gj",None),
    ("Energy",     "Natural Gas",                      "GJ LHV",  "nat_gas_gj",        None),
    ("Energy",     "Coal",                             "GJ LHV",  "coal_gj",           None),
    ("Energy",     "Propane",                          "GJ LHV",  "propane_gj",        None),
    ("Energy",     "Fuel Oil",                         "GJ LHV",  "fuel_oil_gj",       None),
    ("Energy",     "Diesel",                           "GJ LHV",  "diesel_gj",         None),
    ("Energy",     "Petrol",                           "GJ LHV",  "petrol_gj",         None),
    ("Energy",     "Biomass",                          "GJ LHV",  "biomass_gj",        None),
    ("Energy",     "LPG",                              "GJ LHV",  "lpg_gj",            None),
    ("Energy",     "Other fuels",                      "GJ LHV",  "other_fuel_gj",     None),
    ("Energy",     "Total Energy",                     "GJ",      None,                "total_energy_gj"),
    ("Energy",     "Energy Intensity KPI",             "GJ/T",    None,                "energy_kpi"),
    ("CO2",        "Scope 1 CO2",                      "T.CO2",   None,                "scope1_co2_t"),
    ("CO2",        "Scope 2 CO2",                      "T.CO2",   None,                "scope2_co2_t"),
    ("CO2",        "Total CO2",                        "T.CO2",   None,                "total_co2_t"),
    ("CO2",        "CO2 Intensity KPI",                "T.CO2/T", None,                "co2_kpi"),
    ("Waste",      "Total waste",                      "metric T","waste_total_t",     None),
    ("Waste",      "Waste recovered",                  "metric T","waste_recovered_t", None),
    ("Waste",      "Waste Recovery Rate",              "%",       None,                "waste_recovery_pct"),
]

def _fmt(v, unit):
    if v is None: return "—"
    try: fv = float(v)
    except: return str(v)
    if fv == 0: return "—"
    if unit == "%": return f"{fv:.1f}%"
    if unit in ("T.CO2/T", "m3/T", "GJ/T"): return f"{fv:.3f}"
    return f"{fv:,.0f}"

def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=CORS)
    try:
        company  = req.params.get("company", "VerdaTyres Corp")
        sel_year = int(req.params.get("year", 2023))
        years    = get_company_years(company)
        if not years:
            return func.HttpResponse(json.dumps({
                "error": f"No data for {company}. Run build_esg_master.py first.",
                "rows": [], "all_years": [], "available_years": [sel_year]
            }), mimetype="application/json", headers=CORS)

        series    = get_historical_series(company, min(years), max(years))
        all_years = [e["year"] for e in series]

        raw_by_year = {}
        for yr in all_years:
            sub          = get_submission(company, yr) or {}
            calc         = calculate_all_kpis(sub)
            series_entry = next((e for e in series if e["year"] == yr), {})
            raw_by_year[yr] = {**sub, **calc, **series_entry}

        rows = []
        for section, label, unit, raw_field, kpi_field in TEMPLATE_ROWS:
            values = {}
            for yr in all_years:
                d = raw_by_year.get(yr, {})
                v = d.get(raw_field or kpi_field)
                values[str(yr)] = _fmt(v, unit)

            yoy = "—"
            if len(all_years) >= 2:
                field = raw_field or kpi_field
                try:
                    v_last = float(raw_by_year.get(all_years[-1], {}).get(field) or 0)
                    v_prev = float(raw_by_year.get(all_years[-2], {}).get(field) or 0)
                    if v_prev:
                        pct = (v_last - v_prev) / abs(v_prev) * 100
                        yoy = f"{pct:+.1f}%"
                except Exception:
                    pass

            rows.append({"section":section,"label":label,"unit":unit,
                         "type":"input" if raw_field else "formula",
                         "values":values,"yoy":yoy})

        return func.HttpResponse(json.dumps({
            "company":           company,
            "selected_year":     sel_year,
            "available_years":   sorted(set(list(years)+[sel_year])),
            "next_year":         max(years)+1,
            "all_years":         all_years,
            "rows":              rows,
            "verification_status": get_verification_status(company, sel_year),
        }, default=str), mimetype="application/json", headers=CORS)
    except Exception as ex:
        import traceback
        return func.HttpResponse(json.dumps({"error":str(ex),"trace":traceback.format_exc()}),
                                 status_code=500, mimetype="application/json", headers=CORS)