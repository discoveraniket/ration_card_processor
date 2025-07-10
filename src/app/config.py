# config.py
"""
Application configuration settings.
"""
import os
from typing import List, Dict, Tuple, Optional


class Config:
    """
    Configuration class for the Ration Card Processor application.

    This class holds various settings related to data handling, UI, OCR,
    API keys, and prompts for the Gemini model.
    """

    # Data Configuration
    DATA_REQUIRED_COLS: List[str] = [
        "image_name",
        "Ration Card ID",
        "Name of Card Holder",
        "Guardian's Name",
        "Head of Family",
        "Village",
    ]
    """List of required column names for data processing."""

    DATA_FILE_NAME: str = "data.xlsx"
    """Name of the data file."""

    # UI Configuration
    UI_IMAGE_EXTENSIONS: Tuple[str, ...] = (".jpg", ".jpeg", ".png", ".bmp", ".gif")
    """Tuple of supported image file extensions for the UI."""

    UI_FIELD_MAPPING: Dict[str, str] = {
        "Ration Card ID:": "Ration Card ID",
        "Name of Card Holder:": "Name of Card Holder",
        "Guardian's Name:": "Guardian's Name",
        "Head of Family:": "Head of Family",
        "Village:": "Village",
    }
    """Mapping from UI display labels to internal data field names."""

    # OCR Configuration
    OCR_FIELD_MAPPING: Dict[str, str] = {
        "ration_card_id": "Ration Card ID:",
        "name_of_card_holder": "Name of Card Holder:",
        "guardian_name": "Guardian's Name:",
        "head_of_family": "Head of Family:",
        "address": "Village:",
    }
    """Mapping from OCR output keys to UI display labels."""

    API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    """API key for accessing the Gemini model, fetched from environment variables."""

    MODEL_LIST: List[str] = [
        "gemini-2.5-pro-exp-03-25",
        "gemini-1.5-flash-8b-exp-0924",
        "gemini-2.0-flash",
    ]
    """List of available Gemini models."""

    @classmethod
    def validate(cls) -> None:
        """
        Validates that essential configuration variables are set.

        Raises:
            ValueError: If GEMINI_API_KEY is not set, MODEL_LIST is empty,
                        or PROMPT2 is missing.
        """
        if not cls.API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        if not cls.MODEL_LIST:
            raise ValueError("Model list cannot be empty")
        if not cls.PROMPT2:
            raise ValueError("OCR prompt configuration missing")

    PROMPT1: str = """
        Perform OCR on the ration card document image and return EXCLUSIVELY these 4 fields with strict JSON keys:

        1. `ration_card_id`: 
        - The exact alphanumeric ration card ID 
        - Example: "PHH 0046010534"

        2. `name_of_card_holder`:
        - Full name of the primary card holder
        - Example: "SUNITI BANARJEE"

        3. `guardian_name`:
        - Name of father/husband/guardian 
        - Return "NA" if not present
        - Example: "KHUDIRAM" or "NA"

        4. `head_of_family`:
        - Name of the head of family
        - Return "NA" if not present
        - Example: "KHUDIRAM" or "NA"

        5. `address`:
        - find village name
        - Example: "Lakhra"

        FORMAT REQUIREMENTS:
        - Use exactly these lowercase snake_case keys
        - Include bounding boxes as [y_min, x_min, y_max, x_max]
        - Return empty strings for missing fields
        - Strict JSON format, no extra fields

        EXAMPLE RESPONSE:
        {
        "ration_card_id": {
            "value": "alphanumeric ration card ID",
            "bounding_box": [y_min, x_min, y_max, x_max]
        },
        // Rest of the fields follow the same format
        }
        """
    """Prompt template for OCR extraction (version 1)."""

    PROMPT2: str = """
        Perform OCR on the ration card document image and return EXCLUSIVELY 
        these 5 fields and their bounding box coordinates with strict JSON keys:

        1. `ration_card_id`:
        - Either one of "AAY/SPHH/PHH/RKSY-I/RKSY-II", followed by a number.
        - For example: "AAY 0123456789"
        - Return empty string if missing (not "NA")
        - Return bounding box coordinates

        2. `name_of_card_holder`:
        - Name of primary card holder (e.g., "FIRST_NAME LAST_NAME")
        - Return empty string if missing (not "NA")
        - Return bounding box coordinates

        3. `guardian_name`:
        - Name of father/husband/guardian 
        - Return empty string if missing (not "NA")
        - Return bounding box coordinates

        4. `head_of_family`:
        - Name of family head
        - Return empty string if missing (not "NA")
        - Return bounding box coordinates

        5. `address`:
        - Village name:
        - Return empty string if missing (not "NA")
        - Return bounding box coordinates

        FORMAT REQUIREMENTS:
        - Use exactly these lowercase snake_case keys
        - Bounding boxes as [y_min, x_min, y_max, x_max] (top-left origin coordinates)
        - Empty strings for missing fields (no "NA")
        - Strict JSON format, no extra fields/markdown

        EXAMPLE RESPONSE:
        {
        "ration_card_id": {
            "value": "alphanumeric code",
            "bounding_box": [y_min, x_min, y_max, x_max]
        },
        // Rest of the fields follow the same format
        }
        """
    """Prompt template for OCR extraction (version 2)."""


# Instantiate for easy access
CONFIG: Config = Config()
"""An instance of the Config class for easy access to configuration settings."""

VERSION: str = "1.0.0"
"""Current version of the application."""

APP_NAME: str = "RCP"
"""Short name of the application."""

EXE_NAME: str = APP_NAME
"""Name of the executable file."""
