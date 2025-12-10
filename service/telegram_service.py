import asyncio
import json
import os
import flet as ft
from telethon import TelegramClient, events
import config

STATE_FILE = "telegram_state.json"

class TelegramService:
    def __init__(self, update_callback, logger=None):
        self.api_id = config.API_ID
        self.api_hash = config.API_HASH
        self.channel_username = config.CHANNEL_USERNAME
        self.client = TelegramClient('anon', self.api_id, self.api_hash)
        self.update_callback = update_callback
        self.logger = logger
        self.last_message_id = self.load_state()

    def load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get("last_message_id")
            except Exception as e:
                self.log(f"Error loading state: {e}")
        return None

    def save_state(self, msg_id):
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump({"last_message_id": msg_id}, f)
            self.last_message_id = msg_id
        except Exception as e:
            self.log(f"Error saving state: {e}")

    def log(self, msg):
        if self.logger:
            self.logger(msg)
        print(msg)

    async def start(self):
        await self.client.start()
        
        # Ensure we are connected
        if not await self.client.is_user_authorized():
            self.log("Client not authorized. Please run interactively to login first.")
            
        self.log(f"Listening to {self.channel_username}...")

        # Catch up on missed messages
        if self.last_message_id:
            self.log(f"Checking for missed messages since ID {self.last_message_id}...")
            try:
                # min_id excludes the message with that ID, so we get only newer ones
                # limit=20 to avoid fetching too many if gap is huge
                messages = await self.client.get_messages(self.channel_username, min_id=self.last_message_id, limit=20, reverse=True)
                if messages:
                    self.log(f"Found {len(messages)} missed messages.")
                    for message in messages:
                        await self.process_message(message)
                else:
                    self.log("No missed messages found.")
            except Exception as e:
                self.log(f"Error fetching missed messages: {e}")
        else:
            self.log("First run or no state found. Listening for new messages only.")
            # We could fetch the latest message ID here to set looking forward, 
            # but getting the next new message will set the state anyway.

        @self.client.on(events.NewMessage(chats=self.channel_username))
        async def handler(event):
            await self.process_message(event.message)

        # Run until disconnected
        await self.client.run_until_disconnected()

    async def process_message(self, message):
        # Update state
        if message.id:
             self.save_state(message.id)

        raw_text = message.message
        date = message.date
        
        self.log(f"New message received: {raw_text[:50]}...")
        
        # --- Parsing Logic ---
        # 1. Skip first line (usually "json")
        lines = raw_text.split('\n')
        if len(lines) < 2:
            return
        
        # Join the rest to get JSON string
        json_str = "\n".join(lines[1:])
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            self.log("Failed to parse JSON. Ignoring.")
            return

        # 2. Check status
        status = data.get("status", "").lower()
        if status == "ignore":
            self.log("Status is ignore. Skipping.")
            return
        
        # 3. Determine Level and Region
        level = data.get("level", "LOW")
        # region_mentioned = data.get("region_mentioned", False) # Ignored for UI styling as per request
        summary = data.get("summary", "")
        
        # self.log(f"Parsed: Status={status}, Level={level}, Region={region_mentioned}") # Optional logging
        
        title = "ІНФОРМАЦІЯ"
        bg_color = ft.Colors.GREEN_700
        
        # Logic: Solely based on level
        if level == "LOW":
            title = "ІНФОРМАЦІЯ"
            bg_color = ft.Colors.GREEN_700
        elif level == "MEDIUM":
            title = "УВАГА"
            bg_color = ft.Colors.YELLOW_700 
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

    async def connect(self):
        await self.client.start()
