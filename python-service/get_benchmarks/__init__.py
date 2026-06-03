import azure.functions as func
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.data_loader import get_sector_benchmarks, get_all_companies, get_submissions

CORS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=CORS)

    try:
        year       = int(req.params.get("year", 2023))
        company_id = req.params.get("company_id")

        benchmarks   = get_sector_benchmarks(year)
        all_companies = get_all_companies()
        submissions  = get_submissions(year=year)
        sub_map      = {s["company_id"]: s for s in submissions}

        # Build the scorecard — all companies with their KPIs
        scorecard = []
        for co in all_companies:
            sub = sub_map.get(co["id"])
            entry = {
                "company_id":   co["id"],
                "company_name": co["name"],
                "region":       co["region"],
                "submitted":    sub is not None,
            }
            if sub:
                kpis = sub.get("kpis", {})
                entry.update({
                    "energy_kpi":          kpis.get("energy_kpi"),
                    "co2_kpi":             kpis.get("co2_kpi"),
                    "water_kpi":           kpis.get("water_kpi"),
                    "renewable_share_pct": kpis.get("renewable_share_pct"),
                    "waste_recovery_pct":  kpis.get("waste_recovery_pct"),
                    "iso_certified_pct":   kpis.get("iso_certified_pct"),
                    "status":              sub.get("status"),
                })
            scorecard.append(entry)

        # My company's position vs bands (if requested)
        my_kpis = None
        if company_id and company_id in sub_map:
            my_kpis = sub_map[company_id].get("kpis", {})

        return func.HttpResponse(
            json.dumps({
                "year":       year,
                "bands":      benchmarks["kpis"],
                "scorecard":  scorecard,
                "my_kpis":    my_kpis,
            }),
            mimetype="application/json",
            status_code=200,
            headers=CORS,
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json", status_code=500, headers=CORS,
        )
