import flet as ft
from datetime import datetime

class NewsCard(ft.Container):
    def __init__(self, title: str, text: str, footer: str, created_at: str, bg_color: str):
        super().__init__()
        self.title = title
        self.text = text
        self.footer = footer
        self.created_at = created_at
        
        # Colors passed directly from logic
        main_color = bg_color
        text_color = ft.Colors.WHITE
        
        self.content = ft.Column(
            controls=[
                # Header Row
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE, color=text_color),
                        ft.Text(self.title, weight=ft.FontWeight.BOLD, color=text_color, size=16),
                        ft.Container(expand=True),
                        ft.Text(self.created_at, color=text_color, size=12),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(color=ft.Colors.WHITE24, height=1),
                # Body Text
                ft.Text(self.text, color=text_color, size=16, weight=ft.FontWeight.BOLD),
                # Footer
                ft.Text(self.footer, color=ft.Colors.WHITE70, size=12, italic=True),
            ],
            spacing=10,
        )
        
        self.bgcolor = main_color
        self.border_radius = 10
        self.padding = 15
        self.margin = ft.margin.only(bottom=10)

