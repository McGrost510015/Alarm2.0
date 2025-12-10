import flet as ft
from ui.components.map_component import REGION_MAPPING

class SettingsDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, on_dev_mode_change, on_region_changed):
        super().__init__()
        self.page = page
        self.on_dev_mode_change = on_dev_mode_change
        self.on_region_changed = on_region_changed
        
        # Load saved region from client storage
        # DEFERRED to show() to avoid TimeoutError
        # saved_region = self.page.client_storage.get("user_region")
        
        self.dev_mode_switch = ft.Switch(
            label="Режим розробника",
            value=False,
            on_change=self.on_switch_change
        )
        
        # Sort regions alphabetically
        regions = sorted(REGION_MAPPING.keys())
        # Add "None" option
        options = [ft.dropdown.Option("Не обрано")] + [ft.dropdown.Option(r) for r in regions]
        
        self.region_dropdown = ft.Dropdown(
            label="Ваш регіон",
            hint_text="Оберіть область",
            options=options,
            value="Не обрано", # Default, updated in show()
            on_change=self.on_region_change,
            width=280
        )
        
        self.title = ft.Text("Налаштування")
        self.content = ft.Column(
            controls=[
                self.region_dropdown,
                ft.Divider(),
                self.dev_mode_switch
            ],
            height=200,
            width=300,
            tight=True
        )
        self.actions = [
            ft.TextButton("Закрити", on_click=self.close_dialog)
        ]

    def on_switch_change(self, e):
        self.on_dev_mode_change(e.control.value)
        
    def on_region_change(self, e):
        val = e.control.value
        if val == "Не обрано":
            self.page.client_storage.remove("user_region")
            self.on_region_changed(None)
        else:
            self.page.client_storage.set("user_region", val)
            self.on_region_changed(val)

    def close_dialog(self, e):
        self.page.close(self)

    def show(self):
        # Load saved region just before showing to ensure client is ready
        # and to avoid TimeoutError during app startup
        try:
            saved_region = self.page.client_storage.get("user_region")
            self.region_dropdown.value = saved_region if saved_region else "Не обрано"
            
            # Note: We do NOT call .update() here because the dialog isn't open yet.
            # Setting .value is enough; it will render correctly when opened.
            
            # Also update the cache in main
            self.on_region_changed(saved_region)
        except Exception as e:
            print(f"Error loading settings: {e}")
            
        self.page.open(self)
