"""
An easily customizable Slider widget for Textual.

Features:
- Fairly precise numeric ranges at unprecedented scale
- Optional built-in Label display
- Handle dragging
- Snap to Track position
- Scroll wheel stepping
- Fully reactive propertied
- Customizations of visuals:
   a. Handle Type
   b. Handle Color
   c. Grip Color
   d. Track Color
   e. Track Width
   f. Tick Display
   g. Label Display
   h. Label Ranges
"""

from textual.widget import Widget
from textual.widgets import Label, Input
from textual.geometry import clamp
from textual.color import Color
from textual.containers import Container
from textual.renderables.bar import Bar
from textual.events import (
    Enter, Leave,
    MouseMove, MouseDown, MouseUp,
    MouseScrollUp, MouseScrollDown,
    Click,
    Key
)
from textual.reactive import reactive
from textual import on
from rich.text import Text
from math import log10

__all__ = ["Slider"]

class Track(Widget): #{
    def __init__(self, color: str, width: int, **kwargs): #{
        super().__init__(**kwargs)
        self.color = color
        self.width = width
        self.styles.width = self.width
        self.styles.height = 1

    def render(self) -> Bar: #{
        return Bar(
            highlight_range = (0, 0),
            highlight_style = "white",
            background_style = self.color,
            width = self.width
        )
    #}
#}
    

class Handle(Widget): #{
    def __init__(self, hand_type: str, g_color: str, color: Color, **kwargs): #{
        super().__init__(**kwargs)
        self.styles.width = 3
        self.styles.height = 1
        self.handle_color = color
        self.highlight = False

        self.styles.background = color
        self.styles.outline = (hand_type, g_color)

        # Correct attribute
        self.offset = (0, -1)
    #}

    def apply_highlight(self) -> None: #{
        self.highlight = True
        self.styles.background = self.styles.background.blend (
            Color(240, 240, 240, 0.50),
            0.025
        )
    #}

    def remove_highlight(self) -> None: #{
        self.highlight = False
        self.styles.background = self.handle_color
    #}
    
    def render(self) -> Text: #{
         return Text(" ")
    #}
#}

