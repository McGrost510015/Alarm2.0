import flet as ft
from datetime import datetime
import threading

class NewsCard(ft.Container):
    def __init__(self, title: str, text: str, footer: str, created_at: str, bg_color: str, animate_entrance: bool = True):
        super().__init__()
        self.title = title
        self.text = text
        self.footer = footer
        self.created_at = created_at
        
        # Determine Indicator Color
        # We use brighter shades for the dot to pop against the card background
        indicator_color = ft.Colors.GREY_400
        if bg_color == ft.Colors.GREEN_700:
            indicator_color = ft.Colors.GREEN_400
        elif bg_color == ft.Colors.YELLOW_700:
            indicator_color = ft.Colors.YELLOW_400
        elif bg_color == ft.Colors.ORANGE_700:
            indicator_color = ft.Colors.ORANGE_400
        elif bg_color == ft.Colors.RED_700:
            indicator_color = ft.Colors.RED_400
        elif bg_color == ft.Colors.BLUE_GREY_700:
            indicator_color = ft.Colors.BLUE_400
            
        text_color = ft.Colors.WHITE
        
        self.content = ft.Column(
            controls=[
                # Header Row
                ft.Row(
                    controls=[
                        # Styled Circle Indicator
                        ft.Container(
                            width=16,
                            height=16,
                            bgcolor=indicator_color,
                            border_radius=8, # Circle
                            border=ft.border.all(1.5, ft.Colors.BLACK), # Black Outline
                        ),
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
        
        self.bgcolor = bg_color
        self.border_radius = 12
        self.padding = 20
        # Add horizontal margin to allow scaling without hitting screen edges
        # Increased to 20 to prevent clipping when scaling up by 1.05
        self.margin = ft.margin.symmetric(vertical=10, horizontal=20) 
        
        # Animations - Smoother curves and slightly longer duration
        self.animate_scale = ft.Animation(400, ft.AnimationCurve.EASE_OUT_QUINT)
        self.animate_opacity = ft.Animation(600, ft.AnimationCurve.EASE_OUT_QUINT)
        self.animate_offset = ft.Animation(600, ft.AnimationCurve.EASE_OUT_QUINT)
        
        # Initial State
        self.should_animate = animate_entrance
        if self.should_animate:
            self.opacity = 0
            self.offset = ft.Offset(0, 0.2) # Start slightly lower
        else:
            self.opacity = 1
            self.offset = ft.Offset(0, 0)
            
        self.scale = 1.0
        
        self.on_hover = self.hover_card

    def did_mount(self):
        if self.should_animate:
            # Use a small delay to ensure the initial state (opacity=0) is rendered
            threading.Timer(0.05, self._animate_in).start()

    def _animate_in(self):
        self.opacity = 1
        self.offset = ft.Offset(0, 0)
        self.update()

    def hover_card(self, e):
        self.scale = 1.05 if e.data == "true" else 1.0
        self.update()

