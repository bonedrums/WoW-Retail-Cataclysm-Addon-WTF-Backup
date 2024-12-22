import os
import shutil
from datetime import datetime
import zipfile
import threading
import logging
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# Function to start the backup process
def main(root):
    cancel_flag.clear()  # Clear the cancel flag before starting a new backup
    threading.Thread(target=backup_process, args=(root,)).start()

# Function to generate the zip file name based on selected options
def generate_zip_name():
    selected_options = []

    if addons_toggle.get():
        selected_options.append("AddOns")
    if wtf_toggle.get():
        selected_options.append("WTF")
    if retail_toggle.get():
        selected_options.append("Retail")
    if cataclysm_toggle.get():
        selected_options.append("Cataclysm")

    # Join selected options to form part of the file name
    options_part = " - ".join(selected_options)
    
    # Form the final zip file name without timestamp
    zip_name = f"WoW_Backup - {options_part}.zip"
    
    return zip_name

# Function to perform the backup
def backup_process(root):
    progress_bar.set(0)
    progress_label.configure(text="0%")  # Set progress label to 0% when backup starts
    total_files = 0
    completed_files = 0
    update_interval = 100  # Update UI every 100 files

    if not selected_directory:
        messagebox.showwarning("Warning", "Please select a backup destination.")
        return

    # Define the selected directories based on checkbox states
    selected_dirs = []

    if retail_toggle.get():
        if addons_toggle.get():
            selected_dirs.append("/Applications/World of Warcraft/_retail_/Interface/AddOns")
        if wtf_toggle.get():
            selected_dirs.append("/Applications/World of Warcraft/_retail_/WTF")

    elif cataclysm_toggle.get():
        if addons_toggle.get():
            selected_dirs.append("/Applications/World of Warcraft/_classic_/Interface/AddOns")  # Corrected Cataclysm AddOns path
        if wtf_toggle.get():
            selected_dirs.append("/Applications/World of Warcraft/_classic_/WTF")  # Ensure correct WTF path for Cataclysm

    else:
        # If no Retail or Cataclysm are selected, default to Classic
        if addons_toggle.get():
            selected_dirs.append("/Applications/World of Warcraft/_classic_/Interface/AddOns")
        if wtf_toggle.get():
            selected_dirs.append("/Applications/World of Warcraft/_classic_/WTF")

    # Print the selected directories for verification
    for directory in selected_dirs:
        print(f"Selected Directory: {directory}")

    if not selected_dirs:
        messagebox.showwarning("Warning", "Please select folders to backup.")
        return
    # Generate the zip file name dynamically
    zip_name = generate_zip_name()
    backup_path = os.path.join(selected_directory, zip_name)
    
    logging.info(f"Starting backup for: {', '.join(selected_dirs)}")
    progress_label.configure(text="Backing up...", font=("Adobe Clean Condensed", 14))

    # Count total files for progress bar
    for folder in selected_dirs:
        for root_folder, dirs, files in os.walk(folder):
            total_files += len(files)

    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:  # Ensuring zip format
            for folder in selected_dirs:
                for root_folder, dirs, files in os.walk(folder):
                    for file in files:
                        if cancel_flag.is_set():
                            progress_bar.configure(progress_color="red")
                            progress_label.configure(text="")
                            return

                        file_path = os.path.join(root_folder, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(folder))
                        backup_zip.write(file_path, arcname)
                        logging.info(f"Added {file_path} as {arcname}")

                        completed_files += 1
                        if completed_files % update_interval == 0 or completed_files == total_files:
                            progress = completed_files / total_files
                            progress_bar.set(progress)
                            progress_label.configure(text=f"{int(progress * 100)}%")
                            root.update_idletasks()

        progress_bar.set(1.0)
        progress_label.configure(text="", font=("Adobe Clean Condensed", 16))  # Clear the label after completion
        logging.info("Backup Complete")

    except Exception as e:
        logging.error(f"Error during backup: {e}")
        progress_label.configure(text="Backup Failed", font=("Adobe Clean Condensed", 16))

# Function to cancel the backup process
def cancel_backup():
    cancel_flag.set()
    progress_bar.configure(progress_color="red")
    progress_label.configure(text="")