class Slider(Container): #{

    DEFAULT_CSS = """
    Slider {
    
        layers: back front;

        & > #value_input {
            layer: front;
            dock: top;
        }

        align: center middle;

        & > Label {
            text-align: center;
        }

        & > Input {
            margin-right: 1;
            border: vkey #1c0917
        }
    }"""

    posVal = reactive(0.0)
    
    def __init__(
        self,
        show_label = False,
        label_min = 0,
        label_max = 100,
        label_color = Color.parse("antiquewhite"),
        step = 1,
        tr_width = 60,
        **kwargs
    ): #{
        super().__init__(**kwargs)

        self.track_color = "#0C0C0C"
        self.track_width = tr_width if (tr_width >= 20) else 60
        self.handle_type = "panel"
        self.handle_color = Color(56, 40, 28, 0.75)
        self.grip_color = "#C6BABCD7"
        self.label_min = label_min if label_max > label_min else 0
        self.label_max = label_max if label_max > label_min else 100
        self.span = (self.label_max - self.label_min)
        self.step = step if (step > 0 and step < self.span) else 1
        self.density = self.span / (tr_width * pow(10, int(log10(self.step))))
        self.value = 0
        
        self.label = Label(str(label_min), id="label") if show_label else None

        self.track = Track(
            color=self.track_color,
            width=self.track_width,
            id="track"
        )
        self.handle = Handle(
            hand_type=self.handle_type,
            g_color=self.grip_color,
            color=self.handle_color,
            id="handle"
        )
        
        self.dragging = False
        self.drag_start_screen_x = 0
        self.handle_start_offset = 0

        if show_label: self.label.styles.color = label_color
        
        self.styles.height = 4
        self.styles.width = tr_width + 2
    #}

    def compose(self): #{
        if self.label: #{
            self.label.styles.width = self.track_width
            self.label.styles.text_align = "center"
            self.label.styles.margin = (1,0,0,0)
            yield self.label
        #}

        yield self.track
        yield self.handle
    #}

    # -----------------------------
    # Dragging
    # -----------------------------

    def offset_from_value(self, value: float) -> int: #{
        span = self.label_max - self.label_min
        max_offset = self.track_width - 2

        ratio = (value - self.label_min) / span
        return (int(round(ratio * max_offset))) if ratio else 0
    #}

    def value_from_offset(self, offset: int) -> float: #{
        max_offset = self.track_width - 3

        ratio = offset / max_offset
        value = ratio * self.span

        # snap to step
        stepped = value // self.step * self.step
        return clamp(self.label_min + stepped, self.label_min, self.label_max) if offset != max_offset else self.label_max
    #}

    def on_mount(self): #{            
        self.value = self.label_min if self.label_min >= 0 or self.label_max <= 0 else 0
        self.posVal = self.value
        self.can_focus = True

        if self.styles.border: #{
            self.styles.width = self.track_width + 4
            self.styles.height = 6
        #}
    #}

    def on_mouse_down(self, event: MouseDown) -> None: #{
        x,y,w,h = self.handle.region
        
        if (event.screen_y < y or event.y): #{
            return
        #}

        self.dragging = True
        
        self.capture_mouse()
        
        self.drag_start_screen_x = event.screen_x
        new_offset = clamp(
            (event.x + self.handle.offset.x) if (self.handle.is_mouse_over) else event.x,
            0,
            self.track_width
        ) - 1
            
        self.handle.offset = (new_offset if new_offset > 1 else 0, -1)
        
        # Store drag start info
        self.handle_start_offset = new_offset

        # Convert offset → value using unified math
        self.posVal = self.value_from_offset(new_offset)
    #}

    def on_mouse_move(self, event: MouseMove) -> None: #{
        if not self.dragging: #{
            return
        #}

        delta = event.screen_x - self.drag_start_screen_x
        new_offset = clamp(self.handle_start_offset + delta, 0, self.track_width - 2)

        self.handle.offset = (new_offset, -1)

        # Convert offset → value using unified math
        self.posVal = self.value_from_offset(new_offset)
    #}

    def on_mouse_up(self) -> None: #{
        
        if self.dragging: #{
            self.dragging = False
            self.release_mouse()
            self.handle.remove_highlight()
        #}
    #}

    def on_key(self, event) -> None:#{
        if event.key == "escape" and self.val_input != None and self.val_input.has_focus: #{
            self.val_input.remove()
        #}

        if event.key in ("a", "ctrl+a") and self.has_focus_within: self.posVal = clamp(self.posVal - self.step * (10**(int(log10(self.density)) - 3) if self.span > 1000 else 10) / (10 if event.key == "ctrl+a" else 1), self.label_min, self.label_max)
        if event.key in ("d", "ctrl+d") and self.has_focus_within: self.posVal = clamp(self.posVal + self.step * (10**(int(log10(self.density)) - 3) if self.span > 1000 else 10) / (10 if event.key == "ctrl+d" else 1), self.label_min, self.label_max)
    #}

    @on(Click, "#label")
    def add_form(self) -> None: #{
        self.val_input = Input(
            id="value_input",
            validate_on=["submitted"]
        )
        
        self.mount(self.val_input)
        self.refresh(layout = True)
        self.val_input.focus()
    #}
    
    @on(Input.Submitted, "#value_input")
    def finalize_input(self, event: Input.Submitted) -> None: #{
        raw = event.value

        # Determine numeric type based on step
        if isinstance(self.step, int): #{
            try: #{
                new_value = int(raw)
            #}
            except ValueError: #{
                new_value = self.value
            #}
        #}
        else: #{
            try: #{
                new_value = float(raw)
            #}
            except ValueError: #{
                new_value = self.value
            #}
        #}

        # Update internal value
        self.value = clamp(round(new_value/self.step) * self.step, self.label_min, self.label_max)

        self.posVal = self.value
        
        new_offset = clamp( self.offset_from_value(self.posVal), 0, self.track_width - 2)

        self.handle.offset = (new_offset, -1)

        # Update label text
        self.watch_posVal(self.posVal)

        # Remove the input overlay
        self.val_input.remove()
    #}

    # -----------------------------
    # Scroll wheel
    # -----------------------------

    @on(MouseScrollUp)
    def scroll_up(self, event) -> None: #{
        check = int(log10(self.step) - 1)
        
        self.posVal = clamp(
            self.posVal + (
                self.step if ( self.density < 100000 ) else (
                    self.step * 5 if ( self.density < 500000 ) else (
                        self.step * 5 * (10**(int(log10(self.density)) + round(log10(self.step)) + 3) if ((check <= -5)) else 2)
                    )                
                )
            ) * (1 if event.ctrl else (400 if self.density > 100000 else 5)),
            self.label_min,
            self.label_max
        )
    #}
        
    @on(MouseScrollDown)
    def scroll_down(self, event) -> None: #{
        check = int(log10(self.step) - 1)
        
        self.posVal = clamp(
            self.posVal - (
                self.step if ( self.density < 100000 ) else (
                    self.step * 5 if ( self.density < 500000 ) else (
                        self.step * 5 * (10**(int(log10(self.density)) + round(log10(self.step)) + 3) if ((check <= -5)) else 2)
                    )                
                )
            ) * (1 if event.ctrl else (400 if self.density > 100000 else 5)),
            self.label_min,
            self.label_max
        )
    #}

    @on(Enter)
    def ready(self) -> None: #{
        if not self.dragging: #{
            self.handle.apply_highlight()
        #}
    #}

    @on(Leave)
    def not_ready(self) -> None: #{
        if not self.dragging: #{
            self.handle.remove_highlight()
        #}
    #}
    
    # -----------------------------
    # Reactive watcher
    # -----------------------------

    def watch_posVal(self, new_value: float) -> None: #{
        
        if new_value >= self.label_max: #{
            new_value = self.label_max
        #}
        
        elif new_value <= self.label_min: #{
            new_value = self.label_min
        #}

        else: #{
            new_value = round(new_value / self.step)
            new_value = clamp(new_value * self.step, self.label_min, self.label_max)
        #}

        self.value = new_value 
        
        val_str = f"{self.value:.8f}"
        
        if "." in val_str: #{
            while True: #{
                last = val_str[-1]

                if last == "0": #{
                    val_str = val_str[:-1]
                    continue
                #}
                
                if last == ".": #{
                    val_str = val_str[:-1]
                    break
                #}

                break
            #}
        #}

        if self.label: self.label.update(val_str)
        
        if not self.dragging: #{
            new_offset = self.offset_from_value(new_value)
            self.handle.offset = (new_offset, -1)

            if self.handle.highlight: self.handle.remove_highlight()
        #}
        
        else: #{
            if not self.handle.highlight: self.handle.apply_highlight()
        #}

        self.focus()
    #}
#}
