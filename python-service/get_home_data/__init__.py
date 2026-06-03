import azure.functions as func
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.data_loader import (
    get_historical_series, get_sector_series, get_verification_status,
    get_company_years, get_submission
)
from shared.calculations import calculate_all_kpis, calculate_yoy_change

CORS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=CORS)
    try:
        company = req.params.get("company", "VerdaTyres Corp")
        year    = int(req.params.get("year", 2023))

        # KPI cards — current vs previous year
        cur  = get_submission(company, year)
        prev = get_submission(company, year - 1)
        cur_kpis  = calculate_all_kpis(cur  or {})
        prev_kpis = calculate_all_kpis(prev or {})

        kpi_fields = [
            "total_co2_t","co2_kpi","energy_kpi","renewable_share_pct",
            "water_kpi","total_water_m3","waste_recovery_pct","iso_certified_pct",
        ]
        kpis, yoy = {}, {}
        for f in kpi_fields:
            kpis[f] = cur_kpis.get(f, 0)
            delta    = calculate_yoy_change(cur_kpis.get(f, 0), prev_kpis.get(f, 0))
            yoy[f]   = delta["pct"]

        # Chart data — full company history
        years     = get_company_years(company)
        yr_series = get_historical_series(company, min(years or [2009]), max(years or [year]))

        # Build chart arrays
        chart_years  = [e["year"] for e in yr_series]
        scope1       = [e.get("scope1_co2_t", 0) / 1e6 for e in yr_series]
        scope2       = [e.get("scope2_co2_t", 0) / 1e6 for e in yr_series]
        co2_kpi_arr  = [e.get("co2_kpi", 0)         for e in yr_series]
        energy_arr   = [e.get("energy_kpi", 0)       for e in yr_series]
        water_m3     = [e.get("total_water_m3", 0)   for e in yr_series]
        water_kpi_arr= [e.get("water_kpi") if (e.get("water_kpi") or 0) < 50 else None for e in yr_series]
        waste_pct    = [e.get("waste_recovery_pct", 0) for e in yr_series]
        renew_pct    = [e.get("renewable_share_pct", 0) for e in yr_series]
        nonrenew_elec= [e.get("total_elec_gj", 0) - e.get("renew_elec_gj", 0) for e in yr_series]
        nat_gas_arr  = [e.get("total_fossil_gj", 0) for e in yr_series]

        # Submission status
        verif_status = get_verification_status(company, year)
        sections_done = sum([
            bool(cur_kpis.get("iso_certified_pct", 0)),
            bool(cur_kpis.get("production_t", 0)),
            bool(cur_kpis.get("total_water_m3", 0)),
            bool(cur_kpis.get("total_energy_gj", 0)),
            bool(cur_kpis.get("total_co2_t", 0)),
            bool(cur_kpis.get("total_waste_t", 0)),
        ])

        result = {
            "company": company, "year": year,
            "available_years": years,
            "next_year": max(years) + 1 if years else year + 1,
            "kpis": kpis, "yoy": yoy,
            "submission_status": {
                "sections_done": sections_done,
                "total_sections": 6,
                "verification": verif_status,
            },
            "charts": {
                "years": chart_years,
                "scope1_mt": scope1,
                "scope2_mt": scope2,
                "co2_kpi":   co2_kpi_arr,
                "energy_kpi": energy_arr,
                "water_m3":  water_m3,
                "water_kpi": water_kpi_arr,
                "waste_recovery_pct": waste_pct,
                "renewable_pct": renew_pct,
                "nonrenew_elec_gj": nonrenew_elec,
                "nat_gas_gj": nat_gas_arr,
            },
        }
        return func.HttpResponse(json.dumps(result), mimetype="application/json", headers=CORS)
    except Exception as ex:
        return func.HttpResponse(json.dumps({"error": str(ex)}), status_code=500,
                                 mimetype="application/json", headers=CORS)
