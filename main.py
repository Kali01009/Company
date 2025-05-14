import os
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import websockets
import asyncio
import json
import uvicorn

app = FastAPI()

# Serve static files from /static
app.mount("/", StaticFiles(directory="static", html=True), name="static")


async def subscribe(ws, index):
    await ws.send(json.dumps({
        "ticks": index,
        "subscribe": 1
    }))


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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Use $PORT or fallback to 8000
    uvicorn.run("main:app", host="0.0.0.0", port=port)
