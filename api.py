from fastapi import FastAPI,status
import random
from fastapi.middleware.cors import CORSMiddleware

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


@app.post("/rcms/services/rest/hikRpcService/genAgvSchedulingTask")
async def genAgvSchedulingTask():
    data = f'a{random.randint(1000,10000)}'
    reqCode = f'b{random.randint(1000,10000)}'
    return {"code": "0","data": data,"message": "successful", "reqCode": reqCode}

@app.post("/rcms/services/rest/hikRpcService/queryTaskStatus")
async def queryTaskStatus():
    code = str(random.randint(0,1))
    return {"code": code, "message": "successful"}