import flet as ft
from datetime import datetime
import threading

class NewsCard(ft.Container):
    def __init__(self, title: str, text: str, footer: str, created_at: str, bg_color: str, original_text: str = None, animate_entrance: bool = True, regions=None, on_highlight=None):
        super().__init__()
        self.title = title
        self.text = text
        self.footer = footer
        self.created_at = created_at
        self.original_text = original_text 
        self.regions = regions
        self.on_highlight = on_highlight
        
        # Map flat colors to Gradients
        # This is a heuristic since we receive 'bg_color' as a string/value from main logic.
        # We can map specific known colors to cool gradients.
        
        self.gradient = None
        # Default fallback
        self.bgcolor = bg_color 
        
        # Define Gradients
        if bg_color == ft.Colors.GREEN_700:
            self.bgcolor = None
            self.gradient = ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.Colors.GREEN_900, ft.Colors.GREEN_500]
            )
            indicator_color = ft.Colors.GREEN_300
        elif bg_color == ft.Colors.YELLOW_700:
            self.bgcolor = None
            self.gradient = ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.Colors.YELLOW_900, ft.Colors.YELLOW_600]
            )
            indicator_color = ft.Colors.YELLOW_300
        elif bg_color == ft.Colors.ORANGE_700:
            self.bgcolor = None
            self.gradient = ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.Colors.ORANGE_900, ft.Colors.ORANGE_500]
            )
            indicator_color = ft.Colors.ORANGE_300
        elif bg_color == ft.Colors.RED_700:
            self.bgcolor = None
            self.gradient = ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.Colors.RED_900, ft.Colors.RED_500]
            )
            indicator_color = ft.Colors.RED_300
        elif bg_color == ft.Colors.BLUE_GREY_700:
            self.bgcolor = None
            self.gradient = ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.Colors.BLUE_GREY_900, ft.Colors.BLUE_GREY_500]
            )
            indicator_color = ft.Colors.BLUE_INFO_200
        else:
             # Fallback for unknown colors
             indicator_color = ft.Colors.GREY_400
            
        text_color = ft.Colors.WHITE
        
        # Helper to rebuild content with correct indicator color
        self.indicator_color = indicator_color 
        self.text_color = text_color
        
        self.border_radius = 12
        self.padding = 20
        self.margin = ft.margin.symmetric(vertical=10, horizontal=20) 
        
        self.animate_scale = ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT)
        self.scale = ft.Scale(1, 1)
        
        self.on_hover = self.hover_card
        self.on_click = self.flip_card

        # Initial Content
        self.is_front = True
        self.content = self._build_front_content()
        
        # Initial State
        self.should_animate = animate_entrance
        
        if self.should_animate:
            self.opacity = 0
            self.offset = ft.Offset(0, 0.2) 
        else:
            self.opacity = 1
            self.offset = ft.Offset(0, 0)

    def did_mount(self):
        if self.should_animate:
            threading.Timer(0.05, self._animate_in).start()

    def _animate_in(self):
        self.opacity = 1
        self.offset = ft.Offset(0, 0)
        self.update()

    def hover_card(self, e):
        is_hovering = (e.data == "true")
        
        if is_hovering:
             self.scale = 1.05
             # Trigger Map Highlight
             if self.on_highlight:
                 print(f"DEBUG: Hovering card. Regions: {self.regions}") # DEBUG LOG
                 if self.regions:
                     self.on_highlight(self.regions)
        else:
             self.scale = 1.0
             # Clear Map Highlight
             if self.on_highlight:
                 self.on_highlight([])

        self.update()
        
    def flip_card(self, e):
        self.scale = ft.Scale(0, 1)
        self.update()
        threading.Timer(0.3, self._swap_content).start()
        
    def _swap_content(self):
        self.is_front = not self.is_front
        
        if self.is_front:
            self.content = self._build_front_content()
        else:
            self.content = self._build_back_content()
            
        self.scale = ft.Scale(1, 1)
        self.update()

    def _build_front_content(self):
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(width=16, height=16, bgcolor=self.indicator_color, border_radius=8, border=ft.border.all(1.5, ft.Colors.BLACK)),
                        ft.Text(self.title, weight=ft.FontWeight.BOLD, color=self.text_color, size=16),
                        ft.Container(expand=True),
                        ft.Text(self.created_at, color=self.text_color, size=12),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(color=ft.Colors.WHITE24, height=1),
                ft.Text(self.text, color=self.text_color, size=16, weight=ft.FontWeight.BOLD),
                ft.Text(self.footer, color=ft.Colors.WHITE70, size=12, italic=True),
            ],
            spacing=10,
        )

    def _build_back_content(self):
        return ft.Column(
             controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.SOURCE, color=ft.Colors.WHITE, size=20),
                        ft.Text("ОРИГІНАЛЬНЕ ДЖЕРЕЛО", size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8
                ),
                ft.Divider(color=ft.Colors.WHITE54, height=1),
                ft.Container(
                    content=ft.Text(
                        self.original_text if self.original_text else "Текст відсутній", 
                        size=16,
                        color=ft.Colors.WHITE, 
                        selectable=False,
                        weight=ft.FontWeight.W_500 
                    ),
                    expand=True,
                ),
             ],
             spacing=10
        )
