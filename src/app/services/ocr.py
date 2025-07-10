# ocr.py

import google.generativeai as genai, json
# import time
from PIL import Image
from app.config import CONFIG # Updated import
from app.services.image_manager import ImageManager # Updated import

CONFIG.validate()

def perform_ocr(image_path, prompt, model):
    """Sends an image to Gemini Pro Vision for OCR and returns the text."""
    try:
        # Get image bytes via ImageManager
        image_data = ImageManager.image_to_bytes(image_path)
        
        if isinstance(image_data, dict):
            return image_data  # Return error dict directly
        
        image_part = {"mime_type": "image/png", "data": image_data}
        response = model.generate_content([prompt, image_part])
        response.resolve()
        return response
    except Exception as e:
        return {"ERROR": f"OCR processing error: {str(e)}"}

def main(image_path, model_key: int = 2):
    try:
        if model_key >= len(CONFIG.MODEL_LIST):
            return {"ERROR": "Invalid model index specified"}
                          
        genai.configure(api_key=CONFIG.API_KEY)
        model = genai.GenerativeModel(CONFIG.MODEL_LIST[model_key])

        ocr_output = perform_ocr(image_path, CONFIG.PROMPT2, model)
        if isinstance(ocr_output, dict):
            if "ERROR" in ocr_output:
                return {"ERROR": ocr_output["ERROR"]}
            if "error" in ocr_output:
                return {"ERROR": ocr_output["error"]}       

        data = ocr_output.text
        clean_data = data.replace("```json", "").replace("```", "").strip()
        ocr_data = json.loads(clean_data)
        return ocr_data
    except json.JSONDecodeError:
        return {"ERROR": "Invalid JSON response from API"}
    except Exception as e:
        return {"ERROR": f"OCR failed: {str(e)}"}

# Test the function with a sample image path
def main1(image_path):
    clean_data = """
    {
    "ration_card_id": {
        "value": "PHH 0046010534",
        "bounding_box": [383, 251, 404, 446]
    },
    "name_of_card_holder": {
        "value": "SUNITI BANARJEE",
        "bounding_box": [497, 250, 519, 431]
    },
    "father_husband_name": {
        "value": "KHUDIRAM",
        "bounding_box": [529, 250, 549, 358]
    },
    "address": {
        "value": "LAKHRA",
        "bounding_box": [319, 59, 814, 760]
    }
    }
    """
    ocr_data = json.loads(clean_data)
    # time.sleep(15)
    return ocr_data

# result = main(r"c:\image")
# print(result)
