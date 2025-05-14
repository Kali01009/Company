import os
import json
import asyncio
import websockets
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import uvicorn

app = FastAPI()

DERIV_WS = "wss://ws.derivws.com/websockets/v3?app_id=1089"

async def subscribe_ticks(index: str):
    async with websockets.connect(DERIV_WS) as ws:
        await ws.send(json.dumps({"ticks": index, "subscribe": 1}))
        while True:
            msg = await ws.recv()
            yield msg

@app.websocket("/ws/{index}")
async def websocket_endpoint(websocket: WebSocket, index: str):
    await websocket.accept()
    try:
        async for tick in subscribe_ticks(index):
            await websocket.send_text(tick)
    except Exception as e:
        await websocket.close()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
