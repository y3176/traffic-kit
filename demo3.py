import base.logs

import logging
logger = logging.getLogger(__name__)


from fastapi import FastAPI
from fastapi.responses import FileResponse 
from fastapi.staticfiles import StaticFiles 
from fastapi import WebSocket,WebSocketDisconnect


from contextlib import asynccontextmanager
import asyncio
from ws import web_socket

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("启动消息发送任务....")
    web_socket.running = True
    sending_task = asyncio.create_task(web_socket.sending())

    try:
        yield 
    finally:
        web_socket.running = False
        logger.info("停止消息发送任务....")
        sending_task.cancel()

app = FastAPI(lifespan=lifespan)


from api.web import router as api_router
app.include_router(api_router, prefix="/api")


@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    # 注册 WebSocket 连接
    await websocket.accept()
    web_socket.active_connections.add(websocket)
    logger.info(f"WebSocket connection established size={len( web_socket.active_connections)}")
    while True:
        try:
            message = await websocket.receive_text()
            logger.info(f"Received message: {message}")
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")
            break
        except Exception as e:
            logger.error(f"Error in WebSocket: {e}",exc_info=e)
        finally:
            web_socket.active_connections.remove(websocket)
            try:
                await websocket.close()
            except Exception as e:
                logger.info(f"自动关闭websocket：{e}",exc_info=e)

@app.get("/", response_class=FileResponse)
async def read_index():
    return FileResponse("static/demo3/realtime-vehicle.html")

app.mount("/", StaticFiles(directory="static/demo3/"), name="static")

if __name__ == "__main__":  
    host="0.0.0.0"
    port=8008
    import webbrowser
    webbrowser.open(f"http://127.0.0.1:{port}/")
    import uvicorn 
    uvicorn.run(app, host=host, port=port)

