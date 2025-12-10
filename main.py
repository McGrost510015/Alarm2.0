import flet as ft
import asyncio
from ui.app_layout import AppLayout
from service.telegram_service import TelegramService
from service.alerts_service import AlertsService
import os
from datetime import datetime
import config

from ui.settings_dialog import SettingsDialog

async def main(page: ft.Page):
    telegram_service = None
    alerts_service = None
    
    # Store user settings in memory to avoid client_storage calls during callbacks
    user_settings = {
        "region": None
    }
    page.title = "Varta AI"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window.width = 1200 # Increased width
    page.window.height = 800
    page.window.min_width = 1350
    page.window.min_height = 700
    page.update()

    def on_dev_mode_change(enabled):
        layout.toggle_console(visible=enabled)
        layout.log("Developer Mode " + ("Enabled" if enabled else "Disabled"))
        
    def on_region_changed(region):
        user_settings["region"] = region
        if region:
             layout.log(f"Регіон змінено на: {region}")
        else:
             layout.log("Регіон скинуто")

    settings_dialog = SettingsDialog(page, on_dev_mode_change, on_region_changed)

    # --- Info Tooltip (Overlay) ---
    info_tooltip = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Varta AI — твій персональний аналітик безпеки.", weight=ft.FontWeight.BOLD, size=14),
                ft.Text("Програма моніторить Telegram-канали, відсіює інфошум та сповіщає про загрози.", size=13),
                ft.Divider(color=ft.Colors.GREY_700),
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.WARNING_AMBER, color=ft.Colors.ORANGE_400, size=20),
                        ft.Text("Важливо:", color=ft.Colors.ORANGE_400, weight=ft.FontWeight.BOLD, size=13),
                    ],
                    spacing=5
                ),
                ft.Text(
                    "Аналіз виконується штучним інтелектом, тому можливі похибки. Програма є виключно допоміжним інструментом.", 
                    size=12, color=ft.Colors.GREY_400
                ),
                ft.Text(
                    "Автор залишає за собою право не нести відповідальності за недостовірність інформації. Завжди орієнтуйтеся на офіційні сигнали тривоги.",
                    size=12, color=ft.Colors.GREY_400, italic=True
                )
            ],
            spacing=5,
        ),
        padding=15,
        width=400,
        bgcolor=ft.Colors.GREY_900,
        border=ft.border.all(1, ft.Colors.BLUE_900),
        border_radius=10,
        opacity=0,
        animate_opacity=300,
        # top=60,  <-- Moved to wrapper
        # left=20, <-- Moved to wrapper
        shadow=ft.BoxShadow(
            blur_radius=15,
            color=ft.Colors.BLACK,
            offset=ft.Offset(0, 5)
        ),
    )
    
    # Wrap in TransparentPointer so it doesn't block mouse events for elements below (like news cards)
    # properly handling the "ghost" nature of the tooltip.
    info_tooltip_wrapper = ft.TransparentPointer(
        content=info_tooltip,
        top=60, 
        left=20
    )
    
    page.overlay.append(info_tooltip_wrapper)

    def show_tooltip(e):
        info_tooltip.opacity = 1
        info_tooltip.update()

    def hide_tooltip(e):
        info_tooltip.opacity = 0
        info_tooltip.update()

    # --- Header ---
    header_content = ft.Row(
        controls=[
            ft.Icon(ft.Icons.SHIELD_MOON, color=ft.Colors.BLUE_400, size=30),
            ft.Row(
                controls=[
                    ft.Text("Varta", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text("AI", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE),
                ],
                spacing=2
            ),
        ],
        alignment=ft.MainAxisAlignment.START,
    )

    
    def on_header_hover(e):
        if e.data == "true":
            show_tooltip(e)
        else:
            hide_tooltip(e)

    header_interactive = ft.Container(
        content=header_content,
        on_hover=on_header_hover
    )

    settings_btn = ft.IconButton(icon=ft.Icons.SETTINGS, icon_color=ft.Colors.BLUE_400, on_click=lambda _: settings_dialog.show())
    
    header = ft.Row(
        controls=[
            header_interactive,
            ft.Container(expand=True),
            settings_btn
        ],
        alignment=ft.MainAxisAlignment.START,
    )

    async def on_pulse(e):
        layout.log("--- ПЕРЕВІРКА ПУЛЬСУ СИСТЕМИ ---")
        
        # 1. Telegram Connection
        layout.log("1. Перевірка з'єднання з Telegram...")
        if telegram_service:
            connected = await telegram_service.check_connection()
            if not connected:
                layout.log("Увага: Telegram не авторизовано/не підключено.")
        else:
            layout.log("Telegram сервіс: НЕ ЗАПУЩЕНО")
            
        await asyncio.sleep(0.5)

        # 2. Reading Status (Inferred from presence of service)
        layout.log("2. Статус читача...")
        if telegram_service:
             layout.log(f"Слухаємо канал: {telegram_service.channel_username}")
             
        await asyncio.sleep(0.5)
        
        # 3. Missed Messages
        layout.log("3. Перевірка пропущених повідомлень...")
        if telegram_service:
            await telegram_service.check_missed_messages()

        await asyncio.sleep(0.5)

        # 4. Alerts Data
        layout.log("4. Оновлення даних про тривоги...")
        if alerts_service:
            await alerts_service.force_refresh()
        else:
            layout.log("Сервіс тривог: НЕ ЗАПУЩЕНО")
            
        layout.log("--- ПЕРЕВІРКУ ЗАВЕРШЕНО ---")

    layout = AppLayout(page, on_clear_history=lambda e: layout.clear_history(e), on_pulse_click=on_pulse)
    
    page.add(
        header,
        layout
    )

    # Callback to update UI from Telegram
    # Callback to update UI from Telegram
    def on_telegram_message(summary, original_text, level, regions, time, footer):
        # Get User Region from cached settings (AVOIDS TIMEOUT)
        user_region = user_settings.get("region")
        
        is_region_match = False
        if user_region and regions:
            # Check if regions is a list or string, theoretically list per new JSON
            if isinstance(regions, list):
                if user_region in regions:
                    is_region_match = True
            elif isinstance(regions, str) and regions != "none":
                if user_region == regions:
                    is_region_match = True

        # Default Mapping
        title = "ПОВІДОМЛЕННЯ"
        bg_color = ft.Colors.BLUE_GREY_700
        
        # LOGIC:
        # Red Card IF: (Region Match AND Level != LOW) OR (Level == CRITICAL)
        
        is_danger = False
        if level == "CRITICAL":
            is_danger = True
        elif is_region_match and level != "LOW":
            is_danger = True
            
        if is_danger:
            title = "ВЕЛИКА НЕБЕЗПЕКА"
            bg_color = ft.Colors.RED_700
        else:
            # Standard Colors based on Level
            if level == "LOW":
                title = "ІНФОРМАЦІЯ"
                bg_color = ft.Colors.GREEN_700
            elif level == "MEDIUM":
                title = "УВАГА"
                bg_color = ft.Colors.YELLOW_700
            elif level == "HIGH":
                title = "НЕБЕЗПЕКА"
                bg_color = ft.Colors.ORANGE_700
            else:
                title = "ПОВІДОМЛЕННЯ"
                bg_color = ft.Colors.BLUE_GREY_700

        # Add News Card
        layout.add_news(title, summary, footer, time, bg_color, original_text=original_text)
        
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
    if config.API_HASH and config.API_HASH != 'your_api_hash':
        # Temporarily update config with integer ID for this session
        config.API_ID = real_api_id
        
        telegram_service = TelegramService(on_telegram_message, logger=logger)
        
        # Run Telegram client in the background
        asyncio.create_task(telegram_service.start())
        
        # Initialize Alerts Service (Map)
        def on_alerts_update(states):
            # This runs in a thread or async context depending on implementation
            # AppLayout.update_map calls map.update_alerts -> updates UI
            # Flet requires running UI updates on loop?
            # Since requests are blocking in thread, we call this on thread.
            # But MapComponent modifies controls. `image_control.update()` needs to happen.
            # Page is thread-safe.
            layout.update_map(states)
            
        alerts_service = AlertsService(on_alerts_update, logger=logger)
        asyncio.create_task(alerts_service.start_polling())
        
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
