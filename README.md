# Ration Card Processor

The **Ration Card Processor** is a robust desktop application designed to streamline the process of extracting, managing, and visualizing data from ration card images. **Please note that this project is strictly designed for and tested on Windows operating systems.**

This project was born out of a desire to alleviate the repetitive and labor-intensive task of manual data entry from thousands of ration card images into Excel sheets. Observing data entry operators engaged in this arduous process inspired the development of a system that significantly reduces manual effort, making the digitization of ration card information more efficient and less prone to human error.

Built with Python and `ttkbootstrap` for a modern graphical user interface, it leverages Google's Gemini API for advanced Optical Character Recognition (OCR) to automatically pull key information from documents.

This application is ideal for organizations or individuals who need to efficiently digitize and categorize information from a large volume of ration card images, providing capabilities for data verification, correction, and structured storage.

## Features

  * **Image Browse & Navigation**: Easily browse and load folders containing ration card images. Navigate seamlessly between images using "Previous" and "Next" buttons or keyboard shortcuts.
  * **Interactive Image Viewer**:
      * **Zoom & Pan**: Interactively zoom in/out and pan across images for detailed inspection.
      * **Rotation**: Rotate images left or right to correct orientation.
  * **AI-Powered OCR**: Utilizes Google's Gemini API to perform OCR, automatically extracting critical fields such as "Ration Card ID", "Name of Card Holder", "Guardian's Name", "Head of Family", and "Village".
  * **Data Entry Form**: A user-friendly form displays the OCR-extracted data, allowing for easy review and manual correction.
  * **Data Management & Persistence**:
      * Automatically loads and saves extracted and manually updated data to an Excel file (`data.xlsx`) in the image folder.
      * Stores bounding box information in a `bbox_data.json` file for potential future visualization or reference.
      * Synchronizes records to ensure all images in the loaded folder are tracked.
  * **Real-time Status Updates**: A dedicated status bar provides immediate feedback on application operations, including loading progress and OCR status.
  * **Dynamic Theming**: Adapts to Windows' system-wide dark mode setting for a consistent user experience.
  * **Splash Screen**: Features a custom splash screen during application startup for a professional loading experience.

## Technologies Used

The project is built using:

  * **Python**: The core programming language.
  * **ttkbootstrap**: For creating modern and themed graphical user interfaces.
  * **Pillow (PIL)**: For advanced image processing capabilities, including loading, resizing, and rotation.
  * **pandas**: For efficient data manipulation and management, particularly with Excel files.
  * **Google Generative AI (Gemini API)**: Powers the OCR functionality for intelligent text extraction from images.
  * **`tkinter`**: Python's standard GUI library, underlying `ttkbootstrap`.
  * **`json`**: For handling JSON data, especially bounding box information.
  * **`os`**: For file system operations.
  * **`threading`**: For handling background tasks like OCR to keep the UI responsive.
  * **`openpyxl`**: Used by pandas for reading and writing Excel files (`.xlsx`).
  * **`PyInstaller`**: For packaging the Python application into a standalone executable.
  * \*\*\*\*`winreg`**: Used for Windows-specific functionalities like dark mode detection and crucial for Windows OS compatibility.**

## Installation

To set up and run the Ration Card Processor **on Windows**, follow these steps:

1.  **Clone the Repository (if applicable):**

    ```bash
    git clone https://github.com/discoveraniket/ration_card_processor
    cd ration_card_processor
    ```

    *(Note: Since this is a single project, you may just have the files directly.)*

2.  **Create a Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment (Windows Command Prompt/PowerShell):**

    ```bash
    .\venv\Scripts\activate
    ```

