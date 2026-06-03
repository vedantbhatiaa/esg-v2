import azure.functions as func
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.calculations import calculate_all_kpis

CORS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Live KPI calculation — called as user fills in form steps.
    Does NOT save — just returns calculated values for the live sidebar.
    """
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=CORS)

    try:
        form_data = req.get_json()
        kpis = calculate_all_kpis(form_data)
        return func.HttpResponse(
            json.dumps(kpis),
            mimetype="application/json",
            status_code=200,
            headers=CORS,
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json", status_code=500, headers=CORS,
        )
