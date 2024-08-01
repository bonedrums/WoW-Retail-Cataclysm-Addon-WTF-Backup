<div align="center">
  <img src="https://github.com/user-attachments/assets/0fe9cf33-5d41-42e0-a438-7753657ed4c8" alt="Image" />
</div>

# WoW Cataclysm Addons and WTF Backup

This Python program helps you back up World of Warcraft (WoW) Classic addon and configuration files. It uses a modern GUI built with customtkinter.

## Features

- **Backup Creation:** Select directories for WoW addons and settings.
- **Zip and Move:** Archive directories into a timestamped ZIP file and move it to a chosen destination.
- **Progress Tracking:** Real-time progress display.
- **Cancel Backup:** Option to cancel the backup process at any time.
- **Update Addons:** Download and update specified WoW addons from GitHub repositories.

## Dependencies

- Python 3.x
- customtkinter
- requests

## Usage

1. **Install Dependencies:**
   ```sh
   pip install customtkinter requests
2. Launch the Script:

    Open a command prompt.
    Navigate to the directory with backup_wow_addons_wtf.py.
    Run the script:

    sh

        python backup_wow_addons_wtf.py

    Follow On-screen Instructions:
        Select backup directories and options using the GUI.
        Click "Start Backup" to begin.
        Click "Cancel Backup" to stop at any time.

3. Update Addons Section

The Update Addons section allows you to keep your WoW addons up to date. It downloads the latest versions of specified addons from GitHub repositories and replaces the existing files in the WoW AddOns directory.

    Supported Addons:
        Hekili
        Eltruism
        ElvUI

    Usage:
        Select the addons you want to update using the checkboxes.
        Click "Update Addons" to start the update process.
        The application will display progress and completion status for each addon.

4. Instructions

    Ensure Python and required dependencies are installed.
    Ensure sufficient disk space and permissions for the backup destination.
