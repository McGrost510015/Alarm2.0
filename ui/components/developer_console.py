import flet as ft
from datetime import datetime

class DeveloperConsole(ft.Container):
    def __init__(self, on_clear_history_click, on_pulse_click=None, on_toggle_ignored_click=None):
        super().__init__()
        self.on_clear_history_click = on_clear_history_click
        self.on_pulse_click = on_pulse_click
        self.on_toggle_ignored_click = on_toggle_ignored_click
        
        self.log_list = ft.ListView(
            expand=True,
            spacing=2,
            auto_scroll=True,
            padding=10
        )
        
        self.clear_history_btn = ft.ElevatedButton(
            "Очистити історію",
            icon=ft.Icons.DELETE_SWEEP,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.RED_700,
                shape=ft.RoundedRectangleBorder(radius=5)
            ),
            on_click=self.on_clear_history_click
        )

        self.pulse_btn = ft.ElevatedButton(
            "Пульс",
            icon=ft.Icons.MONITOR_HEART,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
                shape=ft.RoundedRectangleBorder(radius=5)
            ),
            on_click=self.on_pulse_click
        )
        
        self.toggle_ignored_btn = ft.ElevatedButton(
            "Ignored: OFF", # Initial State Text
            icon=ft.Icons.VISIBILITY_OFF,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREY_700,
                shape=ft.RoundedRectangleBorder(radius=5)
            ),
            on_click=lambda e: self.toggle_ignored_state(e)
        )
        
        self.content = ft.Column(
            controls=[
                ft.Text("DEVELOPER CONSOLE", color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD),
                ft.Divider(color=ft.Colors.GREEN_900),
                self.log_list,
                ft.Row([self.clear_history_btn, self.pulse_btn, self.toggle_ignored_btn], alignment=ft.MainAxisAlignment.CENTER)
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )
        
        self.width = 400
        self.bgcolor = ft.Colors.BLACK
        self.border = ft.border.all(1, ft.Colors.GREEN_900)
        self.border_radius = 5
        self.padding = 10
        self.visible = False # Hidden by default
        self.expand = False

    def toggle_ignored_state(self, e):
        is_active = self.toggle_ignored_btn.text == "Ignored: ON"
        # Toggle
        new_state = not is_active
        
        if new_state:
            self.toggle_ignored_btn.text = "Ignored: ON"
            self.toggle_ignored_btn.icon = ft.Icons.VISIBILITY
            self.toggle_ignored_btn.style.bgcolor = ft.Colors.GREEN_700
        else:
            self.toggle_ignored_btn.text = "Ignored: OFF"
            self.toggle_ignored_btn.icon = ft.Icons.VISIBILITY_OFF
            self.toggle_ignored_btn.style.bgcolor = ft.Colors.GREY_700
            
        self.toggle_ignored_btn.update()
        
        if self.on_toggle_ignored_click:
            self.on_toggle_ignored_click(new_state)

    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = ft.Text(f"[{timestamp}] {message}", color=ft.Colors.GREEN, font_family="Consolas, monospace", size=12)
        self.log_list.controls.append(log_line)
        self.update()

    def clear_logs(self):
        self.log_list.controls.clear()
        self.log("Console cleared.")
        self.update()
