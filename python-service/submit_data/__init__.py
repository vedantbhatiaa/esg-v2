import azure.functions as func
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.calculations import calculate_all_kpis, calculate_yoy_all
from shared.verification import check_yoy_flags, get_submission_status
from shared.data_loader   import save_submission, get_prior_year_kpis

CORS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=CORS)

    try:
        body       = req.get_json()
        company_id = body["company_id"]
        year       = int(body["year"])
        form_data  = body["data"]          # merged 6-step wizard payload

        # Calculate all KPIs using original logic
        kpis = calculate_all_kpis(form_data)

        # Store raw ISO values for logical checks
        kpis["_raw_iso_total"]     = int(form_data.get("iso_total_sites", 0))
        kpis["_raw_iso_certified"] = int(form_data.get("iso_certified_sites", 0))

        # Get prior year for YoY comparison
        prior_kpis = get_prior_year_kpis(company_id, year) or {}
        yoy        = calculate_yoy_all(kpis, prior_kpis)
        flags      = check_yoy_flags(kpis, prior_kpis)
        status     = get_submission_status(flags)

        # Persist to local JSON store (swap for Azure SQL later)
        submission = {
            "company_id": company_id,
            "year":       year,
            "raw_data":   form_data,
            "kpis":       kpis,
            "yoy":        yoy,
            "flags":      flags,
            "status":     status,
        }
        saved = save_submission(submission)

        return func.HttpResponse(
            json.dumps({**saved, "message": "Submission saved successfully"}),
            mimetype="application/json",
            status_code=200,
            headers=CORS,
        )

    except KeyError as e:
        return func.HttpResponse(
            json.dumps({"error": f"Missing required field: {e}"}),
            mimetype="application/json", status_code=400, headers=CORS,
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json", status_code=500, headers=CORS,
        )
