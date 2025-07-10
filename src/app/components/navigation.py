# components/navigation.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class NavigationToolbar:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.frame = None
        self.nav_buttons = []
        self.ocr_button = None
        self._create_frame()

    def _create_frame(self):
        """Initialize the toolbar container"""
        self.frame = tb.Frame(self.parent, padding=10)
        self.frame.grid(row=0, column=0, sticky="ew")
        self._create_buttons()

    def _create_buttons(self):
        """Create navigation buttons using configuration"""
        button_config = [
            ("Browse", "browse", OUTLINE),
            ("Previous", "previous_image", OUTLINE),
            ("Next", "next_image", OUTLINE),
            ("Rotate Left", "rotate_left", OUTLINE),
            ("Rotate Right", "rotate_right", OUTLINE),
            ("OCR", "ocr", OUTLINE),
            ("Update Data", "update_data", OUTLINE),
            ("Save", "save_data", OUTLINE),
            ("Options", "options", OUTLINE),
        ]

        for col, (text, command, style) in enumerate(button_config):
            btn = tb.Button(
                self.frame,
                text=text,
                command=lambda cmd=command: self._handle_command(cmd),
                bootstyle=style
            )
            btn.grid(row=0, column=col, padx=5, ipadx=10, sticky="ew")
            self.frame.columnconfigure(col, weight=1)
            
            # Track special buttons
            if text in ["Previous", "Next"]:
                self.nav_buttons.append(btn)
            elif text == "OCR":
                self.ocr_button = btn

    def _handle_command(self, command_name):
        """Route commands to controller"""
        handler = getattr(self.controller, command_name, None)
        if handler:
            handler()
        else:
            print(f"No handler found for command: {command_name}")

    def set_button_state(self, button_type, state):
        """Control button states"""
        if button_type == "navigation":
            for btn in self.nav_buttons:
                btn.config(state=state)
        elif button_type == "ocr":
            self.ocr_button.config(state=state)