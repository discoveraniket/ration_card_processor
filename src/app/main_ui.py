import ttkbootstrap as tb, os, queue, threading
from ttkbootstrap.constants import *
from tkinter import filedialog

# Relative imports based on the new structure
from app.components.navigation import NavigationToolbar
from app.components.data_form import DataForm
from app.components.status_bar import StatusBar
from app.services.image_manager import ImageManager
from app.services.data_manager import DataManager
from app.services.ocr import (
    main as ocr_main,
)  # Renamed to avoid conflict with method name
from app.utils.system_utils import is_dark_mode_windows
from app.config import CONFIG


class MainUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ration Card processor")
        self.root.state("zoomed")

        # Set the application icon
        # Construct the path to the icon file relative to the 'src' directory
        # This assumes main_ui.py is in src/app/
        # And the icon is in src/assets/app_icon.ico
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to 'app', then one more to 'src', then into 'assets'
        icon_path = os.path.join(current_dir, "..", "assets", "app_icon.ico")

        # Check if the icon file exists before trying to set it
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        else:
            print(f"Warning: Icon file not found at {icon_path}")

        # Initialize managers
        self._setup_image_display()
        self.image_manager = ImageManager(self.canvas)
        self.data_manager = DataManager()
        self.ocr_queue = queue.Queue()

        self.ocr_thread = None

        # Initialize core components
        self._create_navigation()
        self._init_data_form()
        self.status_bar = StatusBar(self.root)

        # Configuration values
        self.image_extensions = CONFIG.UI_IMAGE_EXTENSIONS
        self.field_mapping = CONFIG.UI_FIELD_MAPPING

        # Configure root window layout
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Set up event bindings
        self._setup_mouse_bindings()
        self._setup_key_bindings()

    def _setup_image_display(self):
        """Configure image display area"""
        self.frame_image = tb.Frame(self.root)
        self.canvas = tb.Canvas(self.frame_image)
        self.frame_image.grid(row=1, column=0, sticky="nsew")
        self.canvas.pack(fill="both", expand=True)

    def _init_data_form(self):
        """Initialize data entry form component"""
        self.data_form = DataForm(self.root, CONFIG)

    def _setup_mouse_bindings(self):
        """Configure mouse interactions"""
        self.canvas.bind("<MouseWheel>", lambda e: self.image_manager.on_mousewheel(e))
        self.canvas.bind("<ButtonPress-1>", lambda e: self.image_manager.start_pan(e))
        self.canvas.bind("<B1-Motion>", lambda e: self.image_manager.do_pan(e))
        self.canvas.bind("<ButtonRelease-1>", lambda e: self.image_manager.end_pan(e))
        self.canvas.bind("<Double-Button-1>", lambda e: self.zoom_to_fit_and_display())

    def _setup_key_bindings(self):
        """Configure keyboard shortcuts"""
        bindings = {
            # Navigation
            "<Left>": self.previous_image,
            "<Right>": self.next_image,
            "<Control-Left>": self.rotate_left,
            "<Control-Right>": self.rotate_right,
            "<Control-o>": self.browse,
            "<Control-Return>": self.ocr,
            "<Control-s>": self.update_data,
            # Pan controls
            "<Shift-Left>": lambda e: self.image_manager.pan_image(20, 0),
            "<Shift-Right>": lambda e: self.image_manager.pan_image(-20, 0),
            "<Shift-Up>": lambda e: self.image_manager.pan_image(0, 20),
            "<Shift-Down>": lambda e: self.image_manager.pan_image(0, -20),
        }

        for key, command in bindings.items():
            self.root.bind(key, lambda e, cmd=command: cmd())

    def _create_navigation(self):
        """Initialize navigation toolbar"""
        self.nav_toolbar = NavigationToolbar(self.root, self)

    def zoom_to_fit_and_display(self):
        self.image_manager.zoom_to_fit()
        self.image_manager.display_resized_image()

    def browse(self):
        folder_selected = filedialog.askdirectory()
        if not folder_selected:
            return

        self.image_manager.image_files = sorted(
            os.path.join(folder_selected, f)
            for f in os.listdir(folder_selected)
            if f.lower().endswith(CONFIG.UI_IMAGE_EXTENSIONS)
        )
        self.image_manager.current_index = 0

        # 3) Handle data through DataManager
        status_msg = self.data_manager.load_or_create(folder_selected)
        self.data_manager.sync_image_records(self.image_manager.image_files)

        # 4) Load first image (if any)
        if self.image_manager.image_files:
            self.image_manager.load_image(
                self.image_manager.image_files[self.image_manager.current_index]
            )
            self._populate_form_from_df()
            self.status_bar.set_status(
                f"{status_msg}; {len(self.image_manager.image_files)} images tracked."
            )
        else:
            self.status_bar.set_status("No image files found in the selected folder.")

    def previous_image(self):
        if self.image_manager.image_files and self.image_manager.current_index > 0:
            self.image_manager.current_index -= 1
            self.image_manager.load_image(
                self.image_manager.image_files[self.image_manager.current_index]
            )
            self._populate_form_from_df()
            self.status_bar.set_status(
                f"Image {self.image_manager.current_index + 1} of {len(self.image_manager.image_files)}"
            )
        else:
            self.status_bar.set_status("Already at the first image.")

    def next_image(self):
        if (
            self.image_manager.image_files
            and self.image_manager.current_index
            < len(self.image_manager.image_files) - 1
        ):
            self.image_manager.current_index += 1
            self.image_manager.load_image(
                self.image_manager.image_files[self.image_manager.current_index]
            )
            self._populate_form_from_df()
            self.status_bar.set_status(
                f"Image {self.image_manager.current_index + 1} of {len(self.image_manager.image_files)}"
            )
        else:
            self.status_bar.set_status("Already at the last image.")

    def rotate_left(self):
        self.image_manager.rotate_left()

    def rotate_right(self):
        self.image_manager.rotate_right()

    def ocr(self):
        # Prevent duplicate requests
        if self.ocr_thread and self.ocr_thread.is_alive():
            self.status_bar.set_status("Status: OCR already running!")
            return  # Early exit if thread is active

        self.status_bar.show_progress()

        if self.image_manager.current_index == -1:
            self.status_bar.set_status("Status: No image loaded")
            return

        # Disable buttons during processing
        self.nav_toolbar.set_button_state("navigation", "disabled")
        self.nav_toolbar.set_button_state("ocr", "disabled")
        self.status_bar.set_status("Status: Processing OCR...")

        # Start OCR thread
        image_path = self.image_manager.image_files[self.image_manager.current_index]
        self.ocr_thread = threading.Thread(
            target=self._run_ocr, args=(image_path,), daemon=True
        )
        self.ocr_thread.start()

        # Check for OCR results periodically
        self.root.after(100, self._check_ocr_queue)

    def update_data(self):
        # Guard: nothing to do if no image loaded
        if not self.image_manager.image_files or self.image_manager.current_index < 0:
            self.status_bar.set_status("Status: No image loaded to update")
            return

        # Get current image path and details
        old_path = self.image_manager.image_files[self.image_manager.current_index]
        img_dir = os.path.dirname(old_path)
        old_filename = os.path.basename(old_path)
        old_name, old_ext = os.path.splitext(old_filename)

        # Get the new ration card ID from the form
        new_rc_id = self.data_form.entries["Ration Card ID:"].get().strip()

        # Validate Ration Card ID
        if not new_rc_id:
            self.status_bar.set_status("Status: Ration Card ID cannot be empty")
            return

        # Clean invalid characters from RC ID for filename
        cleaned_rc_id = "".join(c for c in new_rc_id if c not in r'\/:*?"<>|')

        # Create new filename
        new_filename = f"{cleaned_rc_id}{old_ext}"
        new_path = os.path.join(img_dir, new_filename)

        try:
            # Rename the physical file
            os.rename(old_path, new_path)

            # Update the image_files list and current path
            self.image_manager.image_files[self.image_manager.current_index] = new_path

            # Update DataFrame references
            img_name = os.path.basename(old_path)

            form_data = {
                label: entry.get() for label, entry in self.data_form.entries.items()
            }
            update_values = self.data_manager.prepare_update_values(
                new_filename, form_data
            )

            self.data_manager.update_record(img_name, update_values)
            self.data_manager.save()

            # Update status and refresh form
            self.status_bar.set_status(f"Data updated")
            self._populate_form_from_df()

        except Exception as e:
            self.status_bar.set_status(f"Error: {str(e)}")

    def save_data(self):
        self.status_bar.set_status("Status: Save clicked")

    def options(self):
        self.status_bar.set_status("Status: Options clicked")

    def _run_ocr(self, image_path):
        try:
            # Call the ocr_main function from the ocr service
            ocr_data = ocr_main(image_path)

            # Check for OCR module errors first
            if isinstance(ocr_data, dict) and "ERROR" in ocr_data:
                self.ocr_queue.put(("error", ocr_data["ERROR"]))
            else:
                img_name = os.path.basename(image_path)
                self.data_manager.update_record_with_ocr(img_name, ocr_data)
                self.ocr_queue.put(("success", ocr_data))
        except Exception as e:
            self.ocr_queue.put(("error", f"System error: {str(e)}"))

    def _check_ocr_queue(self):
        try:
            result = self.ocr_queue.get_nowait()
            status, data = result

            if status == "success":
                self._populate_form(data)
                self.status_bar.set_status("Status: OCR completed")
            else:
                self.status_bar.set_status(f"Status: OCR Error - {data}")

            # Re-enable buttons
            self.ocr_thread = None  # Reset reference
            self.nav_toolbar.set_button_state("navigation", "normal")
            self.nav_toolbar.set_button_state("ocr", "normal")

            self.status_bar.hide_progress()

        except queue.Empty:
            if (
                self.ocr_thread and self.ocr_thread.is_alive()
            ):  # Only keep checking if active
                self.root.after(100, self._check_ocr_queue)
            else:
                # Handle zombie threads
                self.ocr_thread = None
                self.nav_toolbar.set_button_state("navigation", "normal")
                self.nav_toolbar.set_button_state("ocr", "normal")
                self.status_bar.set_status("Status: OCR failed unexpectedly")
                # Stop and hide progress bar
                self.status_bar.hide_progress()

    def _populate_form(self, ocr_data):
        """Extract only text values for form display"""
        values = {k: v["value"] for k, v in ocr_data.items()}
        self.data_form.populate_from_ocr(values)

    def _populate_form_from_df(self):
        if self.image_manager.current_index < 0:
            return
        if self.data_manager.df is None:
            self.data_form.clear_form()
            return
        if self.data_manager.df.empty:
            self.data_form.clear_form()
            return

        img_name = os.path.basename(
            self.image_manager.image_files[self.image_manager.current_index]
        )

        row = self.data_manager.get_record(img_name)
        if row is None:
            self.data_form.clear_form()
            return
        self.data_form.populate_from_dataframe(row, CONFIG.UI_FIELD_MAPPING)


if __name__ == "__main__":
    theme_name = "darkly" if is_dark_mode_windows() else "flatly"
    app = tb.Window(themename=theme_name)
    MainUI(app)
    app.mainloop()
