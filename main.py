from fastapi import FastAPI, WebSocket
import websockets
import asyncio
import json

app = FastAPI()

DERIV_WS = "wss://ws.derivws.com/websockets/v3?app_id=1089"

async def subscribe_ticks(index: str):
    async with websockets.connect(DERIV_WS) as ws:
        await ws.send(json.dumps({"ticks": index, "subscribe": 1}))
        while True:
            msg = await ws.recv()
            yield msg

@app.websocket("/ws/{index}")
async def ws_endpoint(websocket: WebSocket, index: str):
    await websocket.accept()
    async for tick in subscribe_ticks(index):
        await websocket.send_text(tick)
