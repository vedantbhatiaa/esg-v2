import azure.functions as func
import json,sys,os
sys.path.insert(0,os.path.join(os.path.dirname(__file__),".."))
from shared.data_loader import authenticate

CORS={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"POST,OPTIONS","Access-Control-Allow-Headers":"Content-Type"}

def main(req):
    if req.method=="OPTIONS": return func.HttpResponse(status_code=204,headers=CORS)
    try:
        body=req.get_json(); email=body.get("email",""); pw=body.get("password","")
        user=authenticate(email,pw)
        if not user: return func.HttpResponse(json.dumps({"error":"Invalid credentials"}),status_code=401,mimetype="application/json",headers=CORS)
        return func.HttpResponse(json.dumps(user),mimetype="application/json",headers=CORS)
    except Exception as e:
        return func.HttpResponse(json.dumps({"error":str(e)}),status_code=500,mimetype="application/json",headers=CORS)