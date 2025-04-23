# 这里写模块的rest接口
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sumo import sumo_manager

router = APIRouter()

@router.post("/start-sumo")
async def starSumo():  
    return JSONResponse(content=sumo_manager.start_sumo())

@router.post("/stop-sumo")
async def stopSumo():
    return JSONResponse(content=sumo_manager.stop_sumo())