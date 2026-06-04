import azure.functions as func
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.data_loader import get_historical_series, get_company_years, get_verification_status
from shared.calculations import calculate_all_kpis

CORS = {"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"GET,OPTIONS","Access-Control-Allow-Headers":"Content-Type"}

# TEMPLATE_ROWS — exact match with Streamlit render_template_table() ROWS list
# (type, label, unit, input_field, calc_key)
TEMPLATE_ROWS = [
    ("section", "ISO 14001",       None,       None,                   None),
    ("input",   "Total no. of sites",        "no.",      "total_sites",          None),
    ("input",   "ISO 14001 certified sites", "no.",      "iso_sites",            None),
    ("calc",    "% certified sites",         "%",        None,                   "pct_certified_pct"),
    ("section", "Production",      None,       None,                   None),
    ("input",   "Production",                "metric T", "production",           None),
    ("section", "Water",           None,       None,                   None),
    ("input",   "Water withdrawals",         "m3",       "water_withdrawals",    None),
    ("calc",    "Water intensity KPI",       "m3/T",     None,                   "water_kpi"),
    ("section", "Energy",          None,       None,                   None),
    ("calc",    "Total Electricity",         "GJ",       None,                   "total_electricity"),
    ("input",   "Renewable electricity purchased",    "GJ", "renew_elec_purchased",  None),
    ("input",   "Non-renewable electricity purchased","GJ", "nonrenew_elec_purchased",None),
    ("input",   "Self-generated renewable on-site",  "GJ", "self_gen_elec",         None),
    ("input",   "Purchased Steam",           "GJ",       "purchased_steam",      None),
    ("input",   "Sold Electricity",          "GJ",       "sold_electricity",     None),
    ("input",   "Sold Steam",                "GJ",       "sold_steam",           None),
    ("input",   "Natural Gas",               "GJ LHV",   "nat_gas",              None),
    ("input",   "Coal (all types)",          "GJ LHV",   "coal_sub",             None),
    ("input",   "Propane",                   "GJ LHV",   "propane",              None),
    ("input",   "Fuel Oil",                  "GJ LHV",   "fuel_oil_heavy_a",     None),
    ("input",   "Diesel",                    "GJ LHV",   "diesel",               None),
    ("input",   "Petrol",                    "GJ LHV",   "petrol",               None),
    ("input",   "Biomass",                   "GJ LHV",   "biomass",              None),
    ("input",   "Waste tires",               "metric T", "waste_tires_mt",       None),
    ("input",   "LPG",                       "GJ LHV",   "lpg",                  None),
    ("input",   "Other fuels",               "GJ LHV",   "other_fuels",          None),
    ("calc",    "TOTAL ENERGY",              "GJ",       None,                   "total_energy"),
    ("calc",    "Energy intensity KPI",      "GJ/T",     None,                   "energy_kpi"),
    ("section", "CO2 Emissions",   None,       None,                   None),
    ("input",   "Scope 2 from Steam",        "T.CO2",    "co2_scope2_steam",     None),
    ("calc",    "CO2 Natural Gas",           "T.CO2",    None,                   "co2_nat_gas"),
    ("calc",    "CO2 Coal",                  "T.CO2",    None,                   "co2_coal"),
    ("calc",    "CO2 Propane",               "T.CO2",    None,                   "co2_propane"),
    ("calc",    "CO2 Fuel Oil",              "T.CO2",    None,                   "co2_fuel_oil"),
    ("calc",    "CO2 Diesel",                "T.CO2",    None,                   "co2_diesel"),
    ("calc",    "CO2 Petrol",                "T.CO2",    None,                   "co2_petrol"),
    ("calc",    "CO2 LPG",                   "T.CO2",    None,                   "co2_lpg"),
    ("calc",    "TOTAL CO2 Scope 1",         "T.CO2",    None,                   "scope1"),
    ("calc",    "TOTAL CO2 Scope 2",         "T.CO2",    None,                   "scope2"),
    ("calc",    "TOTAL CO2 (S1+S2)",         "T.CO2",    None,                   "total_co2"),
    ("calc",    "CO2 intensity KPI",         "T.CO2/T",  None,                   "co2_kpi"),
    ("section", "Waste",           None,       None,                   None),
    ("input",   "Total waste generated",     "metric T", "waste_total",          None),
    ("input",   "Waste sent to recovery",    "metric T", "waste_recovery",       None),
    ("calc",    "Waste sent to elimination", "metric T", None,                   "waste_elimination"),
    ("calc",    "Recovery rate",             "%",        None,                   "waste_recov_pct"),
]

def _fmt(v, unit):
    if v is None: return "—"
    try: fv=float(v)
    except: return str(v)
    if fv==0: return "—"
    if unit in ("%",): return f"{fv:.1f}%"
    if unit in ("T.CO2/T","m3/T","GJ/T"): return f"{fv:.3f}"
    return f"{fv:,.0f}"

def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method=="OPTIONS": return func.HttpResponse(status_code=204,headers=CORS)
    try:
        company  = req.params.get("company","VerdaTyres Corp")
        sel_year = int(req.params.get("year",2023))

        years = get_company_years(company)
        if not years:
            return func.HttpResponse(json.dumps({
                "error":f"No data for {company}. Run build_esg_master.py.",
                "rows":[],"all_years":[],"available_years":[sel_year],
            }), mimetype="application/json", headers=CORS)

        series    = get_historical_series(company, min(years), max(years))
        all_years = [e["year"] for e in series]

        # Build per-year merged data (raw inputs + calculated KPIs)
        by_year = {}
        for e in series:
            k = calculate_all_kpis(e)
            # also add pct_certified_pct for % certified sites
            iso_total = int(e.get("total_sites",0) or 0)
            iso_cert  = int(e.get("iso_sites",0) or 0)
            k["pct_certified_pct"] = round(iso_cert/max(1,iso_total)*100,1) if iso_total>0 else 0
            by_year[e["year"]] = {**e, **k}

        rows = []
        for rtype,label,unit,raw_field,calc_key in TEMPLATE_ROWS:
            if rtype=="section":
                rows.append({"section":True,"label":label,"unit":"","type":"section","values":{},"yoy":"—"})
                continue
            values = {}
            for yr in all_years:
                d = by_year.get(yr,{})
                v = d.get(raw_field) if raw_field else d.get(calc_key)
                values[str(yr)] = _fmt(v, unit)
            # YoY
            yoy="—"
            if len(all_years)>=2:
                field=raw_field or calc_key
                try:
                    vl=float(by_year.get(all_years[-1],{}).get(field) or 0)
                    vp=float(by_year.get(all_years[-2],{}).get(field) or 0)
                    if vp: yoy=f"{(vl-vp)/abs(vp)*100:+.1f}%"
                except: pass
            rows.append({"section":False,"label":label,"unit":unit or "","type":rtype,"values":values,"yoy":yoy})

        return func.HttpResponse(json.dumps({
            "company":company,"selected_year":sel_year,
            "available_years":sorted(set(list(years)+[sel_year])),
            "next_year":max(years)+1,
            "all_years":all_years,"rows":rows,
            "verification_status":get_verification_status(company,sel_year),
        },default=str), mimetype="application/json", headers=CORS)
    except Exception as ex:
        import traceback
        return func.HttpResponse(json.dumps({"error":str(ex),"trace":traceback.format_exc()}),
            status_code=500,mimetype="application/json",headers=CORS)