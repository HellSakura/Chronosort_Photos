[Read this in Chinese (简体中文)](README_zh-CN.md)

---

# ChronoSort Photos

A Python script to rename photo files based on their EXIF date or file modification date.

## Features

*   **Date Detection**: Prioritizes dates in the following order:
    1.  EXIF "Date Taken"
    2.  File "Date Modified"
    3.  File "Date Created"
*   **Post-processing**:
    *   Resolves filename conflicts by adding a numerical suffix.
    *   Skips files that are already in the correct format.

## Usage

1.  **Install Dependencies**
    ```bash
    pip install Pillow
    ```
2.  **Run the Script**
    ```bash
    python chronosort_photos.py
    ```
3.  **Select Folder**
4.  **Review Preview**  
    Check the list of proposed changes printed in the terminal.
5.  **Confirm**  
    Type `yes` and press Enter to apply the changes.