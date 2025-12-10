import requests
import asyncio
import time

URL = "https://ubilling.net.ua/aerialalerts/"

class AlertsService:
    def __init__(self, on_update, logger=None):
        self.on_update = on_update
        self.logger = logger
        self.running = False
        self._last_states = {}

    def log(self, msg):
        if self.logger:
            self.logger(f"[Alerts] {msg}")
        else:
            print(f"[Alerts] {msg}")

    async def start_polling(self):
        self.running = True
        self.log("Started polling for alerts...")
        while self.running:
            await self.fetch_alerts()
            
            # Poll every 15 seconds to avoid rate limits
            await asyncio.sleep(15)

    async def force_refresh(self):
        self.log("Примусове оновлення тривог...")
        await self.fetch_alerts()

    async def fetch_alerts(self):
        try:
            # Run blocking request in executor
            response = await asyncio.to_thread(requests.get, URL)
            if response.status_code == 200:
                data = response.json()
                states = data.get("states", {})
                self.on_update(states)
                self.log("Дані тривог успішно оновлено.")
            elif response.status_code == 429:
                self.log(f"Rate limit hit (429).")
            else:
                self.log(f"Error fetching alerts: {response.status_code}")
        except Exception as e:
            self.log(f"Exception fetching alerts: {e}")

    def stop(self):
        self.running = False
