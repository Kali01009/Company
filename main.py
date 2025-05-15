from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import websockets
import json
import os
import uvicorn
import asyncio
from datetime import datetime, timezone

app = FastAPI()

DERIV_WS = "wss://ws.derivws.com/websockets/v3?app_id=1089"

async def subscribe_ticks(index: str):
    async with websockets.connect(DERIV_WS) as ws:
        await ws.send(json.dumps({"ticks": index, "subscribe": 1}))

        # Variables to accumulate candle data
        candle = None
        current_minute = None

        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            if "tick" in data:
                tick = data["tick"]
                tick_time = datetime.fromtimestamp(tick["epoch"], tz=timezone.utc)
                tick_minute = tick_time.replace(second=0, microsecond=0)

                price = tick["quote"]

                if current_minute != tick_minute:
                    # New minute started - yield previous candle if exists
                    if candle is not None:
                        yield json.dumps({"candle": candle})

                    # Initialize new candle for this minute
                    candle = {
                        "time": tick_minute.isoformat(),
                        "open": price,
                        "high": price,
                        "low": price,
                        "close": price,
                    }
                    current_minute = tick_minute
                else:
                    # Update current candle
                    candle["high"] = max(candle["high"], price)
                    candle["low"] = min(candle["low"], price)
                    candle["close"] = price

            # Also yield raw tick data so client can have realtime tick if needed
            yield msg


@app.websocket("/ws/{index}")
async def websocket_endpoint(websocket: WebSocket, index: str):
    await websocket.accept()
    async for message in subscribe_ticks(index):
        await websocket.send_text(message)


# Serve static files from the ./static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    # Redirect root path to /static/index.html
    return RedirectResponse(url="/static/index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Use Render's PORT or default 8000
    uvicorn.run("main:app", host="0.0.0.0", port=port)
