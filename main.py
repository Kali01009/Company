from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import websockets
import json

app = FastAPI()

app.mount("/", StaticFiles(directory="static", html=True), name="static")

async def subscribe(ws, index):
    msg = {
        "ticks": index,
        "subscribe": 1
    }
    await ws.send(json.dumps(msg))

@app.websocket("/ws/{index}")
async def websocket_endpoint(websocket: WebSocket, index: str):
    await websocket.accept()
    url = "wss://ws.binaryws.com/websockets/v3?app_id=1089"

    async with websockets.connect(url) as ws:
        await subscribe(ws, index)

        try:
            while True:
                data = await ws.recv()
                await websocket.send_text(data)
        except Exception as e:
            print("WebSocket error:", e)
