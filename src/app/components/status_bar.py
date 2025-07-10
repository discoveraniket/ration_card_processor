# components/status_bar.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class StatusBar:
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.label = None
        self.progress = None
        self._create_widgets()

    def _create_widgets(self):
        """Initialize status bar components"""
        self.frame = tb.Frame(self.parent)
        self.frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 5))
        
        # Status label
        self.label = tb.Label(self.frame, text="Status: Ready", anchor="w")
        self.label.grid(row=0, column=0, sticky="ew")
        
        # Progress bar
        self.progress = tb.Progressbar(
            self.frame, 
            mode='indeterminate', 
            bootstyle=(STRIPED, SUCCESS)
        )
        self.progress.grid(row=0, column=1, sticky="e", padx=5)
        self.progress.grid_remove()
        
        # Grid configuration
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, minsize=150)

    def set_status(self, message):
        """Update status text"""
        self.label.config(text=message)

    def show_progress(self):
        """Show and start progress animation"""
        self.progress.grid()
        self.progress.start()

    def hide_progress(self):
        """Hide and stop progress animation"""
        self.progress.stop()
        self.progress.grid_remove()
    
    def start_progress(self):
        self.progress.start()

    def stop_progress(self):
        self.progress.stop()