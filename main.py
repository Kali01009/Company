from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import random
import json
from datetime import datetime

app = FastAPI()

# Simulated candlestick data function
def get_1m_candle_data():
    open_price = random.uniform(24000, 25000)
    high_price = open_price + random.uniform(0, 100)
    low_price = open_price - random.uniform(0, 100)
    close_price = random.uniform(low_price, high_price)
    return {
        "time": datetime.utcnow().isoformat() + "Z",
        "open": round(open_price, 2),
        "high": round(high_price, 2),
        "low": round(low_price, 2),
        "close": round(close_price, 2)
    }

# WebSocket route
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            candle = get_1m_candle_data()
            await websocket.send_text(json.dumps(candle))
            await asyncio.sleep(60)  # Wait 1 minute before sending next candle
    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"Unexpected error: {e}")
