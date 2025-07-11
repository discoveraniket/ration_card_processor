# src/app/services/data_manager.py
import pandas as pd, os, json
from typing import Dict, List, Optional, Any

from app.config import CONFIG


class DataManager:
    """Manages the loading, saving, and manipulation of ration card data.

    This class handles interaction with an Excel file for structured data
    and a JSON file for bounding box information, ensuring data consistency
    and providing methods for updating and retrieving records.

    Attributes:
        df: A pandas DataFrame holding the ration card data.
        data_path: The absolute path to the Excel data file (e.g., `data.xlsx`).
        bbox_path: The absolute path to the JSON bounding box data file (e.g., `bbox_data.json`).
        required_cols: A list of column names that must be present in the DataFrame,
            sourced from `CONFIG.DATA_REQUIRED_COLS`.
    """

    def __init__(self) -> None:
        """Initializes the DataManager with empty DataFrame and paths.

        The DataFrame and file paths are set to None or empty, and will be
        initialized upon calling `load_or_create`.
        """
        self.df: pd.DataFrame = pd.DataFrame()
        self.data_path: Optional[str] = None
        self.bbox_path: Optional[str] = None
        self.required_cols: List[str] = CONFIG.DATA_REQUIRED_COLS

    def load_or_create(self, folder_path: str) -> str:
        """Loads an existing data file or creates a new one if not found.

        Initializes `self.df` from `data.xlsx` or creates a new DataFrame
        with `required_cols`. Also ensures `bbox_data.json` exists.

        Args:
            folder_path: The directory where `data.xlsx` and `bbox_data.json`
                are expected or will be created.

        Returns:
            A status message indicating whether an existing file was loaded
            or a new one was created.
        """
        self.data_path = os.path.join(folder_path, CONFIG.DATA_FILE_NAME)

        if os.path.exists(self.data_path):
            self.df = pd.read_excel(
                self.data_path, dtype={col: "string" for col in self.required_cols}
            )
            status_msg: str = "Loaded existing data.xlsx"
        else:
            self.df = pd.DataFrame(columns=self.required_cols).astype("string")
            status_msg: str = "Created new data.xlsx"

        self.bbox_path = os.path.join(folder_path, "bbox_data.json")
        if not os.path.exists(self.bbox_path):
            with open(self.bbox_path, "w") as f:
                json.dump({}, f)

        for col in self.required_cols:
            if col not in self.df.columns:
                self.df[col] = pd.Series(dtype="string")

        self.df = self.df[self.required_cols]
        return status_msg

    def sync_image_records(self, image_paths: List[str]) -> None:
        """Synchronizes DataFrame records with the current list of image files.

        Adds new image files as records to the DataFrame if they don't already
        exist. Saves the DataFrame if new records are added.

        Args:
            image_paths: A list of absolute paths to image files found in the
                current directory.
        """
        existing: set[str] = set(self.df["image_name"].dropna())
        new_rows: List[Dict[str, str]] = [
            {"image_name": os.path.basename(p)}
            for p in image_paths
            if os.path.basename(p) not in existing
        ]

        if new_rows:
            new_df: pd.DataFrame = pd.DataFrame(new_rows).astype("string")
            self.df = pd.concat([self.df, new_df], ignore_index=True)
            self.save()

    def save(self) -> None:
        """Saves the current DataFrame to the Excel file.

        The DataFrame is saved to the path specified by `self.data_path`.
        """
        if self.data_path:
            self.df.to_excel(self.data_path, index=False)
        else:
            print(
                "Warning: Data path not set. Cannot save DataFrame."
            )  # <--- Added warning if data_path is None

    def update_record(self, old_filename: str, new_data: Dict[str, Any]) -> None:
        """Updates a record in the DataFrame and potentially renames its bbox entry.

        Args:
            old_filename: The original filename of the image record to update.
            new_data: A dictionary of column-value pairs to update in the record.
                If 'image_name' is present, the corresponding bbox entry is also renamed.
        """
        mask: pd.Series[bool] = self.df["image_name"] == old_filename
        for col, value in new_data.items():
            self.df.loc[mask, col] = str(value) if pd.notna(value) else pd.NA

        if "image_name" in new_data:
            new_filename: str = new_data["image_name"]
            with open(self.bbox_path, "r+") as f:
                data: Dict[str, Any] = json.load(f)
                if old_filename in data:
                    data[new_filename] = data.pop(old_filename)
                    f.seek(0)
                    json.dump(data, f, indent=2)

    def get_record(self, image_name: str) -> Optional[pd.Series]:
        """Retrieves a single record from the DataFrame by image name.

        Args:
            image_name: The filename of the image whose record is to be retrieved.

        Returns:
            A pandas Series representing the record if found, otherwise None.
        """
        row: pd.DataFrame = self.df[self.df["image_name"] == image_name]
        return row.iloc[0] if not row.empty else None

    def prepare_update_values(
        self, new_image_name: str, form_label_values: Dict[str, str]
    ) -> Dict[str, str]:
        """Constructs the update dictionary for a record using raw form values.

        Args:
            new_image_name: New filename for the image.
            form_label_values: Dictionary of {form_label: entered_value}
                (e.g., {"Ration Card ID:": "12345", ...}).

        Returns:
            Dictionary ready for `update_record()` with {column_name: value}.
        """
        update_values: Dict[str, str] = {"image_name": new_image_name}
        for label, col in CONFIG.UI_FIELD_MAPPING.items():
            raw_value: str = form_label_values.get(label, "").strip()
            update_values[col] = raw_value if raw_value else ""
        return update_values

    def update_bbox(self, image_name: str, bbox_data: Dict[str, Any]) -> None:
        """Updates the bounding box data for a specific image in the JSON file.

        Args:
            image_name: The filename of the image for which to update bbox data.
            bbox_data: A dictionary containing the bounding box information.
        """
        if self.bbox_path:
            try:
                with open(self.bbox_path, "r+") as f:
                    data: Dict[str, Any] = json.load(f)
                    data[image_name] = bbox_data
                    f.seek(0)
                    json.dump(data, f, indent=2)
            except Exception as e:
                print(f"Error updating bbox: {str(e)}")
        else:
            print(
                "Warning: Bbox path not set. Cannot update bbox data."
            )  # <--- Added warning if bbox_path is None

    def get_bbox(self, image_name: str) -> Dict[str, Any]:
        """Retrieves bounding box data for a specific image.

        Args:
            image_name: The filename of the image for which to retrieve bbox data.

        Returns:
            A dictionary containing the bounding box data for the image, or an
            empty dictionary if not found or `bbox_path` is not set.
        """
        if self.bbox_path and os.path.exists(self.bbox_path):
            try:
                with open(self.bbox_path, "r") as f:
                    data: Dict[str, Any] = json.load(f)
                    return data.get(image_name, {})
            except Exception as e:
                print(
                    f"Error reading bbox: {str(e)}"
                )  # <--- Added error handling for bbox read
                return {}
        else:
            print(
                "Warning: Bbox path not set or file does not exist. Cannot retrieve bbox data."
            )  # <--- Added warning if bbox_path is None or file does not exist
            return {}

    def update_record_with_ocr(self, image_name: str, ocr_data: Dict[str, Any]) -> None:
        """Updates the DataFrame record and bbox data with OCR results.

        This method processes OCR output, mapping text data to Excel columns
        and bounding box data to the JSON file.

        Args:
            image_name: The filename of the image for which OCR was performed.
            ocr_data: A dictionary containing the raw OCR results, including
                text values and bounding box information.
        """
        text_data: Dict[str, str] = {}
        for ocr_key, value_dict in ocr_data.items():
            for label, col in CONFIG.UI_FIELD_MAPPING.items():
                if CONFIG.OCR_FIELD_MAPPING.get(ocr_key) == label:
                    text_data[col] = value_dict["value"]
                    break

        filtered_data: Dict[str, str] = {
            k: v for k, v in text_data.items() if k in self.required_cols
        }
        self.update_record(image_name, filtered_data)

        bbox_data: Dict[str, List[Any]] = {
            k: v.get("bounding_box", []) for k, v in ocr_data.items()
        }
        self.update_bbox(image_name, bbox_data)
