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

2.  **Run**
    ```bash
    python chronosort_photos.py
    ```
3.  **Select a Folder**
    *   Choose the folder with your photos.

4.  **Review the Preview**
    *   Check for all planned renames.

5.  **Confirm the Operation**