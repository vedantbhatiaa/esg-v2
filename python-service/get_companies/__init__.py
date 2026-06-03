import azure.functions as func
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.data_loader import get_all_companies, get_submissions

CORS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=CORS)

    try:
        year = req.params.get("year")
        companies = get_all_companies()

        # Enrich each company with submission status for the requested year
        if year:
            year_int = int(year)
            subs = get_submissions(year=year_int)
            sub_map = {s["company_id"]: s for s in subs}
            for co in companies:
                sub = sub_map.get(co["id"])
                if sub:
                    co["submission_status"] = sub.get("status", "unknown")
                    co["submitted_at"]       = sub.get("submitted_at")
                    co["flag_count"]         = len(sub.get("flags", []))
                    co["error_count"]        = sum(1 for f in sub.get("flags", []) if f["severity"] == "error")
                    co["warning_count"]      = sum(1 for f in sub.get("flags", []) if f["severity"] == "warning")
                else:
                    co["submission_status"] = "pending"
                    co["submitted_at"]      = None
                    co["flag_count"]        = 0

        return func.HttpResponse(
            json.dumps(companies),
            mimetype="application/json",
            status_code=200,
            headers=CORS,
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json", status_code=500, headers=CORS,
        )
