# components/navigation.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from typing import Any, List, Tuple, Literal


class NavigationToolbar:
    """Manages the navigation toolbar for the application.

    This class creates and controls the buttons for various application actions
    such as browsing images, navigating, rotating, performing OCR, and updating data.

    Attributes:
        parent: The parent widget (e.g., a ttkbootstrap.Window) to which this
            toolbar will be attached.
        controller: An object (expected to be MainUI) that contains methods
            corresponding to the button commands (e.g., `browse`, `next_image`).
        frame: The `ttkbootstrap.Frame` widget that serves as the container for
            all navigation buttons.
        nav_buttons: A list of `ttkbootstrap.Button` widgets specifically for
            image navigation (Previous, Next).
        ocr_button: The `ttkbootstrap.Button` widget for initiating OCR.
    """

    def __init__(self, parent: tb.Window, controller: Any) -> None:
        """Initializes the NavigationToolbar.

        Args:
            parent: The parent widget (e.g., a ttkbootstrap.Window) to which this
                toolbar will be attached.
            controller: An object that contains methods corresponding to the
                button commands.
        """
        self.parent: tb.Window = parent
        self.controller: Any = controller
        self.frame: tb.Frame | None = None
        self.nav_buttons: List[tb.Button] = []
        self.ocr_button: tb.Button | None = None
        self._create_frame()

    def _create_frame(self) -> None:
        """Creates the container frame for the toolbar.

        The frame is a `ttkbootstrap.Frame` and is placed at the top of the
        parent widget's grid. It then calls `_create_buttons` to populate itself.
        """
        self.frame = tb.Frame(self.parent, padding=10)
        self.frame.grid(row=0, column=0, sticky="ew")
        self._create_buttons()

    def _create_buttons(self) -> None:
        """Creates and configures the navigation and action buttons.

        Buttons are created based on `button_config`, assigned commands that
        route through `_handle_command`, and their states are tracked for
        dynamic control.
        """
        button_config: List[Tuple[str, str, str]] = [
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
            btn: tb.Button = tb.Button(
                self.frame,
                text=text,
                command=lambda cmd=command: self._handle_command(cmd),
                bootstyle=style,
            )
            btn.grid(row=0, column=col, padx=5, ipadx=10, sticky="ew")
            self.frame.columnconfigure(col, weight=1)

            if text in ["Previous", "Next"]:
                self.nav_buttons.append(btn)
            elif text == "OCR":
                self.ocr_button = btn

    def _handle_command(self, command_name: str) -> None:
        """Routes button commands to the appropriate controller method.

        Args:
            command_name: The name of the method to call on the controller object.
        """
        handler: Any = getattr(self.controller, command_name, None)
        if handler:
            handler()
        else:
            print(f"No handler found for command: {command_name}")

    def set_button_state(
        self,
        button_type: Literal["navigation", "ocr"],
        state: Literal["normal", "disabled"],
    ) -> None:
        """Controls the enabled/disabled state of specified button types.

        Args:
            button_type: The type of button to control. Can be "navigation" for
                previous/next buttons, or "ocr" for the OCR button.
            state: The desired state for the buttons. Can be "normal" to enable
                or "disabled" to disable.
        """
        if button_type == "navigation":
            for btn in self.nav_buttons:
                btn.config(state=state)
        elif button_type == "ocr":
            if (
                self.ocr_button
            ):  # <--- Added check for ocr_button to prevent AttributeError if it's None
                self.ocr_button.config(state=state)
