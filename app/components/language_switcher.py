"""
Simple Language Switcher - Just Text Links
"""

import reflex as rx


class LangState(rx.State):
    """Simple language state"""
    lang: str = "en"
    
    def set_en(self):
        self.lang = "en"
    
    def set_ms(self):
        self.lang = "ms"


def language_switcher():
    """Simple text-based language switcher"""
    return rx.box(
        rx.text(
            "🇬🇧 EN",
            on_click=LangState.set_en,
            style={
                "cursor": "pointer",
                "padding": "0.5rem",
                "font-weight": "bold" if LangState.lang == "en" else "normal",
                "color": "#2563eb" if LangState.lang == "en" else "#6b7280",
            },
        ),
        rx.text(
            "🇲🇾 MS",
            on_click=LangState.set_ms,
            style={
                "cursor": "pointer",
                "padding": "0.5rem",
                "font-weight": "bold" if LangState.lang == "ms" else "normal",
                "color": "#2563eb" if LangState.lang == "ms" else "#6b7280",
            },
        ),
        style={
            "display": "flex",
            "gap": "0.5rem",
            "align-items": "center",
        }
    )
