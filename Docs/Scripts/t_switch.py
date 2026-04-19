"""
An easily customizable Switch widget for Textual. It handles boolean flags with assigning the displayed labels for the boolean states

Features:
- Optional built-in Label display
- Customizations of visuals:
   a. Handle Type
   b. Handle Color
   c. Grip Color
   f. Tick Display
   g. Label Display
   h. On/Off Monikers
"""

from textual.widget import Widget
from textual.widgets import Label
from textual.geometry import clamp
from textual.color import Color
from textual.containers import Container
from textual.renderables.bar import Bar
from textual.events import (
    MouseScrollUp, MouseScrollDown,
    Click
)

from textual import on
from rich.text import Text

__all__ = ["Switch"]

class _Track(Widget):
    def __init__(self, color: str, width: int, **kwargs):
        super().__init__(**kwargs)
        self.color = color
        self.width = width
        self.styles.width = width
        self.styles.height = 1

    def render(self) -> Bar:
        return Bar(
            highlight_range=(0, 0),
            highlight_style="white",
            background_style=self.color,
            width=self.width
        )

class _Handle(Widget):
    def __init__(self, hand_type: str, g_color: str, color: Color, **kwargs):
        super().__init__(**kwargs)
        self.styles.width = 3
        self.styles.height = 1
        self.handle_color = color
        self.highlight = False

        if hand_type not in ("tall", "hkey", "outer", "panel"):
            hand_type = "vkey"

        self.styles.background = self.handle_color
        self.styles.outline = (hand_type, g_color)

        # Correct attribute
        self.offset = (0, -1)

    def apply_highlight(self) -> None:
        self.highlight = True
        self.styles.background = self.styles.background.blend(
            Color(240, 240, 240, 0.50),
            0.05
        )

    def remove_highlight(self) -> None:
        self.highlight = False
        self.styles.background = self.handle_color

    def render(self) -> Text:
        return Text(" ")

class Switch(Container):

    DEFAULT_CSS = """
    Switch {
        content-align: center middle;

        & > Label {
            text-align: center;
        }
    }"""
    
    def __init__(self,
        show_label = True,
        off_label = "Off",
        on_label = "On",
        default = "Off",
        label_color = Color.parse("antiquewhite"),
        bg_color = Color.parse("dimgrey"),
        border_type = "outer",
        border_color = "antiquewhite",
        g_color = "#0C0C0C",
        h_type = "hkey",
        h_color = Color.parse("wheat"),
        **kwargs
    ):
        super().__init__(**kwargs)

        self.track_color = "#0C0C0C"
        self.track_width = 5
        self.handle_type = h_type if isinstance(h_type, str) else "vkey"
        self.handle_color = h_color if isinstance(h_color, Color) else Color(56, 40, 28, 0.75)
        self.grip_color = g_color if isinstance (g_color, str) else "#C4BFB2D7"
        self.default = default if default in (on_label, off_label) else off_label
        
        self.off_label = off_label
        self.on_label = on_label
        self.label = Label(self.default, id="label") if show_label else None

        self.track = _Track (
            color = self.track_color,
            width = self.track_width,
            id="track"
        )
        
        self.handle = _Handle (
            hand_type = self.handle_type,
            g_color = self.grip_color,
            color = self.handle_color,
            id="handle"
        )
        
        self.value = 0 if self.default == off_label else 1
        self.handle.offset = ((self.track_width - 2) if self.value else 0, -2)

        self.styles.height = 8 if self.label else 5
        self.styles.width = 10
        
        if self.label: self.label.styles.color = label_color
        
        self.styles.border = (
            border_type if border_type in ("inner", "panel", "thick") else "outer",
            border_color
        )
        self.styles.align = ("center", "middle")
        self.styles.background = bg_color

    def compose(self):
        if self.label:
            self.label.styles.width = self.track_width 
            self.label.styles.text_align = "center"
            self.label.styles.margin = 1
            yield self.label

        self.track.styles.margin = 1
        self.handle.styles.margin = 1
        yield self.track
        yield self.handle

    def on_mount(self):
        if self.label: self.label.disabled = True

    def flip(self):
        x, y = self.handle.offset
        if x >= 1:
            self.value = 0
            self.handle.offset = (0, -2)
            if self.label: self.label.update(self.off_label)
        else:
            self.value = 1
            self.handle.offset = (self.track_width - 2, -2)
            if self.label: self.label.update(self.on_label)

    @on(Click)
    def click_switch(self, event) -> None:  
        self.flip()
    
    # -----------------------------
    # Scroll wheel
    # -----------------------------
    
    @on(MouseScrollUp)
    def scroll_up(self) -> None:
        self.value = 1
        self.handle.offset = (self.track_width - 2, -2)
        if self.label: self.label.update(self.on_label)
        
    @on(MouseScrollDown)
    def scroll_down(self) -> None:
        self.value = 0
        self.handle.offset = (0, -2)
        if self.label: self.label.update(self.off_label)
