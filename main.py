import os
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import websockets
import asyncio
import json
import uvicorn
import aiohttp

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get_index():
    return FileResponse("static/index.html")

async def fetch_historical_candles(index: str):
    url = "https://api.deriv.com/api/websockets/v3"
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://deriv-api.binary.com/exchange/ticks?index={index}&count=100&style=candles&granularity=60"
        ) as response:
            data = await response.json()
            return data["candles"] if "candles" in data else []

@app.websocket("/ws/{index}")
async def websocket_endpoint(websocket: WebSocket, index: str):
    await websocket.accept()
    
    # Send historical data first
    candles = await fetch_historical_candles(index)
    await websocket.send_text(json.dumps({"type": "historical", "candles": candles}))

    # Start WebSocket connection for live ticks
    async with websockets.connect("wss://ws.binaryws.com/websockets/v3?app_id=1089") as ws:
        await ws.send(json.dumps({
            "ticks": index,
            "subscribe": 1
        }))

        try:
            while True:
                tick = await ws.recv()
                await websocket.send_text(json.dumps({"type": "tick", "tick": json.loads(tick)}))
        except Exception as e:
            print("WebSocket error:", e)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
