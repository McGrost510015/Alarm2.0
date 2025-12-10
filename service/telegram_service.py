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
            await self.check_missed_messages()
        else:
            self.log("First run or no state found. Listening for new messages only.")

            # We could fetch the latest message ID here to set looking forward, 
            # but getting the next new message will set the state anyway.

    async def check_connection(self):
        if await self.client.is_user_authorized():
            self.log("З'єднання з Telegram: ОК")
            return True
        else:
            self.log("З'єднання з Telegram: НЕ АВТОРИЗОВАНО")
            return False

    async def check_missed_messages(self):
        if not self.last_message_id:
            self.log("Немає ID останнього повідомлення для перевірки.")
            return

        self.log(f"Перевірка пропущених повідомлень починаючи з ID {self.last_message_id}...")
        try:
            # min_id excludes the message with that ID, so we get only newer ones
            # limit=20 to avoid fetching too many if gap is huge
            messages = await self.client.get_messages(self.channel_username, min_id=self.last_message_id, limit=20, reverse=True)
            if messages:
                self.log(f"Знайдено {len(messages)} пропущених повідомлень.")
                for message in messages:
                    await self.process_message(message)
            else:
                self.log("Пропущених повідомлень не знайдено.")
        except Exception as e:
            self.log(f"Помилка отримання пропущених повідомлень: {e}")


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
        
        # 3. Determine Level, Region, and Original Text
        level = data.get("level", "LOW")
        regions = data.get("regions", []) # List of strings
        original_text = data.get("original_text", "")
        summary = data.get("summary", "")
        
        # We now pass 'level', 'regions', 'summary', 'original_text' to the UI callback
        # The logic for determining color/title will move to main.py because it needs access to user settings (client_storage)
        
        formatted_time = date.strftime("%H:%M:%S")
        footer_text = date.strftime("%d.%m.%Y")
        
        # Callback to UI
        if self.update_callback:
            # New Signature: callback(title, summary, footer, time, bg_color, original_text, level, regions)
            # Wait, main.py expects (title, text, footer, time, bg_color) currently.
            # I should update main.py FIRST or pass a dict/object.
            # Or just pass raw data and let main.py decide title/color.
            
            # Let's change the callback contract to:
            # on_message(data_dict) or on_message(summary, original_text, level, regions, time_str, date_str)
            
            # To minimize breakage during refactor, I will change main.py's handler first?
            # No, I can't change main.py signature in the same atomic step easily if I strictly follow file-by-file.
            # But I can modify the arguments passed here.
            
            # Let's pass: 
            # callback(summary, original_text, level, regions, formatted_time, footer_text)
            self.update_callback(summary, original_text, level, regions, formatted_time, footer_text)

    async def connect(self):
        await self.client.start()
