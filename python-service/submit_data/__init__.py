import azure.functions as func
import json,sys,os
sys.path.insert(0,os.path.join(os.path.dirname(__file__),".."))
from shared.calculations import calculate_all_kpis,calculate_yoy_all
from shared.verification  import check_yoy_flags,get_submission_status
from shared.data_loader   import save_submission,get_prior_year_kpis,id_to_name

CORS={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"POST,OPTIONS","Access-Control-Allow-Headers":"Content-Type"}

def main(req):
    if req.method=="OPTIONS": return func.HttpResponse(status_code=204,headers=CORS)
    try:
        body=req.get_json()
        company_id=body.get("company_id","")
        year=int(body.get("year",2023))
        form_data=body.get("data",{})
        company_name=id_to_name(company_id) or company_id
        kpis=calculate_all_kpis(form_data)
        kpis["_raw_iso_total"]=int(form_data.get("total_sites",0))
        kpis["_raw_iso_certified"]=int(form_data.get("iso_sites",0))
        prior=get_prior_year_kpis(company_name,year) or {}
        yoy=calculate_yoy_all(kpis,prior)
        flags=check_yoy_flags(kpis,prior)
        status=get_submission_status(flags)
        saved=save_submission(company_name,year,form_data)
        return func.HttpResponse(json.dumps({**saved,"kpis":kpis,"yoy":yoy,"flags":flags,
            "status":status,"company":company_name,"year":year,
            "message":f"Submission for {company_name} {year} saved successfully."},default=str),
            mimetype="application/json",status_code=200,headers=CORS)
    except Exception as e:
        import traceback
        return func.HttpResponse(json.dumps({"error":str(e),"trace":traceback.format_exc()}),
            status_code=500,mimetype="application/json",headers=CORS)