import azure.functions as func
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.data_loader import (
    get_historical_series, get_company_years,
    get_submission, get_verification_status
)

CORS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

def _yoy(cur, prev):
    if not prev or prev == 0:
        return None
    return round(((cur - prev) / abs(prev)) * 100, 1)

def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=CORS)
    try:
        company = req.params.get("company", "VerdaTyres Corp")
        year    = int(req.params.get("year", 2023))

        # ── Get full history, then pick current + previous year ───────────────
        years     = get_company_years(company)
        if not years:
            return func.HttpResponse(
                json.dumps({"error": f"No data found for {company}"}),
                status_code=404, mimetype="application/json", headers=CORS)

        # Use the requested year or the most recent available
        if year not in years:
            year = max(years)

        # Full series — pre-computed values from CSV
        yr_series = get_historical_series(company, min(years), max(years))

        # Find current and previous year entries
        cur_entry  = next((e for e in yr_series if e["year"] == year), None)
        prev_entry = next((e for e in yr_series if e["year"] == year - 1), None)

        if not cur_entry:
            cur_entry = {k: 0 for k in ["co2_kpi","energy_kpi","water_kpi",
                         "renewable_share_pct","waste_recovery_pct","iso_certified_pct",
                         "total_co2_t","total_water_m3","scope1_co2_t","scope2_co2_t",
                         "total_energy_gj","production_t"]}

        # ── KPI cards ─────────────────────────────────────────────────────────
        KPI_FIELDS = [
            "total_co2_t", "co2_kpi", "energy_kpi", "renewable_share_pct",
            "water_kpi", "total_water_m3", "waste_recovery_pct", "iso_certified_pct",
        ]
        kpis = {f: cur_entry.get(f, 0) for f in KPI_FIELDS}
        yoy  = {}
        for f in KPI_FIELDS:
            cur_v  = cur_entry.get(f, 0)  or 0
            prev_v = (prev_entry or {}).get(f, 0) or 0
            yoy[f] = _yoy(cur_v, prev_v)

        # ── Chart arrays ──────────────────────────────────────────────────────
        chart_years       = [e["year"]               for e in yr_series]
        scope1_mt         = [round((e.get("scope1_co2_t",0) or 0)/1e6, 4) for e in yr_series]
        scope2_mt         = [round((e.get("scope2_co2_t",0) or 0)/1e6, 4) for e in yr_series]
        co2_kpi_arr       = [e.get("co2_kpi", 0)           for e in yr_series]
        energy_kpi_arr    = [e.get("energy_kpi", 0)         for e in yr_series]
        water_m3          = [e.get("total_water_m3", 0)     for e in yr_series]
        water_kpi_arr     = [e.get("water_kpi", 0)          for e in yr_series]
        waste_pct_arr     = [e.get("waste_recovery_pct", 0) for e in yr_series]
        renew_pct_arr     = [e.get("renewable_share_pct", 0)for e in yr_series]
        renew_elec_arr    = [e.get("renew_elec_gj", 0)      for e in yr_series]
        nonrenew_elec_arr = [e.get("nonrenew_elec_gj", 0)   for e in yr_series]
        nat_gas_arr       = [e.get("nat_gas_gj", 0)         for e in yr_series]
        coal_arr          = [e.get("coal_gj", 0)            for e in yr_series]
        diesel_arr        = [e.get("diesel_gj", 0)          for e in yr_series]
        biomass_arr       = [e.get("biomass_gj", 0)         for e in yr_series]
        total_co2_arr     = [e.get("total_co2_t", 0)        for e in yr_series]
        production_arr    = [e.get("production_t", 0)       for e in yr_series]
        energy_arr        = [e.get("total_energy_gj", 0)    for e in yr_series]

        # ── Submission status ─────────────────────────────────────────────────
        verif_status  = get_verification_status(company, year)
        sections_done = sum([
            1 if (cur_entry.get("iso_certified_pct") or 0) > 0 else 0,
            1 if (cur_entry.get("production_t")       or 0) > 0 else 0,
            1 if (cur_entry.get("total_water_m3")     or 0) > 0 else 0,
            1 if (cur_entry.get("total_energy_gj")    or 0) > 0 else 0,
            1 if (cur_entry.get("total_co2_t")        or 0) > 0 else 0,
            1 if (cur_entry.get("waste_total_t")      or 0) > 0 else 0,
        ])

        result = {
            "company":         company,
            "year":            year,
            "available_years": years,
            "next_year":       max(years) + 1,
            "kpis":            kpis,
            "yoy":             yoy,
            "submission_status": {
                "sections_done":  sections_done,
                "total_sections": 6,
                "verification":   verif_status,
            },
            "charts": {
                "years":              chart_years,
                "scope1_mt":          scope1_mt,
                "scope2_mt":          scope2_mt,
                "co2_kpi":            co2_kpi_arr,
                "energy_kpi":         energy_kpi_arr,
                "water_m3":           water_m3,
                "water_kpi":          water_kpi_arr,
                "waste_recovery_pct": waste_pct_arr,
                "renewable_pct":      renew_pct_arr,
                "renew_elec_gj":      renew_elec_arr,
                "nonrenew_elec_gj":   nonrenew_elec_arr,
                "nat_gas_gj":         nat_gas_arr,
                "coal_gj":            coal_arr,
                "diesel_gj":          diesel_arr,
                "biomass_gj":         biomass_arr,
                "total_co2_t":        total_co2_arr,
                "production_t":       production_arr,
                "total_energy_gj":    energy_arr,
            },
        }
        return func.HttpResponse(
            json.dumps(result, default=str),
            mimetype="application/json", headers=CORS)

    except Exception as ex:
        import traceback
        return func.HttpResponse(
            json.dumps({"error": str(ex), "trace": traceback.format_exc()}),
            status_code=500, mimetype="application/json", headers=CORS)