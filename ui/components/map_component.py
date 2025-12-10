import flet as ft
import xml.etree.ElementTree as ET
import base64

# Mapping from API Region Names -> SVG IDs
# Based on ISO 3166-2:UA and common naming in alerts APIs
REGION_MAPPING = {
    "Вінницька область": "UA-05",
    "Волинська область": "UA-07",
    "Дніпропетровська область": "UA-12",
    "Донецька область": "UA-14",
    "Житомирська область": "UA-18",
    "Закарпатська область": "UA-21",
    "Запорізька область": "UA-23",
    "Івано-Франківська область": "UA-26",
    "Київська область": "UA-32", # Usually 32 is region, 30 is city. Need to check svg for both or just one.
    "м. Київ": "UA-30",
    "Кіровоградська область": "UA-35",
    "Луганська область": "UA-09",
    "Львівська область": "UA-46",
    "Миколаївська область": "UA-48",
    "Одеська область": "UA-51",
    "Полтавська область": "UA-53",
    "Рівненська область": "UA-56",
    "Сумська область": "UA-59",
    "Тернопільська область": "UA-61",
    "Харківська область": "UA-63",
    "Херсонська область": "UA-65",
    "Хмельницька область": "UA-68",
    "Черкаська область": "UA-71",
    "Чернівецька область": "UA-77",
    "Чернігівська область": "UA-74",
    "Автономна Республіка Крим": "UA-43",
    "м. Севастополь": "UA-40"
}

