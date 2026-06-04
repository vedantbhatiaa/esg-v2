import azure.functions as func
import json,sys,os
sys.path.insert(0,os.path.join(os.path.dirname(__file__),".."))
from shared.data_loader import get_sector_quartiles,get_historical_series,get_company_years,get_verification_status,get_all_companies,id_to_name
from shared.calculations import calculate_all_kpis

CORS={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"GET,OPTIONS","Access-Control-Allow-Headers":"Content-Type"}

def main(req):
    if req.method=="OPTIONS": return func.HttpResponse(status_code=204,headers=CORS)
    try:
        year=int(req.params.get("year",2023))
        company=req.params.get("company","")
        bands=get_sector_quartiles(year)
        my_kpis=None
        company_trend={}
        
        if company:
            yrs=get_company_years(company)
            for y in yrs:
                series=get_historical_series(company,y,y)
                if series:
                    e=series[0]; k=calculate_all_kpis(e)
                    rt=max((e.get("renew_elec_purchased",0) or 0)+(e.get("nonrenew_elec_purchased",0) or 0)+(e.get("self_gen_elec",0) or 0),1)
                    company_trend[y]={
                        "co2_kpi":k.get("co2_kpi"),"energy_kpi":k.get("energy_kpi"),
                        "water_kpi":k.get("water_kpi"),
                        "waste_pct":k.get("waste_recov_pct"),
                        "renew_pct":(e.get("renew_elec_purchased",0) or 0)/rt*100,
                        "scope1":k.get("scope1"),"scope2":k.get("scope2"),
                        "renew_gj":e.get("renew_elec_purchased",0) or 0,
                        "nonrenew_gj":e.get("nonrenew_elec_purchased",0) or 0,
                        "nat_gas":e.get("nat_gas",0) or 0,"coal":e.get("coal_sub",0) or 0,
                        "diesel":e.get("diesel",0) or 0,"biomass":e.get("biomass",0) or 0,
                        "water_m3":e.get("water_withdrawals",0) or 0,
                        "waste_total":e.get("waste_total",0) or 0,
                        "waste_rec":e.get("waste_recovery",0) or 0,
                    }
                    if y==year: my_kpis={"co2_kpi":k.get("co2_kpi"),"energy_kpi":k.get("energy_kpi"),
                        "water_kpi":k.get("water_kpi"),"waste_recov_pct":k.get("waste_recov_pct"),
                        "renew_share_pct":(e.get("renew_elec_purchased",0) or 0)/rt*100,"iso_pct":k.get("iso_pct")}
        
        scorecard=[]
        for co in get_all_companies():
            if co["role"]!="client": continue
            s=get_historical_series(co["name"],year,year)
            if s:
                e=s[0]; k=calculate_all_kpis(e)
                rt=max((e.get("renew_elec_purchased",0) or 0)+(e.get("nonrenew_elec_purchased",0) or 0)+(e.get("self_gen_elec",0) or 0),1)
                scorecard.append({
                    "company":co["name"],"co2_kpi":k.get("co2_kpi"),"energy_kpi":k.get("energy_kpi"),
                    "water_kpi":k.get("water_kpi"),"renew_pct":(e.get("renew_elec_purchased",0) or 0)/rt*100,
                    "waste_pct":k.get("waste_recov_pct"),"verif_status":get_verification_status(co["name"],year),
                })
        
        return func.HttpResponse(json.dumps({"year":year,"bands":bands,"scorecard":scorecard,
            "my_kpis":my_kpis,"company_trend":company_trend}),
            mimetype="application/json",headers=CORS)
    except Exception as e:
        import traceback
        return func.HttpResponse(json.dumps({"error":str(e),"trace":traceback.format_exc()}),
            status_code=500,mimetype="application/json",headers=CORS)