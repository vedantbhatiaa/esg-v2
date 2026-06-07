"""
data_loader.py — TIP ESG Platform V2
Uses EXACTLY the same field names as the Streamlit TemplateInputs / formula_engine.py.
CSV column → field mapping matches Streamlit data_loader.py WIDE_COL_TO_FIELD exactly.
"""
import os, csv, glob, statistics
from pathlib import Path
from datetime import datetime

_HERE     = Path(__file__).resolve().parent.parent
_DATA_DIR = _HERE.parent / "data_storage"
_MASTER_GLOB = str(_DATA_DIR / "master" / "ESG_MASTER_WIDE_ALL_COMPANIES_*.csv")
_VERIF_CSV   = _DATA_DIR / "verifications.csv"

_COMPANIES = [
    {"id":"verdatyres",   "name":"VerdaTyres Corp",  "email":"verdatyres@tip-reporting.com",   "role":"client"},
    {"id":"alphatread",   "name":"AlphaTread Ltd",   "email":"alphatread@tip-reporting.com",   "role":"client"},
    {"id":"betarubber",   "name":"BetaRubber Inc",   "email":"betarubber@tip-reporting.com",   "role":"client"},
    {"id":"gammatire",    "name":"GammaTire SA",     "email":"gammatire@tip-reporting.com",    "role":"client"},
    {"id":"deltagrip",    "name":"DeltaGrip GmbH",  "email":"deltagrip@tip-reporting.com",    "role":"client"},
    {"id":"epsilonwheel", "name":"EpsilonWheel Co",  "email":"epsilonwheel@tip-reporting.com", "role":"client"},
    {"id":"zetatrac",     "name":"ZetaTrac LLC",     "email":"zetatrac@tip-reporting.com",     "role":"client"},
    {"id":"etaroad",      "name":"EtaRoad AG",       "email":"etaroad@tip-reporting.com",      "role":"client"},
    {"id":"thetadrive",   "name":"ThetaDrive NV",    "email":"thetadrive@tip-reporting.com",   "role":"client"},
    {"id":"iotatire",     "name":"IotaTire PLC",     "email":"iotatire@tip-reporting.com",     "role":"client"},
    {"id":"dss_analyst",  "name":"dss+ Analyst",     "email":"employee@consultdss.com",        "role":"dss"},
]

# CSV column → Streamlit TemplateInputs field name (exact match)
_COL_MAP = {
    "Total no. of sites":                              "total_sites",
    "ISO 14001 sites":                                 "iso_sites",
    "Production":                                      "production",
    "Water intake":                                    "water_withdrawals",
    "Renewable Electricity Purchased":                 "renew_elec_purchased",
    "Non-Renewable Electricity Purchased":             "nonrenew_elec_purchased",
    "Self-generated AND consumed electricity on-site": "self_gen_elec",
    "Purchased Steam":                                 "purchased_steam",
    "Sold Electricity":                                "sold_electricity",
    "Sold Steam":                                      "sold_steam",
    "Natural Gas":                                     "nat_gas",
    "Coal":                                            "coal_sub",
    "Propane":                                         "propane",
    "Fuel Oil":                                        "fuel_oil_heavy_a",
    "Diesel":                                          "diesel",
    "Petrol":                                          "petrol",
    "Biomass":                                         "biomass",
    "Waste tires":                                     "waste_tires_mt",
    "LPG":                                             "lpg",
    "Other":                                           "other_fuels",
    "Total amount of waste":                           "waste_total",
    "Total Waste":                                     "waste_total",
    "Waste Recovered":                                 "waste_recovery",
    "Amount of waste sent to recovery":                "waste_recovery",
    # Electricity by country (GJ)
    "Elec_Canada_GJ":  "elec_canada_gj",
    "Elec_Chile_GJ":  "elec_chile_gj",
    "Elec_Mexico_GJ":  "elec_mexico_gj",
    "Elec_United_States_GJ":  "elec_united_states_gj",
    "Elec_Australia_GJ":  "elec_australia_gj",
    "Elec_Japan_GJ":  "elec_japan_gj",
    "Elec_Korea_GJ":  "elec_korea_gj",
    "Elec_New_Zealand_GJ":  "elec_new_zealand_gj",
    "Elec_Austria_GJ":  "elec_austria_gj",
    "Elec_Belgium_GJ":  "elec_belgium_gj",
    "Elec_Czech_Republic_GJ":  "elec_czech_republic_gj",
    "Elec_Denmark_GJ":  "elec_denmark_gj",
    "Elec_Finland_GJ":  "elec_finland_gj",
    "Elec_France_GJ":  "elec_france_gj",
    "Elec_Germany_GJ":  "elec_germany_gj",
    "Elec_Hungary_GJ":  "elec_hungary_gj",
    "Elec_Iceland_GJ":  "elec_iceland_gj",
    "Elec_Ireland_GJ":  "elec_ireland_gj",
    "Elec_Italy_GJ":  "elec_italy_gj",
    "Elec_Luxembourg_GJ":  "elec_luxembourg_gj",
    "Elec_Netherlands_GJ":  "elec_netherlands_gj",
    "Elec_Norway_GJ":  "elec_norway_gj",
    "Elec_Poland_GJ":  "elec_poland_gj",
    "Elec_Portugal_GJ":  "elec_portugal_gj",
    "Elec_Spain_GJ":  "elec_spain_gj",
    "Elec_Sweden_GJ":  "elec_sweden_gj",
    "Elec_Switzerland_GJ":  "elec_switzerland_gj",
    "Elec_Turkey_GJ":  "elec_turkey_gj",
    "Elec_United_Kingdom_GJ":  "elec_united_kingdom_gj",
    "Elec_China_GJ":  "elec_china_gj",
    "Elec_India_GJ":  "elec_india_gj",
    # Pre-computed from CSV
    "Total energy":           "_total_energy",
    "Total energy - KPI":     "_energy_kpi",
    "Total CO2 - Scope 1":    "_scope1",
    "Total CO2 - Scope 2":    "_scope2",
    "Total CO2":              "_total_co2",
    "Total CO2 - KPI":        "_co2_kpi",
    "Water intake - KPI":     "_water_kpi",
    "% certified sites":      "_iso_pct",
    "Total Electricity":      "_total_elec",
    "Renewable_Electricity_Share_%": "_renew_share_pct",
    "Waste_Recovery_Rate_%":  "_waste_recov_pct",
    "ISO_Certification_%":    "_iso_cert_pct",
}

