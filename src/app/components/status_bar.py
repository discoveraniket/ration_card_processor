# components/status_bar.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from typing import Optional


class StatusBar:
    """Manages the application's status bar, displaying messages and progress.

    This class provides a status label and an indeterminate progress bar to
    give visual feedback to the user about ongoing operations.

    Attributes:
        parent: The parent widget (e.g., a ttkbootstrap.Window) to which this
            status bar will be attached.
        frame: The `ttkbootstrap.Frame` widget that serves as the container for
            the status label and progress bar.
        label: The `ttkbootstrap.Label` widget used to display status messages.
        progress: The `ttkbootstrap.Progressbar` widget for showing indeterminate
            progress.
    """

    def __init__(self, parent: tb.Window) -> None:
        """Initializes the StatusBar.

        Args:
            parent: The parent widget (e.g., a ttkbootstrap.Window) to which this
                status bar will be attached.
        """
        self.parent: tb.Window = parent
        self.frame: Optional[tb.Frame] = None
        self.label: Optional[tb.Label] = None
        self.progress: Optional[tb.Progressbar] = None
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Creates and configures the status bar widgets.

        This includes the main frame, the status label, and the progress bar.
        The progress bar is initially hidden.
        """
        self.frame = tb.Frame(self.parent)
        self.frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 5))

        # Status label
        self.label = tb.Label(self.frame, text="Status: Ready", anchor="w")
        self.label.grid(row=0, column=0, sticky="ew")

        # Progress bar
        self.progress = tb.Progressbar(
            self.frame, mode="indeterminate", bootstyle=(STRIPED, SUCCESS)
        )
        self.progress.grid(row=0, column=1, sticky="e", padx=5)
        self.progress.grid_remove()

        # Grid configuration
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, minsize=150)

    def set_status(self, message: str) -> None:
        """Updates the text displayed in the status bar.

        Args:
            message: The status message string to display.
        """
        # if self.label: <-- Gemini suggest this. Chaek why
        self.label.config(text=message)

    def show_progress(self) -> None:
        """Displays the progress bar and starts its animation.

        This method makes the progress bar visible and begins its indeterminate
        animation to indicate an ongoing process.
        """
        # if self.progress: <-- Gemini suggest this. Chaek why
        self.progress.grid()
        self.progress.start()

    def hide_progress(self) -> None:
        """Hides the progress bar and stops its animation.

        This method stops the progress bar's animation and removes it from the
        layout, making it invisible.
        """
        # if self.progress: <-- Gemini suggest this. Chaek why
        self.progress.stop()
        self.progress.grid_remove()

    def start_progress(self) -> None:
        """Starts the progress bar animation. (Deprecated: Use `show_progress` instead for full control)"""  # <--- This method seems redundant with show_progress. Consider removing or merging.
        # if self.progress: <-- Gemini suggest this. Chaek why
        self.progress.start()

    def stop_progress(self) -> None:
        """Stops the progress bar animation. (Deprecated: Use `hide_progress` instead for full control)"""  # <--- This method seems redundant with hide_progress. Consider removing or merging.
        # if self.progress: <-- Gemini suggest this. Chaek why
        self.progress.stop()
