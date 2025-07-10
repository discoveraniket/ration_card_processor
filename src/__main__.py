# __main__.py

import ttkbootstrap as tb
import os
import threading
import tkinter as tk
from PIL import Image, ImageTk
from app.utils.system_utils import is_dark_mode_windows
from typing import Optional


def create_splash_screen(root: tk.Tk, icon_path: str) -> tk.Toplevel:
    """
    Creates and displays a splash screen window with the app icon.

    Args:
        root (tk.Tk): The root Tkinter window of the main application.
        icon_path (str): The file path to the application icon.

    Returns:
        tk.Toplevel: The created splash screen Toplevel window.
    """
    splash: tk.Toplevel = tk.Toplevel(root)
    splash.title("Loading...")
    splash.overrideredirect(True)

    content_frame: tb.Frame = tb.Frame(splash)
    content_frame.pack(padx=20, pady=20)

    photo_image: Optional[ImageTk.PhotoImage] = None
    if os.path.exists(icon_path):
        try:
            pil_image: Image.Image = Image.open(icon_path)
            pil_image = pil_image.resize((128, 128), Image.Resampling.LANCZOS)
            photo_image = ImageTk.PhotoImage(pil_image)

            icon_label: tb.Label = tb.Label(content_frame, image=photo_image)
            icon_label.image = photo_image
            icon_label.pack(side="left", padx=10)
        except Exception as e:
            print(f"Error loading splash screen icon: {e}")
            photo_image = None
    else:
        print(f"Warning: Icon file not found for splash screen at {icon_path}")

    splash.update_idletasks()

    screen_width: int = root.winfo_screenwidth()
    screen_height: int = root.winfo_screenheight()

    x: int = (screen_width // 2) - (splash.winfo_width() // 2)
    y: int = (screen_height // 2) - (splash.winfo_height() // 2)
    splash.geometry(f"+{x}+{y}")

    splash.attributes("-topmost", True)

    return splash


def initialize_main_app(root_app: tk.Tk, app_ready_event: threading.Event) -> None:
    """
    Initializes the main application UI components in a separate thread.

    This function imports and instantiates the `MainUI` class, which is
    responsible for building the main user interface. After the UI is
    initialized, it sets a threading event to signal that the application
    is ready to be displayed.

    Args:
        root_app (tk.Tk): The root Tkinter window for the main application.
        app_ready_event (threading.Event): A threading event used to signal
            when the main application UI has been fully initialized.
    """
    # Import MainUI here to delay its loading until after splash screen is up
    from app.main_ui import MainUI

    # Instantiate the MainUI class, passing the root window
    # This is where the main UI components are created
    MainUI(root_app)

    # Signal that the main application is ready
    app_ready_event.set()


def main() -> None:
    """
    Main function to initialize and run the Ration Card Processor application.

    This function sets up the main application window, determines the theme
    based on the system's dark mode setting, displays a splash screen,
    and then initializes the main application UI in a separate thread.
    It periodically checks for the readiness of the main application and
    manages the visibility of the splash screen and main window accordingly.
    """
    theme_name: str = "darkly" if is_dark_mode_windows() else "flatly"

    app: tb.Window = tb.Window(themename=theme_name)
    app.withdraw()

    current_dir: str = os.path.dirname(os.path.abspath(__file__))
    icon_path: str = os.path.join(current_dir, "assets", "app_icon.ico")
    if os.path.exists(icon_path):
        app.iconbitmap(icon_path)
    else:
        print(f"Warning: Main app icon file not found at {icon_path}")

    splash_screen: tk.Toplevel = create_splash_screen(app, icon_path)

    app_ready_event: threading.Event = threading.Event()

    app_thread: threading.Thread = threading.Thread(
        target=initialize_main_app, args=(app, app_ready_event), daemon=True
    )
    app_thread.start()

    def check_app_ready() -> None:
        """
        Periodically checks if the main application is ready.

        If the `app_ready_event` is set, it destroys the splash screen and
        shows the main application window. Otherwise, it schedules itself
        to run again after a short delay.
        """
        if app_ready_event.is_set():
            splash_screen.destroy()
            app.deiconify()
        else:
            app.after(100, check_app_ready)

    app.after(100, check_app_ready)

    app.mainloop()


if __name__ == "__main__":
    main()
