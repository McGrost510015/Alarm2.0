import asyncio
import json
import flet as ft
from telethon import TelegramClient, events
import config

class TelegramService:
    def __init__(self, update_callback, logger=None):
        self.api_id = config.API_ID
        self.api_hash = config.API_HASH
        self.channel_username = config.CHANNEL_USERNAME
        self.client = TelegramClient('anon', self.api_id, self.api_hash)
        self.update_callback = update_callback
        self.logger = logger

    def log(self, msg):
        if self.logger:
            self.logger(msg)
        print(msg)

    async def start(self):
        await self.client.start()
        
        # Ensure we are connected
        if not await self.client.is_user_authorized():
            self.log("Client not authorized. Please run interactively to login first.")
            # print("Client not authorized. Please run interactively to login first.")
            
        self.log(f"Listening to {self.channel_username}...")

        @self.client.on(events.NewMessage(chats=self.channel_username))
        async def handler(event):
            raw_text = event.message.message
            date = event.message.date
            
            self.log(f"New message received: {raw_text[:50]}...")
            
            # --- Parsing Logic ---
            # 1. Skip first line (usually "json")
            lines = raw_text.split('\n')
            if len(lines) < 2:
                # Not a valid format, maybe log or ignore
                return
            
            # Join the rest to get JSON string
            json_str = "\n".join(lines[1:])
            
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                self.log("Failed to parse JSON. Ignoring.")
                # print("Failed to parse JSON")
                return

            # 2. Check status
            status = data.get("status", "").lower()
            if status == "ignore":
                self.log("Status is ignore. Skipping.")
                return
            
            # 3. Determine Level and Region
            level = data.get("level", "LOW")
            region_mentioned = data.get("region_mentioned", False)
            summary = data.get("summary", "")
            
            self.log(f"Parsed: Status={status}, Level={level}, Region={region_mentioned}")
            
            title = "ІНФОРМАЦІЯ"
            bg_color = ft.Colors.GREEN_700
            
            # Logic:
            # If region_mentioned == true -> RED, "ВЕЛИКА НЕБЕЗПЕКА"
            if region_mentioned:
                title = "ВЕЛИКА НЕБЕЗПЕКА"
                bg_color = ft.Colors.RED_700
            else:
                # Based on level
                if level == "LOW":
                    title = "ІНФОРМАЦІЯ"
                    bg_color = ft.Colors.GREEN_700
                elif level == "MEDIUM":
                    title = "УВАГА"
                    bg_color = ft.Colors.YELLOW_700 # or AMBER
                elif level == "HIGH":
                    title = "НЕБЕЗПЕКА"
                    bg_color = ft.Colors.ORANGE_700
                elif level == "CRITICAL":
                    title = "ВЕЛИКА НЕБЕЗПЕКА"
                    bg_color = ft.Colors.RED_700
                else:
                    # Fallback
                    title = "ПОВІДОМЛЕННЯ"
                    bg_color = ft.Colors.BLUE_GREY_700

            formatted_time = date.strftime("%H:%M:%S")
            footer_text = date.strftime("%d.%m.%Y")
            
            # Callback to UI
            if self.update_callback:
                self.update_callback(title, summary, footer_text, formatted_time, bg_color)

        # Run until disconnected
        await self.client.run_until_disconnected()

    async def connect(self):
        await self.client.start()
