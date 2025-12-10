import flet as ft
from datetime import datetime

class DeveloperConsole(ft.Container):
    def __init__(self, on_clear_history_click):
        super().__init__()
        self.on_clear_history_click = on_clear_history_click
        
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
        
        self.content = ft.Column(
            controls=[
                ft.Text("DEVELOPER CONSOLE", color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD),
                ft.Divider(color=ft.Colors.GREEN_900),
                self.log_list,
                ft.Row([self.clear_history_btn], alignment=ft.MainAxisAlignment.CENTER)
            ]
        )
        
        self.width = 400
        self.bgcolor = ft.Colors.BLACK
        self.border = ft.border.all(1, ft.Colors.GREEN_900)
        self.border_radius = 5
        self.padding = 10
        self.visible = False # Hidden by default
        self.expand = False

    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = ft.Text(f"[{timestamp}] {message}", color=ft.Colors.GREEN, font_family="Consolas, monospace", size=12)
        self.log_list.controls.append(log_line)
        self.update()

    def clear_logs(self):
        self.log_list.controls.clear()
        self.log("Console cleared.")
        self.update()