class MapComponent(ft.Container):
    def __init__(self, svg_path="ukraine.svg"):
        super().__init__()
        self.svg_path = svg_path
        self.tree = None
        self.root = None
        self.svg_content = ""
        self.image_control = ft.Image(src_base64="", fit=ft.ImageFit.CONTAIN, expand=True)
        self.content = self.image_control
        
        # Explicitly set height/width constraints to ensure it takes space
        # We can remove fixed height if we rely on layout expand, but user wanted it larger.
        # Let's keep expand=True and remove fixed height if layout handles it well.
        # But previous issue was visibility. Let's keep expand=True on Component itself.
        self.expand = True
        
        self.active_alert_ids = set()
        self.highlighted_ids = set()
        
        # Load initial SVG
        self.load_svg()

    def load_svg(self):
        try:
            # Register namespaces to prevent ns0: prefixes
            ET.register_namespace("", "http://www.w3.org/2000/svg")
            ET.register_namespace("mapsvg", "http://mapsvg.com")
            
            self.tree = ET.parse(self.svg_path)
            self.root = self.tree.getroot()
            
            # Fix SVG scaling: Add viewBox if missing
            width = self.root.get('width')
            height = self.root.get('height')
            if width and height:
                 if 'viewBox' not in self.root.attrib:
                     w = width.replace('pt', '').replace('px', '')
                     h = height.replace('pt', '').replace('px', '')
                     self.root.set('viewBox', f"0 0 {w} {h}")
                 
                 # Remove width/height to let Flutter handle scaling via viewBox + fit
                 if 'width' in self.root.attrib: del self.root.attrib['width']
                 if 'height' in self.root.attrib: del self.root.attrib['height']
                 
            # Set default style for all paths
            # SVG uses 'path' elements.
            # We explicitly set fill to a visible neutral color
            for elem in self.root.iter():
                # Namespace handling: ElementTree might tag as {http://www.w3.org/2000/svg}path
                if elem.tag.endswith('path'):
                    # Check if it has an ID, if so, color it neutral
                    if elem.get('id'):
                        elem.set("fill", "#2D2D2D") # Neutral Dark Grey
                        elem.set("stroke", "#606060") # Lighter Grey Stroke
                        elem.set("stroke-width", "1")

            self.update_map_image()
            
        except Exception as e:
            print(f"Error loading SVG: {e}")
            self.content = ft.Text(f"Error loading map.svg: {e}", color=ft.Colors.RED)

    def update_alerts(self, states):
        if not self.root:
            return

        # active_ids = set of IDs that are alerts
        self.active_alert_ids = set()
        for region_name, data in states.items():
            if data.get("alertnow"): # Boolean true
                svg_id = REGION_MAPPING.get(region_name)
                if svg_id:
                    self.active_alert_ids.add(svg_id)
        
        self.render_map_state()

    # Common City/Short names to Full Region Names mapping
    CITY_TO_REGION_MAPPING = {
        "Вінниця": "Вінницька область",
        "Дніпро": "Дніпропетровська область",
        "Донецьк": "Донецька область",
        "Житомир": "Житомирська область",
        "Запоріжжя": "Запорізька область",
        "Івано-Франківськ": "Івано-Франківська область",
        "Київ": "м. Київ", # Or Київська область depending on context, usually City for alerts
        "Кропивницький": "Кіровоградська область",
        "Луганськ": "Луганська область",
        "Луцьк": "Волинська область",
        "Львів": "Львівська область",
        "Миколаїв": "Миколаївська область",
        "Одеса": "Одеська область",
        "Полтава": "Полтавська область",
        "Рівне": "Рівненська область",
        "Суми": "Сумська область",
        "Тернопіль": "Тернопільська область",
        "Ужгород": "Закарпатська область",
        "Харків": "Харківська область",
        "Херсон": "Херсонська область",
        "Хмельницький": "Хмельницька область",
        "Черкаси": "Черкаська область",
        "Чернівці": "Чернівецька область",
        "Чернігів": "Чернігівська область",
        "Сімферополь": "Автономна Республіка Крим",
        "Крим": "Автономна Республіка Крим",
        "Севастополь": "м. Севастополь"
    }

    def set_highlights(self, region_names):
        """Highlight specific regions (e.g. on hover) without changing alert state"""
        if not self.root:
            return
            
        new_highlights = set()
        if region_names:
            if isinstance(region_names, str):
                region_names = [region_names]
                
            for name in region_names:
                name = name.strip()
                svg_id = None
                
                # 1. Direct Match
                svg_id = REGION_MAPPING.get(name)
                
                # 2. City Mapping (Robust)
                if not svg_id:
                    full_name = self.CITY_TO_REGION_MAPPING.get(name)
                    if full_name:
                        svg_id = REGION_MAPPING.get(full_name)
                        
                # 3. "Область" suffix check (e.g. input "Вінницька" -> "Вінницька область")
                if not svg_id and "область" not in name:
                     potential_name = f"{name} область"
                     svg_id = REGION_MAPPING.get(potential_name)

                # 4. Partial / Case-insensitive Search
                if not svg_id:
                     name_lower = name.lower()
                     for key, val in REGION_MAPPING.items():
                         if name_lower in key.lower(): 
                             svg_id = val
                             break

                if svg_id:
                    new_highlights.add(svg_id)
                else:
                    print(f"DEBUG: Could not map region name '{name}' to SVG ID")
        
        print(f"DEBUG: Highlight IDs: {new_highlights}")
        if self.highlighted_ids != new_highlights:
            self.highlighted_ids = new_highlights
            self.render_map_state()

    def render_map_state(self):
        # Iterate all paths and update fill
        for elem in self.root.iter():
            if elem.tag.endswith('path'):
                elem_id = elem.get("id")
                if elem_id:
                    # Priority: Highlight > Alert > Normal
                    # Actually, we might want to show Alert color BUT highlighted (brighter)?
                    # User asked for "Highlight regions on hover".
                    
                    fill_color = "#2D2D2D" # Default
                    stroke_color = "#606060"
                    stroke_width = "1"
                    
                    is_alert = elem_id in self.active_alert_ids
                    is_highlight = elem_id in self.highlighted_ids
                    
                    if is_alert:
                        fill_color = "#CC0000" # Red
                        
                    if is_highlight:
                        # If it's an alert, make it brighter red? or White overlay?
                        if is_alert:
                             fill_color = "#FF3333" # Brighter Red
                             stroke_color = "#FFFFFF"
                             stroke_width = "2"
                        else:
                             fill_color = "#707070" # Much Lighter Grey (Highlight) for visibility
                             stroke_color = "#FFFFFF"
                             stroke_width = "1.5"
                             
                    elem.set("fill", fill_color)
                    elem.set("stroke", stroke_color)
                    elem.set("stroke-width", stroke_width)

        self.update_map_image()

    def update_map_image(self):
        # Serialize XML to string, ensuring we don't mess up encoding
        svg_str = ET.tostring(self.root, encoding='utf8', method='xml').decode('utf8')
        
        # Encode to base64
        b64 = base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')
        
        self.image_control.src_base64 = b64
        self.image_control.src = "" # Ensure we are using base64
        if self.image_control.page:
            self.image_control.update()