4.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up Google Gemini API Key:**

      * Obtain a `GEMINI_API_KEY` from the Google AI Studio.
      * Set it as an environment variable before running the application:
          * **Windows (Command Prompt):**
            ```bash
            set GEMINI_API_KEY=YOUR_API_KEY_HERE
            ```
          * **Windows (PowerShell):**
            ```powershell
            $env:GEMINI_API_KEY="YOUR_API_KEY_HERE"
            ```
        *(For permanent setup, add this to your system's environment variables.)*

## Usage

1.  **Run the Application:**

    ```bash
    python __main__.py
    ```

    A splash screen will appear, followed by the main application window.

2.  **Browse for Images:**

      * Click the "Browse" button in the navigation toolbar.
      * Select the folder containing your ration card images (`.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`).
      * The application will load the first image and either load an existing `data.xlsx` or create a new one, synchronizing image names.

3.  **Navigate Images:**

      * Use the "Previous" and "Next" buttons, or the `Left Arrow` and `Right Arrow` keys to cycle through images.

4.  **Perform OCR:**

      * With an image loaded, click the "OCR" button or press `Ctrl + Enter`.
      * The application will send the image to the Gemini API for text extraction.
      * Extracted data will populate the "Card Details" form.

5.  **Update Data:**

      * Manually correct or modify any fields in the "Card Details" form.
      * Click "Update Data" or press `Ctrl + S` to save the changes to the internal dataset.

6.  **Save Changes:**

      * Click the "Save" button to persist all current data to `data.xlsx` and `bbox_data.json` in the browsed image folder.
      * It's recommended to save regularly.

## Project Structure

```
.
├── build.py                # PyInstaller build script
├── LICENSE                 # Project license file
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
└── src/
    ├── __main__.py         # Application entry point
    ├── app/
    │   ├── __init__.py
    │   ├── config.py       # Configuration settings
    │   ├── main_ui.py      # Main application UI
    │   ├── components/
    │   │   ├── __init__.py
    │   │   ├── data_form.py    # Data entry form component
    │   │   ├── navigation.py   # Navigation toolbar component
    │   │   └── status_bar.py   # Status bar component
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── data_manager.py # Data loading and saving
    │   │   ├── image_manager.py# Image handling
    │   │   └── ocr.py          # OCR service
    │   └── utils/
    │       ├── __init__.py
    │       └── system_utils.py # System utility functions
    └── assets/
        ├── app_icon.ico    # Application icon
        └── app_icon.png    # Application icon
```

## Future Updates

While the current version is functional, several exciting enhancements are planned:

-   **Cross-Platform Support**: Refactor the application to be fully compatible with **Linux**, replacing Windows-specific code (like `winreg`) with cross-platform alternatives.
-   **Implement UI Buttons**:
    -   **Save Button**: Develop the "Save" functionality to persist all data changes without requiring a file rename.
    -   **Options Button**: Implement the "Options" panel to manage application settings.
-   **Batch OCR Processing**: Introduce a feature to run OCR on all images in a folder at once.
-   **Bounding Box Visualization**: Use the saved `bbox_data.json` to draw boxes on the image, showing where the OCR extracted text from.
-   **Advanced Data Validation**: Add more robust validation for data fields to improve accuracy.
-   **Configuration & Settings**:
    -   **In-App Theme Switching**: Allow users to toggle between light and dark modes from the Options panel.
    -   **Customizable File Renaming**: Add an option to disable or configure the automatic renaming of image files.

## About the Developer

This project was created by **Aniket Sarkar**, a Python developer with expertise in scripting, automation, and AI integration. Aniket has hands-on experience building practical desktop and web applications, including commercial automation tools and an AI-powered Macbeth learning app prototype using the Gemini API. He is passionate about leveraging technology to solve real-world problems and is open to collaboration and new opportunities.

- **GitHub Profile:** [https://github.com/discoveraniket](https://github.com/discoveraniket)

## Contributing

Contributions are welcome\! If you have suggestions for improvements, bug fixes, or new features, please feel free to:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/YourFeature`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add new feature'`).
5.  Push to the branch (`git push origin feature/YourFeature`).
6.  Open a Pull Request.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details (if applicable, otherwise state as "MIT License" or similar).

## Acknowledgements

  * **ttkbootstrap**: For providing a beautiful and easy-to-use themed `tkinter` experience.
  * **Google Gemini API**: For powering the intelligent OCR capabilities of this application.