# Function to select a directory
def select_directory():
    global selected_directory  # Ensure it's using the global variable
    selected_directory = filedialog.askdirectory()
    dir_label.configure(text=selected_directory, font=("Adobe Clean Condensed", 14))

# Ensure at least one of Retail or Cataclysm is always checked
def enforce_checkbox_state():
    if not retail_toggle.get() and not cataclysm_toggle.get():
        cataclysm_toggle.set(1)  # Default to Cataclysm if both are unchecked

# Callback function to ensure Retail and Cataclysm are mutually exclusive
def toggle_retail_cataclysm(checkbox, other_checkbox):
    if checkbox.get() == 1:
        other_checkbox.set(0)
    enforce_checkbox_state()

# Function to create the GUI
def create_gui():
    global addons_toggle, wtf_toggle, retail_toggle, cataclysm_toggle, progress_bar, progress_label, dir_label
    global selected_directory, cancel_flag, root

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    root = ctk.CTk()
    root.title("WoW Backup Utility")
    root.geometry("360x450")

    # Removed icon-related code

    font = ("Adobe Clean Condensed", 15)

    # Initialize toggle variables here, after creating the root window
    addons_toggle = ctk.IntVar(value=1)
    wtf_toggle = ctk.IntVar(value=1)
    retail_toggle = ctk.IntVar(value=0)  # Retail starts unchecked
    cataclysm_toggle = ctk.IntVar(value=1)  # Cataclysm starts checked by default

    backup_frame = ctk.CTkFrame(root, corner_radius=10)
    backup_frame.pack(pady=20, padx=20, fill="x")

    ctk.CTkLabel(backup_frame, text="Select Folders to Backup", 
                 font=("Adobe Clean Condensed", 18, "bold")).pack(pady=10)

    checkboxes_frame = ctk.CTkFrame(backup_frame)
    checkboxes_frame.pack(pady=5)

    ctk.CTkCheckBox(checkboxes_frame, text="AddOns", variable=addons_toggle, font=font).grid(row=0, column=0, padx=10, pady=5)
    ctk.CTkCheckBox(checkboxes_frame, text="WTF", variable=wtf_toggle, font=font).grid(row=0, column=1, padx=10, pady=5)
    
    # Retail and Cataclysm checkboxes with mutual exclusion and default
    retail_checkbox = ctk.CTkCheckBox(checkboxes_frame, text="Retail", variable=retail_toggle, font=font,
                                      command=lambda: toggle_retail_cataclysm(retail_toggle, cataclysm_toggle))
    retail_checkbox.grid(row=1, column=0, padx=10, pady=5)
    
    cataclysm_checkbox = ctk.CTkCheckBox(checkboxes_frame, text="Cataclysm", variable=cataclysm_toggle, font=font,
                                         command=lambda: toggle_retail_cataclysm(cataclysm_toggle, retail_toggle))
    cataclysm_checkbox.grid(row=1, column=1, padx=10, pady=5)

    dir_button = ctk.CTkButton(backup_frame, text="Select Backup Destination", font=(font[0], font[1]), command=select_directory)
    dir_button.pack(pady=10)

    dir_label = ctk.CTkLabel(backup_frame, text="No destination selected", font=font, wraplength=300)
    dir_label.pack(pady=5)

    backup_button = ctk.CTkButton(backup_frame, text="Start Backup", font=(font[0], font[1]), command=lambda: main(root))
    backup_button.pack(pady=10)

    cancel_button = ctk.CTkButton(backup_frame, text="Cancel Backup", font=(font[0], font[1]), command=cancel_backup)
    cancel_button.pack(pady=5)

    progress_frame = ctk.CTkFrame(backup_frame)
    progress_frame.pack(pady=20, fill="x", padx=20)

    progress_label = ctk.CTkLabel(progress_frame, text="", font=font)  # Initialize to empty
    progress_label.pack(side="top", pady=(0, 10))

    progress_bar = ctk.CTkProgressBar(progress_frame)
    progress_bar.pack(side="top", fill="x", expand=True, padx=(5, 10)) 
    progress_bar.set(0)

    root.mainloop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cancel_flag = threading.Event()
    selected_directory = ""
    create_gui()
