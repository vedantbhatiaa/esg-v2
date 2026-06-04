import azure.functions as func
import json,sys,os
sys.path.insert(0,os.path.join(os.path.dirname(__file__),".."))
from shared.data_loader import get_historical_series,get_sector_series,get_all_companies,id_to_name
from shared.calculations import calculate_all_kpis

CORS={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"GET,OPTIONS","Access-Control-Allow-Headers":"Content-Type"}

def main(req):
    if req.method=="OPTIONS": return func.HttpResponse(status_code=204,headers=CORS)
    try:
        company_id=req.params.get("company_id")
        year_from=int(req.params.get("year_from",2009))
        year_to=int(req.params.get("year_to",2023))
        years=list(range(year_from,year_to+1))
        result={"years":years,"series":{}}
        
        KPI_FIELDS=["_energy_kpi","_co2_kpi","_water_kpi","_scope1","_scope2","_total_co2",
                    "_total_energy","_renew_share_pct","_waste_recov_pct"]
        RENAME={"_energy_kpi":"energy_kpi","_co2_kpi":"co2_kpi","_water_kpi":"water_kpi",
                "_scope1":"scope1_co2","_scope2":"scope2_co2","_total_co2":"total_co2",
                "_total_energy":"total_energy","_renew_share_pct":"renewable_share_pct",
                "_waste_recov_pct":"waste_recovery_pct"}
        
        if company_id:
            company_name=id_to_name(company_id) or company_id
            series=get_historical_series(company_name,year_from,year_to)
            for f in KPI_FIELDS:
                key=RENAME.get(f,f)
                result["series"][key]=[{"year":yr,"value":next((e.get(f) for e in series if e["year"]==yr),None)} for yr in years]
        else:
            sector=get_sector_series(year_from,year_to)
            for f in KPI_FIELDS:
                key=RENAME.get(f,f)
                result["series"][key]=[{"year":e["year"],"value":e.get(f)} for e in sector]
        
        return func.HttpResponse(json.dumps(result),mimetype="application/json",headers=CORS)
    except Exception as e:
        import traceback
        return func.HttpResponse(json.dumps({"error":str(e),"trace":traceback.format_exc()}),
            status_code=500,mimetype="application/json",headers=CORS)