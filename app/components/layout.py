import reflex as rx
from .loading_overlay import loading_overlay

def layout(content: rx.Component) -> rx.Component:
    """A global layout wrapper that includes the loading overlay and standard page structure."""
    return rx.fragment(
        loading_overlay(),
        content,
    )
