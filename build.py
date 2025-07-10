import PyInstaller.__main__
import os
import sys
from pathlib import Path

# --- Path Setup ---
# Add the 'src' directory to the Python path so 'app' can be found
current_dir = Path(__file__).parent.resolve()
src_path = current_dir / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# --- Configuration ---
# Import CONFIG from the app directory to get version and app names
try:
    from app.config import CONFIG
except ImportError as e:
    print(
        f"Error: Could not import CONFIG from app.config. Make sure the file exists and is accessible."
    )
    print(f"Details: {e}")
    sys.exit(1)

# Use values from CONFIG
VERSION = CONFIG.VERSION
APP_NAME = CONFIG.APP_NAME
EXE_NAME = CONFIG.EXE_NAME

# --- Output Directories ---
# Define relative output directories for build artifacts
dist_dir = current_dir / "dist"
build_dir = current_dir / "build"

# --- Main Script ---
# Path to the main entry point file (__main__.py)
main_script_path = src_path / "__main__.py"


# --- Auto-discover Hidden Imports ---
def find_hidden_imports(app_path):
    """
    Automatically finds all Python modules in the 'app' directory to be used as hidden imports.
    """
    hidden_imports = []
    base_path = app_path.parent
    for path in Path(app_path).rglob("*.py"):
        if path.name == "__init__.py":
            continue
        # Convert file path to module path (e.g., src/app/main_ui.py -> app.main_ui)
        relative_path = path.relative_to(base_path)
        module_path = str(relative_path.with_suffix("")).replace(os.path.sep, ".")
        hidden_imports.append(f"--hidden-import={module_path}")
    return hidden_imports


# Find all modules in the 'src/app' directory
app_full_path = src_path / "app"
hidden_imports_args = find_hidden_imports(app_full_path)

# --- PyInstaller Execution ---
# Construct the command for PyInstaller
pyinstaller_command = [
    "--windowed",
    "--noconfirm",  # Overwrite output directory without asking
    f"--name={EXE_NAME}-v{VERSION}",
    "--clean",
    f"--distpath={dist_dir}",
    f"--workpath={build_dir}",
    str(main_script_path),
    "--add-data=src/assets;assets",
] + hidden_imports_args

print("Running PyInstaller with the following command:")
print(" ".join(pyinstaller_command))

# Execute PyInstaller
PyInstaller.__main__.run(pyinstaller_command)
