import azure.functions as func
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.data_loader  import get_benchmarks, get_company_year_data, get_years, load_master
from shared.calculations import calculate_all_kpis

CORS = {"Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"}

def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=CORS)
    try:
        year       = int(req.params.get("year", 2023))
        company    = req.params.get("company")
        benchmarks = get_benchmarks(year)

        my_kpis = None
        if company:
            df  = load_master()
            raw = get_company_year_data(company, year, df)
            if raw:
                my_kpis = calculate_all_kpis({**raw, "company": company, "year": year})

        # Company trend (all years) for benchmarking charts
        company_trend = {}
        if company:
            df    = load_master()
            years = get_years(company, df)
            for y in years:
                raw = get_company_year_data(company, y, df)
                if raw:
                    kpis = calculate_all_kpis({**raw, "company": company, "year": y})
                    rt   = max(float(raw.get("renew_elec_purchased", 0)) +
                               float(raw.get("nonrenew_elec_purchased", 0)) +
                               float(raw.get("self_gen_elec", 0)), 1)
                    company_trend[y] = {
                        "co2_kpi":    kpis.get("co2_kpi"),
                        "energy_kpi": kpis.get("energy_kpi"),
                        "water_kpi":  kpis.get("water_kpi"),
                        "waste_pct":  kpis.get("waste_recovery_pct", 0) * 100,
                        "renew_pct":  float(raw.get("renew_elec_purchased", 0)) / rt * 100,
                        "scope1":     kpis.get("total_co2_scope1"),
                        "scope2":     kpis.get("total_co2_scope2"),
                        "nat_gas":    float(raw.get("nat_gas", 0)),
                        "coal":       float(raw.get("coal_sub", 0)),
                        "diesel":     float(raw.get("diesel", 0)),
                        "biomass":    float(raw.get("biomass", 0)),
                        "renew_gj":   float(raw.get("renew_elec_purchased", 0)),
                        "nonrenew_gj":float(raw.get("nonrenew_elec_purchased", 0)),
                        "water_m3":   float(raw.get("water_withdrawals", 0)),
                        "waste_total":float(raw.get("waste_total", 0)),
                        "waste_rec":  float(raw.get("waste_recovery", 0)),
                    }

        return func.HttpResponse(
            json.dumps({**benchmarks, "my_kpis": my_kpis, "company_trend": company_trend}),
            mimetype="application/json", status_code=200, headers=CORS)
    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}),
            mimetype="application/json", status_code=500, headers=CORS)