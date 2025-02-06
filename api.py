from fastapi import FastAPI,status,Request,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random

app = FastAPI()

origins = [
    "*",
    "http://localhost:8000",
    "http://192.168.0.160:8000",  
    "http://192.168.100.114:8000", 
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)


@app.post("/rcms/services/rest/hikRpcService/bindCtnrAndBin")
async def bindCtnrAndBin(request:Request):
    if request.headers.get("Content-Type") != "application/json":
        raise HTTPException(status_code=400,detail="only json!!")
    else:
        code = "1"
        req_json = await request.json()
        reqCode = req_json['reqCode']
        return {"code": code, "message": "successful","reqCode":reqCode}


@app.post("/rcms/services/rest/hikRpcService/genAgvSchedulingTask")
async def genAgvSchedulingTask(request:Request):
    if request.headers.get("Content-Type") != "application/json":
        raise HTTPException(status_code=400,detail="only json!!")
    else:
        req_json = await request.json()
        reqCode = req_json['reqCode']
        data = f'd_{datetime.now().strftime("%Y%m%d%H%M%S")}'
        return {"code": "0","data": data,"message": "successful", "reqCode": reqCode}
 

@app.post("/rcms/services/rest/hikRpcService/queryTaskStatus")
async def queryTaskStatus(request:Request):
    if request.headers.get("Content-Type") != "application/json":
        raise HTTPException(status_code=400,detail="only json!!")
    else:
        code = str(random.randint(0,1))
    return {"code": code, "message": "successful"}