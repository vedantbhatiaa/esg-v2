import azure.functions as func
import json,sys,os
sys.path.insert(0,os.path.join(os.path.dirname(__file__),".."))
from shared.data_loader import get_all_companies

CORS={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"GET,OPTIONS","Access-Control-Allow-Headers":"Content-Type"}

def main(req):
    if req.method=="OPTIONS": return func.HttpResponse(status_code=204,headers=CORS)
    try:
        return func.HttpResponse(json.dumps(get_all_companies()),mimetype="application/json",headers=CORS)
    except Exception as e:
        return func.HttpResponse(json.dumps({"error":str(e)}),status_code=500,mimetype="application/json",headers=CORS)