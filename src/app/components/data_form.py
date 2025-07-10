# components/data_form.py
import ttkbootstrap as tb, pandas as pd
from ttkbootstrap.constants import *

# Assuming config is imported from the app directory
from app.config import CONFIG  # Added import for CONFIG


class DataForm:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.entries = {}
        self.entry_order = []
        self._create_frame()
        self._create_form()

    def _create_frame(self):
        """Create the container frame for the form"""
        self.frame = tb.Labelframe(self.parent, text="Card Details", padding=10)
        self.frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

    def _create_form(self):
        """Create form elements using config"""
        labels = [
            ("Ration Card ID:", 0, 0),
            ("Name of Card Holder:", 1, 0),
            ("Guardian's Name:", 0, 2),
            ("Head of Family:", 1, 2),
            ("Village:", 0, 4),
        ]

        for text, row, col in labels:
            label = tb.Label(self.frame, text=text)
            entry = tb.Entry(self.frame, width=30, takefocus=True)
            label.grid(row=row, column=col, padx=5, pady=5, sticky="w")
            entry.grid(row=row, column=col + 1, padx=5, pady=5, sticky="w")
            self.entries[text] = entry
            self.entry_order.append(entry)

            # Bind tab navigation
            entry.bind("<Tab>", self._on_tab)
            entry.bind("<Shift-Tab>", self._on_shift_tab)

    def _on_tab(self, event):
        """Handle tab navigation between entries"""
        w = event.widget
        if w in self.entry_order:
            idx = self.entry_order.index(w)
            nxt = self.entry_order[(idx + 1) % len(self.entry_order)]
            nxt.focus_set()
            return "break"

    def _on_shift_tab(self, event):
        """Handle shift-tab navigation between entries"""
        w = event.widget
        if w in self.entry_order:
            idx = self.entry_order.index(w)
            prev = self.entry_order[(idx - 1) % len(self.entry_order)]
            prev.focus_set()
            return "break"

    def populate_from_ocr(self, ocr_data):
        """Populate form fields from simplified OCR data"""
        for ocr_key, label_text in self.config.OCR_FIELD_MAPPING.items():
            if ocr_key in ocr_data and label_text in self.entries:
                value = ocr_data[ocr_key]
                entry = self.entries[label_text]
                entry.delete(0, tb.END)
                entry.insert(0, value)
        if self.entry_order:
            self.entry_order[0].focus_set()

    def populate_from_dataframe(self, row_data, field_mapping):
        """Populate form from DataFrame row"""
        for label_text, entry in self.entries.items():
            col = field_mapping[label_text]
            val = row_data.get(col, "")
            entry.delete(0, tb.END)
            # Handle pd.NA and empty strings safely
            if pd.notna(val) and val:  # Check for non-NA and non-empty
                entry.insert(0, str(val))
        if self.entry_order:
            self.entry_order[0].focus_set()

    def clear_form(self):
        """Clear all form entries"""
        for entry in self.entries.values():
            entry.delete(0, tb.END)
