import azure.functions as func
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.data_loader import get_historical_series, get_company_years, get_submission, get_verification_status
from shared.calculations import calculate_all_kpis

CORS = {"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"GET,OPTIONS","Access-Control-Allow-Headers":"Content-Type"}

def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=CORS)
    try:
        company = req.params.get("company","VerdaTyres Corp")
        year    = req.params.get("year")

        years = get_company_years(company)
        if not years:
            return func.HttpResponse(
                json.dumps({"error": f"No data for {company}"}),
                status_code=404, mimetype="application/json", headers=CORS)

        # If specific year requested, return just that year's data
        if year:
            yr = int(year)
            raw = get_submission(company, yr) or {}
            kpis = calculate_all_kpis(raw)

            # Compute renew share
            rt = max(
                (raw.get("renew_elec_purchased") or 0) +
                (raw.get("nonrenew_elec_purchased") or 0) +
                (raw.get("self_gen_elec") or 0), 1)
            renew_pct = (raw.get("renew_elec_purchased") or 0) / rt * 100

            # Add aliases so CompanyData TABLE_DEF works
            # TABLE_DEF uses: total_co2_scope1, total_co2_scope2, total_co2_t,
            #                 total_energy_gj, iso_certified_pct, waste_recovery_pct (as %)
            kpis_out = {
                **kpis,
                # Aliases for old field names CompanyData.vue uses
                "total_co2_scope1":   kpis.get("scope1", 0),
                "total_co2_scope2":   kpis.get("scope2", 0),
                "total_co2_t":        kpis.get("total_co2", 0),
                "total_energy_gj":    kpis.get("total_energy", 0),
                "iso_certified_pct":  round(kpis.get("pct_certified", 0) * 100, 1),
                "renewable_share_pct":renew_pct,
                "waste_recovery_pct": kpis.get("waste_recov_pct", 0),
                # Reports.vue uses these from kpi object
                "co2_kpi":            kpis.get("co2_kpi", 0),
                "energy_kpi":         kpis.get("energy_kpi", 0),
                "water_kpi":          kpis.get("water_kpi", 0),
            }

            return func.HttpResponse(json.dumps({
                "company": company,
                "year": yr,
                "available_years": years,
                "raw": raw,        # Streamlit field names: production, nat_gas, etc.
                "kpis": kpis_out,
                "verification_status": get_verification_status(company, yr),
            }, default=str), mimetype="application/json", headers=CORS)

        # No specific year: return summary for all years (for table building)
        series = get_historical_series(company, min(years), max(years))
        summary = []
        for e in series:
            k = calculate_all_kpis(e)
            rt = max(
                (e.get("renew_elec_purchased") or 0) +
                (e.get("nonrenew_elec_purchased") or 0) +
                (e.get("self_gen_elec") or 0), 1)
            renew_pct = (e.get("renew_elec_purchased") or 0) / rt * 100
            summary.append({
                "year": e["year"],
                "raw":  e,
                "kpis": {
                    **k,
                    "total_co2_scope1":   k.get("scope1", 0),
                    "total_co2_scope2":   k.get("scope2", 0),
                    "total_co2_t":        k.get("total_co2", 0),
                    "total_energy_gj":    k.get("total_energy", 0),
                    "iso_certified_pct":  k.get("pct_certified", 0),
                    "renewable_share_pct":renew_pct,
                    "waste_recovery_pct": k.get("waste_recov_pct", 0),
                },
            })

        return func.HttpResponse(json.dumps({
            "company": company,
            "years": years,
            "summary": summary,
        }, default=str), mimetype="application/json", headers=CORS)

    except Exception as ex:
        import traceback
        return func.HttpResponse(
            json.dumps({"error": str(ex), "trace": traceback.format_exc()}),
            status_code=500, mimetype="application/json", headers=CORS)