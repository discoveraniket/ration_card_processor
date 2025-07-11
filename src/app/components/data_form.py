# components/data_form.py
import ttkbootstrap as tb, pandas as pd, tkinter as tk
from ttkbootstrap.constants import *
from typing import Dict, List, Tuple, Any, Optional

from app.config import CONFIG


class DataForm:
    """Manages the data entry form for Ration Card details.

    This class creates and manages the UI elements for entering and displaying
    ration card information, including handling data population from OCR results
    or a DataFrame, and managing keyboard navigation.

    Attributes:
        parent: The parent widget (e.g., a ttkbootstrap.Window or Frame) to which
            this form will be attached.
        config: An object containing application configuration, specifically
            expected to have `OCR_FIELD_MAPPING`.
        entries: A dictionary mapping label text to their corresponding
            ttkbootstrap.Entry widgets.
        entry_order: A list of ttkbootstrap.Entry widgets in the order they
            appear in the form, used for tab navigation.
        frame: The ttkbootstrap.Labelframe widget that contains all form elements.
    """

    def __init__(self, parent: tb.Window | tb.Frame, config: Any) -> None:
        """Initializes the DataForm.

        Args:
            parent: The parent widget (e.g., a ttkbootstrap.Window or Frame) to which
                this form will be attached.
            config: An object containing application configuration, specifically
                expected to have `OCR_FIELD_MAPPING`.
        """
        self.parent: tb.Window | tb.Frame = parent
        self.config: Any = config
        self.entries: Dict[str, tb.Entry] = {}
        self.entry_order: List[tb.Entry] = []
        self._create_frame()
        self._create_form()

    def _create_frame(self) -> None:
        """Creates the container frame for the form.

        The frame is a `ttkbootstrap.Labelframe` titled "Card Details" and
        is placed in the parent widget's grid.
        """
        self.frame: tb.Labelframe = tb.Labelframe(
            self.parent, text="Card Details", padding=10
        )
        self.frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

    def _create_form(self) -> None:
        """Creates form elements (labels and entry fields) based on predefined labels.

        Each entry widget is stored in `self.entries` and `self.entry_order`,
        and keyboard bindings for tab navigation are set up.
        """
        labels: List[Tuple[str, int, int]] = [
            ("Ration Card ID:", 0, 0),
            ("Name of Card Holder:", 1, 0),
            ("Guardian's Name:", 0, 2),
            ("Head of Family:", 1, 2),
            ("Village:", 0, 4),
        ]

        for text, row, col in labels:
            label: tb.Label = tb.Label(self.frame, text=text)
            entry: tb.Entry = tb.Entry(self.frame, width=30, takefocus=True)
            label.grid(row=row, column=col, padx=5, pady=5, sticky="w")
            entry.grid(row=row, column=col + 1, padx=5, pady=5, sticky="w")
            self.entries[text] = entry
            self.entry_order.append(entry)

            entry.bind("<Tab>", self._on_tab)
            entry.bind("<Shift-Tab>", self._on_shift_tab)

    def _on_tab(self, event: tk.Event) -> str:
        """Handles tab navigation between entry widgets.

        Moves focus to the next entry in `self.entry_order` when the Tab key is pressed.

        Args:
            event: The Tkinter event object.

        Returns:
            The string "break" to stop the event's default propagation.
        """
        w: tb.Widget = event.widget
        if w in self.entry_order:
            idx: int = self.entry_order.index(w)
            nxt: tb.Entry = self.entry_order[(idx + 1) % len(self.entry_order)]
            nxt.focus_set()
            return "break"
        return ""  # <--- Added return for cases where w is not in entry_order

    def _on_shift_tab(self, event: tk.Event) -> str:
        """Handles shift-tab navigation between entry widgets.

        Moves focus to the previous entry in `self.entry_order` when Shift+Tab is pressed.

        Args:
            event: The Tkinter event object.

        Returns:
            The string "break" to stop the event's default propagation.
        """
        w: tb.Widget = event.widget
        if w in self.entry_order:
            idx: int = self.entry_order.index(w)
            prev: tb.Entry = self.entry_order[(idx - 1) % len(self.entry_order)]
            prev.focus_set()
            return "break"
        return ""  # <--- Added return for cases where w is not in entry_order

    def populate_from_ocr(self, ocr_data: Dict[str, Any]) -> None:
        """Populates form fields with data extracted from OCR.

        It uses `self.config.OCR_FIELD_MAPPING` to map OCR keys to form labels.
        After population, sets focus to the first entry.

        Args:
            ocr_data: A dictionary where keys are OCR field names and values are
                the extracted data.
        """
        for ocr_key, label_text in self.config.OCR_FIELD_MAPPING.items():
            if ocr_key in ocr_data and label_text in self.entries:
                value: Any = ocr_data[ocr_key]
                entry: tb.Entry = self.entries[label_text]
                entry.delete(0, tb.END)
                entry.insert(0, value)
        if self.entry_order:
            self.entry_order[0].focus_set()

    def populate_from_dataframe(
        self, row_data: Dict[str, Any], field_mapping: Dict[str, str]
    ) -> None:
        """Populates form fields with data from a pandas DataFrame row.

        It uses the provided `field_mapping` to map DataFrame column names
        to form labels. Handles `pd.NA` and empty strings safely.
        After population, sets focus to the first entry.

        Args:
            row_data: A dictionary representing a row from a pandas DataFrame,
                where keys are column names and values are the row's data.
            field_mapping: A dictionary mapping form label text to DataFrame
                column names.
        """
        for label_text, entry in self.entries.items():
            col: str = field_mapping[label_text]
            val: Any = row_data.get(col, "")
            entry.delete(0, tb.END)
            if pd.notna(val) and val:
                entry.insert(0, str(val))
        if self.entry_order:
            self.entry_order[0].focus_set()

    def clear_form(self) -> None:
        """Clears the content of all entry fields in the form."""
        for entry in self.entries.values():
            entry.delete(0, tb.END)