_INPUT_FIELDS = {
    "total_sites","iso_sites","production","water_withdrawals",
    "renew_elec_purchased","nonrenew_elec_purchased","self_gen_elec",
    "purchased_steam","sold_electricity","sold_steam",
    "nat_gas","coal_sub","propane","fuel_oil_heavy_a",
    "diesel","petrol","biomass","waste_tires_mt","lpg","other_fuels",
    "co2_scope2_steam","waste_total","waste_recovery",
}

def _num(v, d=0.0):
    try: return float(str(v).replace(",","").strip()) if v not in (None,"","—","N/A") else d
    except: return d

def _int(v, d=0):
    try: return int(float(str(v).strip())) if v not in (None,"") else d
    except: return d

def _load_master():
    files = sorted(glob.glob(_MASTER_GLOB), key=os.path.getmtime, reverse=True)
    for fpath in files:
        try:
            rows = []
            with open(fpath, newline="", encoding="utf-8-sig") as f:
                for r in csv.DictReader(f):
                    rows.append(r)
            if rows: return rows
        except Exception: pass
    return []

def _row_to_canonical(raw):
    out = {"company": raw.get("Company",""), "year": _int(raw.get("Year",0))}
    for csv_col, field in _COL_MAP.items():
        if csv_col in raw:
            out[field] = _num(raw[csv_col])
    return out

def _all_rows():
    return [_row_to_canonical(r) for r in _load_master()]

def get_all_companies(): return _COMPANIES

def authenticate(email, password):
    if password != "demo1234": return None
    el = email.strip().lower()
    for c in _COMPANIES:
        if c["email"].lower() == el: return c
    return None

def id_to_name(cid):
    for c in _COMPANIES:
        if c["id"].lower() == (cid or "").lower(): return c["name"]
    return cid or ""

def name_to_id(name):
    for c in _COMPANIES:
        if c["name"].lower() == (name or "").lower(): return c["id"]
    return (name or "").lower().replace(" ","_")

def get_company_years(company_name):
    rows = _all_rows()
    return sorted({r["year"] for r in rows if r["company"]==company_name and r["year"]>0})

def get_submission(company_name, year):
    for r in _all_rows():
        if r["company"]==company_name and r["year"]==year: return r
    return None

def get_historical_series(company_name, year_from=2009, year_to=2030):
    rows = [r for r in _all_rows() if r["company"]==company_name and year_from<=r["year"]<=year_to]
    return sorted(rows, key=lambda r: r["year"])

def get_sector_series(year_from=2009, year_to=2030):
    by_year = {}
    for r in _all_rows():
        yr = r["year"]
        if year_from<=yr<=year_to: by_year.setdefault(yr,[]).append(r)
    result = []
    for yr in sorted(by_year):
        entries = by_year[yr]
        entry = {"year":yr, "n":len(entries)}
        for f in ["_total_energy","_energy_kpi","_co2_kpi","_water_kpi","_scope1","_scope2",
                  "_total_co2","_renew_share_pct","_waste_recov_pct","production","water_withdrawals"]:
            vals = [e[f] for e in entries if e.get(f) and e[f]>0]
            entry[f] = round(sum(vals)/len(vals),4) if vals else 0
        result.append(entry)
    return result

def get_sector_quartiles(year):
    yr_rows = [r for r in _all_rows() if r["year"]==year]
    result = {}
    for f in ["_co2_kpi","_energy_kpi","_water_kpi","_renew_share_pct","_waste_recov_pct"]:
        vals = sorted([r[f] for r in yr_rows if r.get(f) and r[f]>0])
        if len(vals)>=2:
            n=len(vals)
            result[f] = {
                "q10":round(vals[max(0,int(n*.1))],4),
                "q25":round(vals[max(0,int(n*.25))],4),
                "median":round(statistics.median(vals),4),
                "q75":round(vals[min(n-1,int(n*.75))],4),
                "q90":round(vals[min(n-1,int(n*.9))],4), "n":n,
            }
    return result

