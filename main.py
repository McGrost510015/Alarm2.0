import flet as ft
import asyncio
from ui.app_layout import AppLayout
from service.telegram_service import TelegramService
import os
from datetime import datetime
import config

from ui.settings_dialog import SettingsDialog

async def main(page: ft.Page):
    page.title = "Ukraine News Alert AI"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window_width = 1200 # Increased width
    page.window_height = 800

    def on_dev_mode_change(enabled):
        layout.toggle_console(visible=enabled)
        layout.log("Developer Mode " + ("Enabled" if enabled else "Disabled"))

    settings_dialog = SettingsDialog(page, on_dev_mode_change)

    # Header
    header = ft.Row(
        controls=[
            ft.Icon(ft.Icons.SHIELD_MOON, color=ft.Colors.BLUE_400, size=30),
            ft.Text("News Shield AI", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.IconButton(icon=ft.Icons.SETTINGS, icon_color=ft.Colors.BLUE_400, on_click=lambda _: settings_dialog.show())
        ],
        alignment=ft.MainAxisAlignment.START,
    )

    layout = AppLayout(page, on_clear_history=None) # We need to define clear history logic inside layout or pass here
    # Since AppLayout handles clear_history mostly internally or we need to pass a dummy if the logic is inside AppLayout as implemented...
    # Actually AppLayout implementation above takes `on_clear_history`, let's verify AppLayout again. 
    # AppLayout calls self.news_list_container.controls.clear(). It doesn't need external callback necessarily but I defined it in constructor.
    # Let's link it to AppLayout.clear_history method if needed or just pass a method that does logging.
    
    # Wait, AppLayout implementation I wrote takes `on_clear_history`.
    # `self.console = DeveloperConsole(on_clear_history_click=on_clear_history)`
    # And `DeveloperConsole` calls it.
    # So `layout.clear_history` is the method I wrote in `AppLayout`. 
    # But `DeveloperConsole` is initialized inside `AppLayout`. 
    # Ah, circle dependency potentially if I am not careful. 
    
    # Let's fix AppLayout initialization first in main. 
    
    # Actually, looking at AppLayout I wrote:
    # class AppLayout(ft.Row):
    #   def __init__(self, page: ft.Page, on_clear_history):
    #       ...
    #       self.console = DeveloperConsole(on_clear_history_click=on_clear_history)
    
    # So main.py needs to pass a function that clears history. 
    # But `layout` object is what holds the history. 
    # So we need to create `layout` first, THEN define the callback? No, that's chicken and egg.
    
    # Better approach: Pass a lambda that calls a method on layout, but layout isn't defined yet.
    # Or make `AppLayout` handle the clearing internally without passing it in.
    
    # Refactor AppLayout in main to handle this? 
    # I will modify AppLayout in next step to not require `on_clear_history` in init, but handle it internally.
    # For now, let's just pass a placeholder and re-inject it, or better, pass `lambda e: layout.clear_history(e)`.
    # Flet allows this because lambda is evaluated when clicked.
    
    layout = AppLayout(page, on_clear_history=lambda e: layout.clear_history(e))
    
    page.add(
        header,
        layout
    )

    # Callback to update UI from Telegram
    def on_telegram_message(title, text, footer, time, bg_color):
        layout.add_news(title, text, footer, time, bg_color)
        
    def logger(msg):
        layout.log(msg)

    # Verify API credentials
    api_id_valid = False
    try:
        real_api_id = int(config.API_ID)
        api_id_valid = True
    except (ValueError, TypeError):
        pass

    if not api_id_valid or config.API_ID == 'your_api_id':
        layout.add_news(
            "ПОМИЛКА НАЛАШТУВАННЯ", 
            "Будь ласка, відкрийте файл .env та вкажіть ваші TELEGRAM_API_ID та TELEGRAM_API_HASH.", 
            "Система", 
            datetime.now().strftime("%H:%M:%S"), 
            ft.Colors.RED_700,
            save=False
        )
        print("Invalid Configuration: API_ID is missing or invalid.")
        return

    # Initialize Telegram Service
    # Note: running telethon loop inside Flet's async loop
    if config.API_HASH and config.API_HASH != 'your_api_hash':
        # Temporarily update config with integer ID for this session
        config.API_ID = real_api_id
        
        telegram_service = TelegramService(on_telegram_message, logger=logger)
        
        # Run Telegram client in the background
        # We use asyncio.create_task to run it concurrently with Flet
        asyncio.create_task(telegram_service.start())
    else:
        layout.add_news(
            "ПОМИЛКА НАЛАШТУВАННЯ", 
            "Вкажіть TELEGRAM_API_HASH у файлі .env", 
            "Система", 
            datetime.now().strftime("%H:%M:%S"), 
            ft.Colors.RED_700,
            save=False
        )

if __name__ == "__main__":
    ft.app(target=main)
