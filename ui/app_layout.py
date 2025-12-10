import flet as ft
import json
import os
from ui.components.news_card import NewsCard
from ui.components.developer_console import DeveloperConsole
from ui.components.map_component import MapComponent

HISTORY_FILE = "history.json"

class AppLayout(ft.Row):
    def __init__(self, page: ft.Page, on_clear_history=None, on_pulse_click=None):
        super().__init__()
        self.page = page
        self.news_list_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)
        
        self.show_ignored_news = False

        self.console = DeveloperConsole(
            on_clear_history_click=on_clear_history, 
            on_pulse_click=on_pulse_click,
            on_toggle_ignored_click=self.toggle_ignored_view
        )
        self.map = MapComponent()
        
        # Center Content: Map (initially visible? Request said: "Center if dev mode, Right if not")
        # Actually request said: "central part if developer mode is enabled, or right part if disabled"
        # Since I'm using Row:
        # [News] [Map] [Console]
        # If Dev Mode OFF: Console hidden. [News] [Map] (Map on right)
        # If Dev Mode ON: Console visible. [News] [Map] [Console] (Map in center)
        
        self.controls = [
            # Main Content (News)
            ft.Container(
                content=self.news_list_container,
                expand=2, # Less weight than map
                padding=10
            ),
            # Map
            ft.Container(
                content=self.map,
                expand=3 # More weight
            ),
            # Console (Right Side)
            self.console
        ]
        self.expand = True
        self.vertical_alignment = ft.CrossAxisAlignment.START
        
        self.load_history()

    def toggle_ignored_view(self, show):
        self.show_ignored_news = show
        try:
            self.console.log(f"Ignored News Visibility: {show}")
        except:
            pass
            
        for control in self.news_list_container.controls:
            if isinstance(control, NewsCard) and control.data == "ignore":
                control.visible = show
        self.page.update()

    def update_map(self, states):
        self.map.update_alerts(states)

    def highlight_regions(self, region_names):
        self.map.set_highlights(region_names)
        
    def add_news(self, title, text, footer, time, bg_color, original_text=None, save=True, animate=True, regions=None, status="normal"):
        # Add new card to the top
        # For new items (save=True), we animate. For history (usually save=False), we can skip animation or fast forward.
        # But user wants smooth appearance for NEW news.
        
        is_ignored = (status == "ignore")
        visible = True
        if is_ignored:
            visible = self.show_ignored_news
            
        card = NewsCard(
            title, text, footer, time, bg_color, 
            original_text=original_text, 
            animate_entrance=animate,
            regions=regions, 
            on_highlight=self.highlight_regions
        )
        
        if is_ignored:
            card.data = "ignore"
            card.visible = visible
            
        self.news_list_container.controls.insert(0, card)
        
        # Update page to render the card in its initial (offset/transparent) state
        self.page.update()
        
        # dynamic animation handled in did_mount via threading
        
        if save:
            self.save_news_item({
                "title": title,
                "text": text,
                "footer": footer,
                "time": time,
                "bg_color": bg_color,
                "original_text": original_text,
                "regions": regions,
                "status": status
            })

    def save_news_item(self, item):
        history = []
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception as e:
                self.log(f"Error reading history: {e}")
        
        history.insert(0, item) # Prepend
        
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"Error saving history: {e}")

    def load_history(self):
        if not os.path.exists(HISTORY_FILE):
            return
            
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
                
            # Iterate in reverse order so we insert them and they end up in correct order (or just insert at end?)
            # add_news inserts at 0. So if history is [Newest, ..., Oldest]
            # We should add Oldest first?
            # actually add_news inserts at 0.
            # If load_history reads [Item1, Item2, Item3] where Item1 is newest.
            # We should add Item3, then Item2, then Item1.
            
            for item in reversed(history):
                self.add_news(
                    item.get("title"),
                    item.get("text"),
                    item.get("footer"),
                    item.get("time"),
                    item.get("bg_color"),
                    original_text=item.get("original_text"),
                    save=False,
                    animate=False,
                    regions=item.get("regions"),
                    status=item.get("status", "normal")
                )
        except Exception as e:
            self.log(f"Error loading history: {e}")

    def clear_history(self, e):
        self.news_list_container.controls.clear()
        
        # Clear file
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
            self.console.log("History cleared.")
        except Exception as e:
            self.console.log(f"Error clearing history file: {e}")
            
        self.page.update()

    def toggle_console(self, visible):
        self.console.visible = visible
        self.page.update()

    def log(self, message):
        if self.console.visible:
            self.console.log(message)
