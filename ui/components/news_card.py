import flet as ft
from datetime import datetime
import threading

class NewsCard(ft.Container):
    def __init__(self, title: str, text: str, footer: str, created_at: str, bg_color: str, original_text: str = None, animate_entrance: bool = True):
        super().__init__()
        self.title = title
        self.text = text
        self.footer = footer
        self.created_at = created_at
        self.original_text = original_text # Store for potential future use (e.g. detailed view)
        
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
        self.bgcolor = bg_color # Set bgcolor early so _build_front_content can use it
        
        self.content = self._build_front_content()
        
        self.border_radius = 12
        self.padding = 20
        # Add horizontal margin to allow scaling without hitting screen edges
        # Increased to 20 to prevent clipping when scaling up by 1.05
        self.margin = ft.margin.symmetric(vertical=10, horizontal=20) 
        
        # Animations - Smoother curves and slightly longer duration
        self.animate_scale = ft.Animation(400, ft.AnimationCurve.EASE_OUT_QUINT)
        self.animate_opacity = ft.Animation(600, ft.AnimationCurve.EASE_OUT_QUINT)
        self.animate_offset = ft.Animation(600, ft.AnimationCurve.EASE_OUT_QUINT)
        
        self.animate_scale = ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT)
        # We use separate scale property for hover (scale) and horizontal flip 
        # Flet has `ft.Scale(scale_x, scale_y)`
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
            self.offset = ft.Offset(0, 0.2) # Start slightly lower
        else:
            self.opacity = 1
            self.offset = ft.Offset(0, 0)

    def did_mount(self):
        if self.should_animate:
            # Use a small delay to ensure the initial state (opacity=0) is rendered
            threading.Timer(0.05, self._animate_in).start()

    def _animate_in(self):
        self.opacity = 1
        self.offset = ft.Offset(0, 0)
        self.update()

    def hover_card(self, e):
        # Hover scales generic scale property (both x and y)
        if isinstance(self.scale, ft.Scale):
             # We want to keep current X scale (which might be 0 during flip, or -1/1)
             # But Hover usually implies 'growing'.
             # If we are valid (scale_x != 0), we apply hover on top?
             # That requires modifying the ft.Scale object IN PLACE.
             
             # Simpler approach for now: Just ignore hover scale if we are handling complex flip scale
             # Or: Update strict values.
             
             # Let's just update the cached object.
             # Note: Hover applies 1.05. if we set self.scale = 1.05 it might break the Flip Scale object.
             # So we must modify self.scale.scale_x and scale_y.
             
             # Current Flip State determines sign of X? 
             # No, Flip sets X to 1 or -1? No, 1.
             
             scale_factor = 1.05 if e.data == "true" else 1.0
             self.scale.scale = scale_factor # 'scale' property of ft.Scale object sets uniform scale?
             # No, ft.Scale has scale, scale_x, scale_y arguments in init, but properties?
             # scale (float), scale_x (float), scale_y (float).
             
             # If we set self.scale.scale = 1.05, does it override scale_x? 
             # Usually Flet layout logic: if scale is set, it overrides others? or multiplies?
             # Docs say: `scale` is a property of Control. It accepts float or Scale object.
             # Scale object has `scale` property? No. It has `x` and `y`?
             
             # Wait, `ft.Scale(scale=...)` ?
             # Init: Scale(scale: Optional[Union[float, int]] = 1, scale_x: Optional[Union[float, int]] = None, scale_y: Optional[Union[float, int]] = None, ...)
             
             # So we can set self.scale.scale = 1.05?
             pass
        else:
             self.scale = 1.05 if e.data == "true" else 1.0
             self.update()
        
    def flip_card(self, e):
        # 1. Scale X to 0 (Squeeze)
        # Create NEW Scale object to ensure Flet detects the change and animates it
        self.scale = ft.Scale(0, 1)
        self.update()
        
        # Wait for the squeeze animation to finish (matching animate_scale duration)
        threading.Timer(0.3, self._swap_content).start()
        
    def _swap_content(self):
        self.is_front = not self.is_front
        
        if self.is_front:
            self.content = self._build_front_content()
        else:
            self.content = self._build_back_content()
            
        # 2. Scale X back to 1 (Expand)
        self.scale = ft.Scale(1, 1)
        self.update()

    def _build_front_content(self):
        # Determine Indicator Color (same logic as init)
        indicator_color = ft.Colors.GREY_400
        if self.bgcolor == ft.Colors.GREEN_700: indicator_color = ft.Colors.GREEN_400
        elif self.bgcolor == ft.Colors.YELLOW_700: indicator_color = ft.Colors.YELLOW_400
        elif self.bgcolor == ft.Colors.ORANGE_700: indicator_color = ft.Colors.ORANGE_400
        elif self.bgcolor == ft.Colors.RED_700: indicator_color = ft.Colors.RED_400
        elif self.bgcolor == ft.Colors.BLUE_GREY_700: indicator_color = ft.Colors.BLUE_400
        
        text_color = ft.Colors.WHITE
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(width=16, height=16, bgcolor=indicator_color, border_radius=8, border=ft.border.all(1.5, ft.Colors.BLACK)),
                        ft.Text(self.title, weight=ft.FontWeight.BOLD, color=text_color, size=16),
                        ft.Container(expand=True),
                        ft.Text(self.created_at, color=text_color, size=12),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(color=ft.Colors.WHITE24, height=1),
                ft.Text(self.text, color=text_color, size=16, weight=ft.FontWeight.BOLD),
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
                ft.Divider(color=ft.Colors.WHITE54, height=1), # Slightly more visible divider
                ft.Container(
                    content=ft.Text(
                        self.original_text if self.original_text else "Текст відсутній", 
                        size=16, # Increased from 14
                        color=ft.Colors.WHITE, 
                        selectable=True,
                        weight=ft.FontWeight.W_500 # Slightly bolder
                    ),
                    expand=True,
                ),
             ],
             spacing=10
        )
