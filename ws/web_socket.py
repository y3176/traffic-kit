import logging
logger = logging.getLogger(__name__)

from fastapi import WebSocket,WebSocketDisconnect
import asyncio

import queue 
ws_msg_queue = queue.Queue(maxsize=100)
active_connections = set()
running = True

async def sending():
    global running
    while running:
        try:
            data = ws_msg_queue.get_nowait()   # 从队列中获取数据
        except queue.Empty:
            logger.debug("没有待发送的消息 稍后重试...")
            await asyncio.sleep(0.1)
            continue
        try:
            # 向所有连接的 WebSocket 发送数据
            tasks = [send_data_to_client(client, data) for client in active_connections]
            await asyncio.gather(*tasks)  # 异步地广播数据到所有客户端
        except Exception as e:
            logger.warning(f"推送ws消息异常{e}",exc_info=e)
        logger.info(f"Sent data to all[{len(active_connections)}] dataSize: {len(data)}")

# 向单个 WebSocket 客户端发送数据
async def send_data_to_client(client: WebSocket, data):
    try:
        # 设置超时，防止发送失败阻塞
        await asyncio.wait_for(client.send_json(data), timeout=2.0)  # 2秒超时
        logger.info(f"Sent data to client: {len(data)}")
    except asyncio.TimeoutError:
        logger.warning(f"Timeout error while sending data to client: {len(data)}")
    except WebSocketDisconnect:
        logger.info(f"WebSocket client {client} disconnected")
        active_connections.remove(client)
    except Exception as e:
        logger.error(f"Error sending data to client: {e}",exc_info=e)