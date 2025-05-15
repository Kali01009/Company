import asyncio
import json
import websockets
from datetime import datetime
from analyzer import Analyzer

analyzer = Analyzer()

async def handler(websocket, path):
    index = path.strip("/").split("/")[-1]  # e.g. /ws/R_75
    while True:
        # Simulate receiving a live tick (replace with real source)
        quote = simulate_live_price()
        timestamp = int(datetime.utcnow().timestamp())

        tick_data = {'tick': {'quote': quote, 'epoch': timestamp}}
        signal_data = analyzer.update(quote, timestamp)

        if signal_data:
            tick_data['signal'] = signal_data

        await websocket.send(json.dumps(tick_data))
        await asyncio.sleep(1)

def simulate_live_price():
    from random import uniform
    return round(100 + uniform(-1, 1), 4)

start_server = websockets.serve(handler, "localhost", 8000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
