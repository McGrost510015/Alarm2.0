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
        active_ids = set()
        for region_name, data in states.items():
            if data.get("alertnow"): # Boolean true
                svg_id = REGION_MAPPING.get(region_name)
                if svg_id:
                    active_ids.add(svg_id)
        
        # Iterate all paths and update fill
        for elem in self.root.iter():
            if elem.tag.endswith('path'):
                elem_id = elem.get("id")
                if elem_id:
                    if elem_id in active_ids:
                        elem.set("fill", "#CC0000") # Alert Color (Red)
                    else:
                        elem.set("fill", "#2D2D2D") # Neutral Dark Grey

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
