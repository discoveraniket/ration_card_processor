import PyInstaller.__main__
import os
import sys # Import sys module

# Add the 'src' directory to the Python path so 'app' can be found
# This assumes build.py is at the root of the 'ration-card-processor' folder
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import CONFIG from the app directory to get version and app names
from app.config import CONFIG

# Use values from CONFIG
VERSION = CONFIG.VERSION
APP_NAME = CONFIG.APP_NAME
EXE_NAME = CONFIG.EXE_NAME

# Define the output directory. You might want to make this configurable or relative.
# For now, keeping it as a fixed path for demonstration.
output_dir = r"D:\Desktop\App Deploye\RCP" 

# Get the path to the main entry point file (__main__.py)
# This assumes build.py is at the root of the 'ration-card-processor' folder
# and the entry point is 'src/__main__.py'
main_script_path = os.path.join('src', '__main__.py')

PyInstaller.__main__.run([
    '--windowed',
    f'--name={EXE_NAME}-v{VERSION}',
    '--clean',
    f'--distpath={output_dir}\\dist',    # Final executable location
    f'--workpath={output_dir}\\build',   # Temporary build files location
    main_script_path,                    # Updated: Point to the new main entry point
    '--add-data=src/assets;assets',      # Added: Include the assets folder
    '--hidden-import=app.main_ui',       # Added: Ensure main_ui is included
    '--hidden-import=app.components.navigation', # Add hidden imports for all components
    '--hidden-import=app.components.data_form',
    '--hidden-import=app.components.status_bar',
    '--hidden-import=app.services.image_manager',
    '--hidden-import=app.services.data_manager',
    '--hidden-import=app.services.ocr',
    '--hidden-import=app.utils.system_utils',
    '--hidden-import=app.config'
])
