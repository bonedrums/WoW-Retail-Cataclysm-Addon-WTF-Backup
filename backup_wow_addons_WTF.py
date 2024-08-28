import os
import zipfile
import threading
import logging
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Function to start the backup process
def main(root):
    cancel_flag.clear()
    threading.Thread(target=backup_process, args=(root,)).start()

# Function to perform the backup
def backup_process(root):
    progress_bar.set(0)
    progress_label.configure(text="0%") # Set progress label to 0% when backup starts
    total_files = 0
    completed_files = 0
    update_interval = 100  # Update UI every 100 files

    if not selected_directory:
        messagebox.showwarning("Warning", "Please select a backup destination.")
        return

    selected_dirs = []
    if addons_toggle.get():
        selected_dirs.append(r"C:\Program Files (x86)\World of Warcraft\_classic_\Interface\AddOns")
    if wtf_toggle.get():
        selected_dirs.append(r"C:\Program Files (x86)\World of Warcraft\_classic_\WTF")

    if not selected_dirs:
        messagebox.showwarning("Warning", "Please select folders to backup.")
        return

    backup_path = os.path.join(selected_directory, "WoW_Backup.zip")
    
    logging.info(f"Starting backup for: {', '.join(selected_dirs)}")
    progress_label.configure(text="Backing up...", font=("Roboto Condensed", 14))

    # Count total files for progress bar
    for folder in selected_dirs:
        for root_folder, dirs, files in os.walk(folder):
            total_files += len(files)

    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_STORED) as backup_zip:
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
        progress_label.configure(text="", font=("Roboto Condensed", 14)) # Clear the label after completion
        logging.info("Backup Complete")

    except Exception as e:
        logging.error(f"Error during backup: {e}")
        progress_label.configure(text="Backup Failed", font=("Roboto Condensed", 14))

# Function to cancel the backup process
def cancel_backup():
    cancel_flag.set()
    progress_bar.configure(progress_color="red")
    progress_label.configure(text="")

# Function to select a directory
def select_directory():
    global selected_directory
    selected_directory = filedialog.askdirectory()
    dir_label.configure(text=selected_directory, font=("Roboto Condensed", 14))

# Function to create the GUI
def create_gui():
    global addons_toggle, wtf_toggle, progress_bar, progress_label, dir_label
    global selected_directory, cancel_flag, root

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    root = ctk.CTk()
    root.title("WoW Backup Utility")
    root.geometry("340x360")

    font = ("Roboto Condensed", 14)

    backup_frame = ctk.CTkFrame(root, corner_radius=10)
    backup_frame.pack(pady=20, padx=20, fill="x")

    ctk.CTkLabel(backup_frame, text="Select Folders to Backup", 
                 font=("Roboto Condensed", 18, "bold")).pack(pady=10)

    checkboxes_frame = ctk.CTkFrame(backup_frame)
    checkboxes_frame.pack(pady=5)

    addons_toggle = ctk.IntVar(value=1)
    wtf_toggle = ctk.IntVar(value=1)

    ctk.CTkCheckBox(checkboxes_frame, text="AddOns", variable=addons_toggle, font=font).grid(row=0, column=0, padx=35, pady=5)
    ctk.CTkCheckBox(checkboxes_frame, text="WTF", variable=wtf_toggle, font=font).grid(row=0, column=1, padx=20, pady=5)

    dir_button = ctk.CTkButton(backup_frame, text="Select Backup Destination", font=font, command=select_directory)
    dir_button.pack(pady=10)

    dir_label = ctk.CTkLabel(backup_frame, text="No destination selected", font=font, wraplength=300)
    dir_label.pack(pady=5)

    backup_button = ctk.CTkButton(backup_frame, text="Start Backup", font=font, command=lambda: main(root))
    backup_button.pack(pady=10)

    cancel_button = ctk.CTkButton(backup_frame, text="Cancel Backup", font=font, command=cancel_backup)
    cancel_button.pack(pady=5)

    progress_frame = ctk.CTkFrame(backup_frame)
    progress_frame.pack(pady=20, fill="x", padx=20)

    progress_bar = ctk.CTkProgressBar(progress_frame)
    progress_bar.pack(side="left", fill="x", expand=True, padx=(10, 0)) 
    progress_bar.set(0)

    progress_label = ctk.CTkLabel(progress_frame, text="", font=font) # Initialize to empty
    progress_label.pack(side="left", padx=(10, 10)) 

    root.mainloop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cancel_flag = threading.Event()
    selected_directory = ""
    create_gui()
