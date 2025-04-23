import logging
logger = logging.getLogger(__name__)
import os
import sys
import datetime


if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
else:
    sys.exit("请设置SUMO_HOME环境变量")

import traci
import time
from ws import web_socket 
import threading
stopSumo = False
sumoThread = None

def start_sumo():
    global stopSumo,sumoThread
    if sumoThread is not None:
        logging.info("SUMO...已启动")
        return "SUMO...已启动"
    logger.info("启动sumo...")
    sumoThread = threading.Thread(target=run_sumo)
    stopSumo = False
    sumoThread.daemon = True  
    sumoThread.start()
    return "启动sumo..."

def run_sumo():
    global stopSumo
    sumoBinary = "sumo"
    sumoCmd = [sumoBinary, "-c", "sumo/atm_new.sumocfg"]
    traci.start(sumoCmd)
    step = 0
    while step < 5000:
        if stopSumo:
            logging.info("将退出SUMO...")
            break
        traci.simulationStep()
        on_step()
        step += 1
        logging.info(step)
        time.sleep(0.9)
    traci.close()
    logging.info("SUMO...已关闭")
    return "SUMO...已关闭"

def stop_sumo():
    global stopSumo,sumoThread
    if sumoThread is None:
        logger.info("sumo已经关闭...")
        return "sumo已经关闭..."
    stopSumo = True
    sumoThread.join(timeout=6)
    sumoThread = None
    return "SUMO...关闭成功"



def on_step():
    vehicle_ids = traci.vehicle.getIDList()
    logger.info(f"车辆总数：{len(vehicle_ids)}")
    data=[]
    # 遍历每辆车获取位置信息
    for veh_id in vehicle_ids:
        # 获取二维坐标
        x, y = traci.vehicle.getPosition(veh_id)  
        # 转换为经纬度
        lon, lat = traci.simulation.convertGeo(x, y)  
        angle = traci.vehicle.getAngle(veh_id)
        typeId = traci.vehicle.getTypeID(veh_id)
        speed = traci.vehicle.getSpeed(veh_id)
        data.append({"id":veh_id,"lng":lon,"lat":lat,"heading":angle,"typeId":typeId,"speed":speed})
    message = {"timestamp": int(datetime.datetime.now().timestamp() * 1000),"data":data}
    web_socket.ws_msg_queue.put_nowait(message)

