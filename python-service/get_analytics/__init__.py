import azure.functions as func
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.data_loader import get_historical_kpi_series, get_all_companies, get_submissions

CORS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

ALL_KPIS = [
    "energy_kpi", "co2_kpi", "water_kpi",
    "renewable_share_pct", "waste_recovery_pct",
    "total_co2_t", "total_energy_gj", "total_water_m3",
    "scope1_co2_t", "scope2_co2_t",
]


def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=CORS)

    try:
        company_id = req.params.get("company_id")     # None = sector average
        year_from  = int(req.params.get("year_from", 2009))
        year_to    = int(req.params.get("year_to",   2023))
        years      = list(range(year_from, year_to + 1))

        result = {"years": years, "series": {}}

        for kpi in ALL_KPIS:
            if company_id:
                result["series"][kpi] = get_historical_kpi_series(company_id, kpi, years)
            else:
                # Sector average — average across all companies
                companies = get_all_companies()
                company_series = [
                    get_historical_kpi_series(co["id"], kpi, years)
                    for co in companies
                ]
                # Average per year
                avg_series = []
                for i, yr in enumerate(years):
                    vals = [s[i]["value"] for s in company_series if s[i]["value"] is not None]
                    avg_series.append({
                        "year":  yr,
                        "value": round(sum(vals) / len(vals), 3) if vals else None,
                    })
                result["series"][kpi] = avg_series

        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200,
            headers=CORS,
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json", status_code=500, headers=CORS,
        )
