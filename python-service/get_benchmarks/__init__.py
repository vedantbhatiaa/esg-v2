import azure.functions as func
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.data_loader import get_sector_quartiles, get_historical_series, get_company_years, get_verification_status

CORS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=CORS)
    try:
        year    = int(req.params.get("year", 2023))
        company = req.params.get("company", "")

        # Sector quartile bands for the year
        bands = get_sector_quartiles(year)

        # Company-specific KPI trend (all years)
        company_trend = {}
        my_kpis       = None

        if company:
            yrs = get_company_years(company)
            for y in yrs:
                series = get_historical_series(company, y, y)
                if series:
                    e = series[0]
                    company_trend[y] = {
                        "co2_kpi":      e.get("co2_kpi"),
                        "energy_kpi":   e.get("energy_kpi"),
                        "water_kpi":    e.get("water_kpi"),
                        "waste_pct":    e.get("waste_recovery_pct"),
                        "renew_pct":    e.get("renewable_share_pct"),
                        "scope1":       e.get("scope1_co2_t"),
                        "scope2":       e.get("scope2_co2_t"),
                        "renew_gj":     e.get("renew_elec_gj"),
                        "nonrenew_gj":  e.get("nonrenew_elec_gj"),
                        "nat_gas":      e.get("nat_gas_gj"),
                        "coal":         e.get("coal_gj"),
                        "diesel":       e.get("diesel_gj"),
                        "biomass":      e.get("biomass_gj"),
                        "water_m3":     e.get("total_water_m3"),
                        "waste_total":  e.get("waste_total_t"),
                        "waste_rec":    e.get("waste_recovered_t"),
                        "total_co2":    e.get("total_co2_t"),
                        "total_energy": e.get("total_energy_gj"),
                    }
                    if y == year:
                        my_kpis = {
                            "co2_kpi":            e.get("co2_kpi"),
                            "energy_kpi":         e.get("energy_kpi"),
                            "water_kpi":          e.get("water_kpi"),
                            "waste_recovery_pct": e.get("waste_recovery_pct"),
                            "renewable_share_pct":e.get("renewable_share_pct"),
                            "iso_certified_pct":  e.get("iso_certified_pct"),
                            "total_co2_t":        e.get("total_co2_t"),
                            "total_energy_gj":    e.get("total_energy_gj"),
                        }

        # Build scorecard (all companies for this year)
        from shared.data_loader import get_all_companies, get_historical_series as ghs
        scorecard = []
        for co in get_all_companies():
            s = ghs(co["name"], year, year)
            if s:
                e = s[0]
                scorecard.append({
                    "company":            co["name"],
                    "co2_kpi":            e.get("co2_kpi"),
                    "energy_kpi":         e.get("energy_kpi"),
                    "water_kpi":          e.get("water_kpi"),
                    "renew_pct":          e.get("renewable_share_pct"),
                    "waste_pct":          e.get("waste_recovery_pct"),
                    "verif_status":       get_verification_status(co["name"], year),
                })

        return func.HttpResponse(
            json.dumps({
                "year":          year,
                "bands":         bands,
                "scorecard":     scorecard,
                "my_kpis":       my_kpis,
                "company_trend": company_trend,
            }),
            mimetype="application/json", status_code=200, headers=CORS)

    except Exception as e:
        import traceback
        return func.HttpResponse(
            json.dumps({"error": str(e), "trace": traceback.format_exc()}),
            mimetype="application/json", status_code=500, headers=CORS)