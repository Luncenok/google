
from reportlab.lib.colors import HexColor

TEMPLATES = {
    "classic": {
        "layout": {
            "show_image": True,
            "header_style": "basic",
        },
        "colors": {
            "primary": HexColor("#2c3e50"),
            "secondary": HexColor("#34495e"),
            "text": HexColor("#2c3e50"),
            "skill_bg": HexColor("#ecf0f1"),
        }
    },
    "modern": {
        "layout": {
            "show_image": False,
            "header_style": "compact",
        },
        "colors": {
            "primary": HexColor("#1E3A8A"),
            "secondary": HexColor("#374151"),
            "text": HexColor("#111827"),
            "skill_bg": HexColor("#E5E7EB"),
        }
    }
}
