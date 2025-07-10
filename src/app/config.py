# config.py
"""
Application configuration settings.
"""
import os

class Config:
    # Data Configuration
    DATA_REQUIRED_COLS = [
        "image_name",
        "Ration Card ID",
        "Name of Card Holder",
        "Guardian's Name",
        "Head of Family",
        "Village"
    ]
    DATA_FILE_NAME = "data.xlsx"

    # UI Configuration
    UI_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".gif")
    UI_FIELD_MAPPING = {
        "Ration Card ID:": "Ration Card ID",
        "Name of Card Holder:": "Name of Card Holder",
        "Guardian's Name:": "Guardian's Name",
        "Head of Family:": "Head of Family",
        "Village:": "Village"
    }

    # OCR Configuration
    OCR_FIELD_MAPPING = {
        "ration_card_id": "Ration Card ID:",
        "name_of_card_holder": "Name of Card Holder:",
        "guardian_name": "Guardian's Name:",
        "head_of_family": "Head of Family:",
        "address": "Village:"
    }

    API_KEY = os.getenv("GEMINI_API_KEY")
    MODEL_LIST = [
        "gemini-2.5-pro-exp-03-25",
        "gemini-1.5-flash-8b-exp-0924",
        "gemini-2.0-flash"
    ]

    @classmethod
    def validate(cls):
        if not cls.API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        if not cls.MODEL_LIST:
            raise ValueError("Model list cannot be empty")
        if not cls.PROMPT2:
            raise ValueError("OCR prompt configuration missing")

    PROMPT1 = """
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
    
    PROMPT2 = """
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

# Instantiate for easy access
CONFIG = Config()

VERSION = "1.0.0"
APP_NAME = "RCP"
EXE_NAME = APP_NAME