def get_verification_status(company_name, year):
    if not _VERIF_CSV.exists(): return "Pending"
    try:
        with open(_VERIF_CSV,newline="") as f:
            for row in csv.DictReader(f):
                if row.get("Company","").strip()==company_name and str(row.get("Year","")).strip()==str(year):
                    return row.get("Status","Pending")
    except: pass
    return "Pending"

def set_verification_status(company_name, year, status):
    rows = []
    if _VERIF_CSV.exists():
        try:
            with open(_VERIF_CSV,newline="") as f:
                for row in csv.DictReader(f):
                    if not (row.get("Company","").strip()==company_name and str(row.get("Year","")).strip()==str(year)):
                        rows.append(row)
        except: pass
    rows.append({"Company":company_name,"Year":str(year),"Status":status,"UpdatedAt":datetime.utcnow().isoformat()})
    _VERIF_CSV.parent.mkdir(parents=True,exist_ok=True)
    with open(_VERIF_CSV,"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["Company","Year","Status","UpdatedAt"]); w.writeheader(); w.writerows(rows)

def save_submission(company_name, year, data):
    """data uses Streamlit TemplateInputs field names."""
    try:
        import pandas as pd
        from .calculations import calculate_all_kpis
        kpis = calculate_all_kpis(data)
        wt_gj = data.get("waste_tires_mt",0) * 36.23  # metric T → GJ
        new_row = {
            "Company":company_name,"Year":year,
            "Total no. of sites":int(data.get("total_sites",0)),
            "ISO 14001 sites":int(data.get("iso_sites",0)),
            "% certified sites":round(int(data.get("iso_sites",0))/max(1,int(data.get("total_sites",1))),4),
            "Production":data.get("production",0),
            "Water intake":data.get("water_withdrawals",0),
            "Water intake - KPI":kpis.get("water_kpi",0),
            "Total Electricity":kpis.get("total_electricity",0),
            "Renewable Electricity Purchased":data.get("renew_elec_purchased",0),
            "Non-Renewable Electricity Purchased":data.get("nonrenew_elec_purchased",0),
            "Self-generated AND consumed electricity on-site":data.get("self_gen_elec",0),
            "Purchased Steam":data.get("purchased_steam",0),
            "Sold Electricity":data.get("sold_electricity",0),
            "Sold Steam":data.get("sold_steam",0),
            "Natural Gas":data.get("nat_gas",0),
            "Coal":data.get("coal_sub",0),
            "Propane":data.get("propane",0),
            "Fuel Oil":data.get("fuel_oil_heavy_a",0),
            "Diesel":data.get("diesel",0),
            "Petrol":data.get("petrol",0),
            "Biomass":data.get("biomass",0),
            "Waste tires":wt_gj,
            "LPG":data.get("lpg",0),
            "Other":data.get("other_fuels",0),
            "Total energy":kpis.get("total_energy",0),
            "Total energy - KPI":kpis.get("energy_kpi",0),
            "Total CO2 - Scope 1":kpis.get("scope1",0),
            "Total CO2 - Scope 2":kpis.get("scope2",0),
            "Total CO2":kpis.get("total_co2",0),
            "Total CO2 - KPI":kpis.get("co2_kpi",0),
            "Total Waste":data.get("waste_total",0),
            "Waste Recovered":data.get("waste_recovery",0),
            "Recovery Rate":kpis.get("waste_recov_pct",0)/100,
            "Renewable_Electricity_Share_%":kpis.get("renew_share_pct",0),
            "ISO_Certification_%":kpis.get("iso_pct",0),
            "Waste_Recovery_Rate_%":kpis.get("waste_recov_pct",0),
        }
        files=sorted(glob.glob(_MASTER_GLOB),key=os.path.getmtime,reverse=True)
        df=pd.read_csv(files[0]) if files else pd.DataFrame()
        if not df.empty and "Company" in df.columns:
            df=df[~((df["Company"]==company_name)&(df["Year"]==year))]
        combined=pd.concat([df,pd.DataFrame([new_row])],ignore_index=True)
        combined=combined.sort_values(["Company","Year"]).reset_index(drop=True)
        yr_min=int(combined["Year"].min()); yr_max=int(combined["Year"].max())
        save_path=_DATA_DIR/"master"/f"ESG_MASTER_WIDE_ALL_COMPANIES_{yr_min}_{yr_max}.csv"
        save_path.parent.mkdir(parents=True,exist_ok=True)
        combined.to_csv(save_path,index=False)
        return {"saved":True,"n_records":len(combined),"kpis":kpis}
    except Exception as e:
        return {"saved":False,"error":str(e)}

def get_prior_year_kpis(company_name, year):
    row=get_submission(company_name,year-1)
    if not row: return {}
    from .calculations import calculate_all_kpis
    return calculate_all_kpis(row)