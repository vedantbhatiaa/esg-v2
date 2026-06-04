import azure.functions as func
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.data_loader import get_historical_series, get_company_years, get_submission, get_verification_status
from shared.calculations import calculate_all_kpis

CORS = {"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"GET,OPTIONS","Access-Control-Allow-Headers":"Content-Type"}

def _yoy(cur, prev):
    if not prev or prev==0: return None
    return round(((cur-prev)/abs(prev))*100,1)

def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method=="OPTIONS": return func.HttpResponse(status_code=204,headers=CORS)
    try:
        company = req.params.get("company","VerdaTyres Corp")
        year    = int(req.params.get("year",2023))

        years = get_company_years(company)
        if not years:
            return func.HttpResponse(json.dumps({"error":f"No data for {company}"}),
                status_code=404, mimetype="application/json", headers=CORS)

        if year not in years: year = max(years)

        series = get_historical_series(company, min(years), max(years))
        cur = next((e for e in series if e["year"]==year), None)
        prv = next((e for e in series if e["year"]==year-1), None)

        if not cur:
            cur = {"year":year}

        # Recalculate KPIs from raw inputs (matches Streamlit exactly)
        kpis     = calculate_all_kpis(cur)
        kpis_prv = calculate_all_kpis(prv) if prv else {}

        # Compute renew_share from raw inputs
        rt = max((cur.get("renew_elec_purchased",0) or 0) +
                 (cur.get("nonrenew_elec_purchased",0) or 0) +
                 (cur.get("self_gen_elec",0) or 0), 1)
        renew_pct = (cur.get("renew_elec_purchased",0) or 0) / rt * 100

        rt_prv = max((prv.get("renew_elec_purchased",0) or 0) +
                     (prv.get("nonrenew_elec_purchased",0) or 0) +
                     (prv.get("self_gen_elec",0) or 0), 1) if prv else 1
        renew_pct_prv = (prv.get("renew_elec_purchased",0) or 0) / rt_prv * 100 if prv else 0

        # 8 KPI cards matching Streamlit page_home exactly
        kpi_cards = {
            "co2_abs":        kpis.get("total_co2",0),
            "co2_kpi":        kpis.get("co2_kpi",0),
            "energy_kpi":     kpis.get("energy_kpi",0),
            "renew_share_pct": renew_pct,
            "water_kpi":      kpis.get("water_kpi",0),
            "water_withdrawals": cur.get("water_withdrawals",0),
            "waste_recov_pct": kpis.get("waste_recov_pct",0),
            "iso_pct":        kpis.get("iso_pct",0),
        }
        yoy_cards = {
            "co2_abs":        _yoy(kpis.get("total_co2",0), kpis_prv.get("total_co2",0)),
            "co2_kpi":        _yoy(kpis.get("co2_kpi",0), kpis_prv.get("co2_kpi",0)),
            "energy_kpi":     _yoy(kpis.get("energy_kpi",0), kpis_prv.get("energy_kpi",0)),
            "renew_share_pct": _yoy(renew_pct, renew_pct_prv),
            "water_kpi":      _yoy(kpis.get("water_kpi",0), kpis_prv.get("water_kpi",0)),
            "water_withdrawals": None,
            "waste_recov_pct": _yoy(kpis.get("waste_recov_pct",0), kpis_prv.get("waste_recov_pct",0)),
            "iso_pct":        None,
        }

        # Chart series — per-year computed values (same as Streamlit yr_kpis)
        yr_kpis_list = []
        for e in series:
            ek = calculate_all_kpis(e)
            rt_e = max((e.get("renew_elec_purchased",0) or 0) +
                       (e.get("nonrenew_elec_purchased",0) or 0) +
                       (e.get("self_gen_elec",0) or 0), 1)
            yr_kpis_list.append({
                "year":          e["year"],
                "scope1":        ek.get("scope1",0),
                "scope2":        ek.get("scope2",0),
                "total_co2":     ek.get("total_co2",0),
                "co2_kpi":       ek.get("co2_kpi",0),
                "energy_kpi":    ek.get("energy_kpi",0),
                "water_kpi":     ek.get("water_kpi",0),
                "waste_pct":     ek.get("waste_recov_pct",0),
                "renew_pct":     (e.get("renew_elec_purchased",0) or 0)/rt_e*100,
                "nat_gas":       e.get("nat_gas",0) or 0,
                "coal":          e.get("coal_sub",0) or 0,
                "diesel":        e.get("diesel",0) or 0,
                "biomass":       e.get("biomass",0) or 0,
                "renew_elec":    e.get("renew_elec_purchased",0) or 0,
                "nonrenew_elec": e.get("nonrenew_elec_purchased",0) or 0,
                "water_m3":      e.get("water_withdrawals",0) or 0,
                "waste_total":   e.get("waste_total",0) or 0,
                "waste_recovery":e.get("waste_recovery",0) or 0,
                "production":    e.get("production",0) or 0,
            })

        # Submission status (match Streamlit logic)
        def _has(key): return (cur.get(key,0) or 0) >= 1
        section_done = [
            _has("total_sites"), _has("production"), _has("water_withdrawals"),
            _has("renew_elec_purchased") or _has("nonrenew_elec_purchased") or _has("nat_gas"),
            cur.get("co2_scope2_steam") is not None and _has("production"),
            _has("waste_total"),
        ]

        return func.HttpResponse(json.dumps({
            "company":      company,
            "year":         year,
            "available_years": years,
            "kpi_cards":    kpi_cards,
            "yoy":          yoy_cards,
            "yr_kpis":      yr_kpis_list,
            "submission_status": {
                "sections_done": sum(section_done),
                "total_sections": 6,
                "verification": get_verification_status(company, year),
            },
        }, default=str), mimetype="application/json", headers=CORS)
    except Exception as ex:
        import traceback
        return func.HttpResponse(json.dumps({"error":str(ex),"trace":traceback.format_exc()}),
            status_code=500, mimetype="application/json", headers=CORS)