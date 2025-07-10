# data_manager.py
import pandas as pd, os, json
from app.config import CONFIG  # Updated import


class DataManager:
    def __init__(self):
        self.df = pd.DataFrame()
        self.data_path = None
        self.bbox_path = None
        self.required_cols = CONFIG.DATA_REQUIRED_COLS

    def load_or_create(self, folder_path):
        self.data_path = os.path.join(folder_path, CONFIG.DATA_FILE_NAME)

        if os.path.exists(self.data_path):
            self.df = pd.read_excel(
                self.data_path, dtype={col: "string" for col in self.required_cols}
            )
            status_msg = "Loaded existing data.xlsx"
        else:
            self.df = pd.DataFrame(columns=self.required_cols).astype("string")
            status_msg = "Created new data.xlsx"

        # New: Initialize bbox JSON
        self.bbox_path = os.path.join(folder_path, "bbox_data.json")
        if not os.path.exists(self.bbox_path):
            with open(self.bbox_path, "w") as f:
                json.dump({}, f)

        # Ensure required columns exist
        for col in self.required_cols:
            if col not in self.df.columns:
                self.df[col] = pd.Series(dtype="string")  # Initialize as string

        self.df = self.df[self.required_cols]
        return status_msg

    def sync_image_records(self, image_paths):
        existing = set(self.df["image_name"].dropna())
        new_rows = [
            {"image_name": os.path.basename(p)}
            for p in image_paths
            if os.path.basename(p) not in existing
        ]

        if new_rows:
            new_df = pd.DataFrame(new_rows).astype("string")
            self.df = pd.concat([self.df, new_df], ignore_index=True)
            self.save()

    def save(self):
        self.df.to_excel(self.data_path, index=False)

    def update_record(self, old_filename, new_data):
        mask = self.df["image_name"] == old_filename
        for col, value in new_data.items():
            self.df.loc[mask, col] = str(value) if pd.notna(value) else pd.NA

        # New: Handle JSON key rename if image_name changes
        if "image_name" in new_data:
            new_filename = new_data["image_name"]
            with open(self.bbox_path, "r+") as f:
                data = json.load(f)
                if old_filename in data:
                    data[new_filename] = data.pop(old_filename)
                    f.seek(0)
                    json.dump(data, f, indent=2)

    def get_record(self, image_name):
        """Returns a record (as a pandas Series) for the given image name."""
        row = self.df[self.df["image_name"] == image_name]
        return row.iloc[0] if not row.empty else None

    def prepare_update_values(
        self, new_image_name: str, form_label_values: dict
    ) -> dict:
        """Constructs the update dictionary for a record using raw form values.

        Args:
            new_image_name: New filename for the image
            form_label_values: Dictionary of {form_label: entered_value}
                (e.g., {"Ration Card ID:": "12345", ...})

        Returns:
            Dictionary ready for `update_record()` with {column_name: value}
        """
        update_values = {"image_name": new_image_name}
        for label, col in CONFIG.UI_FIELD_MAPPING.items():
            raw_value = form_label_values.get(label, "").strip()
            update_values[col] = raw_value if raw_value else ""
        return update_values

    def update_bbox(self, image_name: str, bbox_data: dict):
        try:
            with open(self.bbox_path, "r+") as f:
                data = json.load(f)
                data[image_name] = bbox_data
                f.seek(0)
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error updating bbox: {str(e)}")

    def get_bbox(self, image_name: str) -> dict:
        """Retrieve bbox data for an image"""
        with open(self.bbox_path, "r") as f:
            data = json.load(f)
            return data.get(image_name, {})

    def update_record_with_ocr(self, image_name: str, ocr_data: dict):
        """Split OCR data into Excel and JSON storage"""
        # Map OCR keys to Excel columns using UI_FIELD_MAPPING
        text_data = {}
        for ocr_key, value_dict in ocr_data.items():
            # Find the corresponding label in UI_FIELD_MAPPING
            for label, col in CONFIG.UI_FIELD_MAPPING.items():
                if CONFIG.OCR_FIELD_MAPPING.get(ocr_key) == label:
                    text_data[col] = value_dict["value"]
                    break

        # Ensure we only update required columns
        filtered_data = {k: v for k, v in text_data.items() if k in self.required_cols}
        self.update_record(image_name, filtered_data)

        # Bounding box handling remains unchanged
        bbox_data = {k: v.get("bounding_box", []) for k, v in ocr_data.items()}
        self.update_bbox(image_name, bbox_data)
