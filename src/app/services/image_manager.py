# image_manager.py
from PIL import Image, ImageTk
import os, threading, io

class ImageManager:
    def __init__(self, canvas):
        self.lock = threading.Lock()
        self.canvas = canvas
        self.image_files = []
        self.current_index = -1
        self.original_image = None
        self.tk_image = None
        self.zoom_factor = 1.0
        self.image_pos = [0, 0]
        self.pan_start = None
        self.image_id = None

    def load_image(self, path=None):
        if not path or not os.path.exists(path):
            self.clear_canvas("Image not found")
            return None

        try:
            self.original_image = Image.open(path)
            self._refresh_ui_display()
            return self.original_image
        except Exception as e:
            self.clear_canvas(str(e))
            return {"error": f"Image processing error: {str(e)}"}
    
    def _refresh_ui_display(self):
        """Private method for UI updates"""
        self.zoom_factor = 1.0
        self.image_pos = [
            self.canvas.winfo_width()/2,
            self.canvas.winfo_height()/2
        ]
        self.zoom_to_fit()
        self.display_resized_image()

    def clear_canvas(self, text=None):
        self.canvas.delete("all")
        if text:
            self.canvas.create_text(100, 100, text=text, fill="red")
        self.original_image = None

    def zoom_to_fit(self):
        if not self.original_image:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return

        img_width = self.original_image.width
        img_height = self.original_image.height

        width_ratio = canvas_width / img_width
        height_ratio = canvas_height / img_height
        self.zoom_factor = min(width_ratio, height_ratio)
        self.image_pos = [canvas_width/2, canvas_height/2]  # 🚨 Critical fix

    def display_resized_image(self):
        """Display the image with current zoom and position"""
        if self.original_image:
            width = int(self.original_image.width * self.zoom_factor)
            height = int(self.original_image.height * self.zoom_factor)
            resized_img = self.original_image.resize((width, height), Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(resized_img)
            self.canvas.delete("all")
            self.image_id = self.canvas.create_image(
                self.image_pos[0], 
                self.image_pos[1],
                anchor="center",
                image=self.tk_image
            )

    def start_pan(self, event):
        self.pan_start = (event.x, event.y)

    def do_pan(self, event):
        if self.pan_start and self.image_id is not None:
            dx = event.x - self.pan_start[0]
            dy = event.y - self.pan_start[1]
            self.image_pos[0] += dx
            self.image_pos[1] += dy
            self.canvas.move(self.image_id, dx, dy)
            self.pan_start = (event.x, event.y)

    def end_pan(self, event):
        self.pan_start = None

    def pan_image(self, dx, dy):
        if self.image_id is not None:  # 🟢 Guard clause
            self.image_pos[0] += dx
            self.image_pos[1] += dy
            self.canvas.move(self.image_id, dx, dy)

    def rotate_left(self):
        if self.original_image:
            self.original_image = self.original_image.rotate(90, expand=True)
            self.zoom_to_fit()
            self.display_resized_image()
            self._save_rotated_image()

    def rotate_right(self):
        if self.original_image:
            self.original_image = self.original_image.rotate(-90, expand=True)
            self.zoom_to_fit()
            self.display_resized_image()
            self._save_rotated_image()

    def on_mousewheel(self, event):
            zoom_center = (event.x, event.y)
            if event.delta > 0 or event.num == 4:
                self.zoom_factor *= 1.1
            else:
                self.zoom_factor *= 0.9
            self.zoom_factor = max(0.1, min(self.zoom_factor, 5.0))
            
            # Adjust position to maintain zoom center
            self.image_pos[0] = zoom_center[0] - (zoom_center[0] - self.image_pos[0]) * (self.zoom_factor/(self.zoom_factor/1.1))
            self.image_pos[1] = zoom_center[1] - (zoom_center[1] - self.image_pos[1]) * (self.zoom_factor/(self.zoom_factor/1.1))
            
            self.display_resized_image()

    def on_frame_resize(self, event):
        """Handle window resize events"""
        if self.original_image:
            self.zoom_to_fit()
            self.display_resized_image()
    
    def _save_rotated_image(self):
        """Save the rotated image to disk, overwriting the original file."""    
        current_index = self.current_index
        if current_index < 0 or current_index >= len(self.image_files):
            return
        
        current_path = self.image_files[current_index]
        try:
            self.original_image.save(current_path)
            # print(f"Image saved: {os.path.basename(current_path)}")
        except Exception as e:
            print(f"Error saving image: {str(e)}")

    # OCR-Specific Methods ==========================================

    @staticmethod
    def image_to_bytes(image_path: str) -> bytes | dict:
        """Convert image to PNG bytes for OCR processing"""
        try:
            with Image.open(image_path) as img:
                return ImageManager._pil_image_to_bytes(img)
        except FileNotFoundError:
            return {"error": "Image file not found"}
        except Exception as e:
            return {"error": f"Image processing error: {str(e)}"}
    
    @staticmethod
    def _pil_image_to_bytes(image: Image.Image) -> bytes:
        """Convert PIL Image to PNG bytes"""
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def validate_image_size(image: Image.Image, max_mb=10):
        """Check image size constraints"""
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        if len(buffer.getvalue()) > max_mb * 1024 * 1024:
            raise ValueError(f"Image exceeds {max_mb}MB size limit")
