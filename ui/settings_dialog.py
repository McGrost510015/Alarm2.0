import flet as ft

class SettingsDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, on_dev_mode_change):
        super().__init__()
        self.page = page
        self.on_dev_mode_change = on_dev_mode_change
        
        self.dev_mode_switch = ft.Switch(
            label="Режим розробника",
            value=False,
            on_change=self.on_switch_change
        )
        
        self.title = ft.Text("Налаштування")
        self.content = ft.Column(
            controls=[
                self.dev_mode_switch
            ],
            height=100,
            width=300,
            tight=True
        )
        self.actions = [
            ft.TextButton("Закрити", on_click=self.close_dialog)
        ]

    def on_switch_change(self, e):
        self.on_dev_mode_change(e.control.value)

    def close_dialog(self, e):
        self.page.close(self)

    def show(self):
        self.page.open(self)
