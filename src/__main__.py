# __main__.py

import ttkbootstrap as tb
import os
import threading
import tkinter as tk
from PIL import Image, ImageTk  # Import PIL for image handling
from app.utils.system_utils import is_dark_mode_windows


def create_splash_screen(root, icon_path):
    """
    Creates and displays a splash screen window with the app icon and loading text.
    """
    splash = tk.Toplevel(root)
    splash.title("Loading...")  # Set a title for the splash screen
    splash.overrideredirect(True)  # Remove window decorations (title bar, buttons)

    # Create a frame to hold the icon and text, allowing for horizontal layout
    content_frame = tb.Frame(splash)
    content_frame.pack(padx=20, pady=20)  # Padding for the overall content

    # Load and display the icon on the splash screen
    photo_image = None
    if os.path.exists(icon_path):
        try:
            pil_image = Image.open(icon_path)
            # Increase icon size (e.g., 128x128 pixels)
            pil_image = pil_image.resize((128, 128), Image.Resampling.LANCZOS)
            photo_image = ImageTk.PhotoImage(pil_image)

            icon_label = tb.Label(content_frame, image=photo_image)
            icon_label.image = (
                photo_image  # Keep a reference to prevent garbage collection
            )
            icon_label.pack(side="left", padx=10)  # Position icon to the left
        except Exception as e:
            print(f"Error loading splash screen icon: {e}")
            photo_image = None
    else:
        print(f"Warning: Icon file not found for splash screen at {icon_path}")

    # Add a label for loading message (smaller font)
    # label = tb.Label(content_frame, text="Loading Application...", font=("Helvetica", 10), bootstyle="primary")
    # label.pack(side="left", padx=5) # Position text to the right of the icon

    # Center the splash screen on the actual screen
    splash.update_idletasks()  # Update geometry to get correct width/height
    # splash.update()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width // 2) - (splash.winfo_width() // 2)
    y = (screen_height // 2) - (splash.winfo_height() // 2)
    splash.geometry(f"+{x}+{y}")

    # Make the splash screen always on top
    splash.attributes("-topmost", True)

    return splash


def initialize_main_app(root_app, app_ready_event):
    """
    Initializes the main application UI in a separate thread.
    Signals when the main UI is ready.
    """
    # Import MainUI here to delay its loading until after splash screen is up
    from app.main_ui import MainUI

    # Instantiate the MainUI class, passing the root window
    # This is where the main UI components are created
    MainUI(root_app)

    # Signal that the main application is ready
    app_ready_event.set()


def main():
    """
    Main function to initialize and run the Ration Card Processor application,
    with a splash screen.
    """
    # Determine the theme based on system dark mode setting
    theme_name = "darkly" if is_dark_mode_windows() else "flatly"

    # Create the main application window (initially hidden)
    app = tb.Window(themename=theme_name)
    app.withdraw()  # Hide the main window initially

    # Set the main application window icon (for taskbar)
    # This should still be done on the main 'app' window for taskbar visibility
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "assets", "app_icon.ico")
    if os.path.exists(icon_path):
        app.iconbitmap(icon_path)
    else:
        print(f"Warning: Main app icon file not found at {icon_path}")

    # Create and display the splash screen
    splash_screen = create_splash_screen(app, icon_path)

    # Event to signal when the main app is ready
    app_ready_event = threading.Event()

    # Start the main application initialization in a separate thread
    app_thread = threading.Thread(
        target=initialize_main_app,
        args=(app, app_ready_event),
        daemon=True,  # Daemon thread exits when main program exits
    )
    app_thread.start()

    def check_app_ready():
        """
        Periodically checks if the main app is ready and manages the splash screen.
        """
        if app_ready_event.is_set():
            # Main app is ready, destroy splash screen and show main window
            splash_screen.destroy()
            app.deiconify()  # Show the main window
        else:
            # Main app not ready yet, check again after a short delay
            app.after(100, check_app_ready)  # Check every 100ms

    # Start checking for app readiness
    app.after(100, check_app_ready)

    # Start the Tkinter event loop
    app.mainloop()


if __name__ == "__main__":
    main()
