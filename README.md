WoW Cataclysm Addons Backup

This Python program facilitates backing up World of Warcraft (WoW) Classic addon and configuration files from specific directories to a chosen destination. It uses a graphical user interface (GUI) built with customtkinter for a modern look and functionality.
Features

    Backup Creation: Allows selection of directories containing WoW addon and configuration files.
    Zip and Move: Archives selected directories into a timestamped ZIP file and moves it to the chosen backup destination.
    Progress Tracking: Displays real-time progress of the backup process including file-by-file progress and overall completion percentage.
    Cancel Backup: Provides an option to cancel the backup process at any time.

Dependencies

    Python 3.x
    customtkinter (custom GUI library)

Usage

    Select Backup Destination:
        Click "Backup to Desktop" to backup files to your desktop.
        Or use "Manual Location Backup" to choose a custom backup destination.

    Start Backup:
        Click "Start Backup" to begin the backup process. Progress will be displayed in real-time.

    Cancel Backup:
        Click "Cancel Backup" to halt the backup process mid-operation.

Instructions

    Ensure Python and required dependencies are installed.
    Run the script (python script_name.py) to launch the GUI.
    Follow on-screen prompts to select backup directories and start the backup process.

Notes

    This program assumes specific directory paths for WoW addon and configuration files.
    Ensure sufficient disk space and permissions for writing to the selected backup destination.
