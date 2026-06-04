import azure.functions as func
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.data_loader import set_verification_status, get_verification_status

CORS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=CORS)
    try:
        body    = req.get_json()
        company = body.get("company", "")
        year    = int(body.get("year", 2023))
        status  = body.get("status", "Pending")  # Verified | Pending | Flagged

        if not company:
            return func.HttpResponse(
                json.dumps({"error": "company required"}),
                status_code=400, mimetype="application/json", headers=CORS)

        valid_statuses = {"Verified", "Pending", "Flagged"}
        if status not in valid_statuses:
            return func.HttpResponse(
                json.dumps({"error": f"status must be one of {valid_statuses}"}),
                status_code=400, mimetype="application/json", headers=CORS)

        set_verification_status(company, year, status)
        current = get_verification_status(company, year)

        return func.HttpResponse(
            json.dumps({"ok": True, "company": company, "year": year, "status": current}),
            mimetype="application/json", status_code=200, headers=CORS)

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500, mimetype="application/json", headers=CORS)