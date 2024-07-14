import os
import zipfile
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading

default_directory = ""
selected_directory = ""
cancel_flag = threading.Event()

def zip_folders(folder_paths, zip_name, progress_callback, file_callback):
    total_files = sum([len(files) for _, _, files in os.walk(folder_paths[0])] + 
                      [len(files) for _, _, files in os.walk(folder_paths[1])])
    file_count = 0

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for folder in folder_paths:
            for root, _, files in os.walk(folder):
                if cancel_flag.is_set():
                    return
                for file in files:
                    if cancel_flag.is_set():
                        return
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.join(folder, '..'))
                    zipf.write(file_path, arcname)
                    file_count += 1
                    progress_callback(file_count / total_files * 100)
                    file_callback(file_path)

def move_file(src, dst, progress_callback):
    total_size = os.path.getsize(src)
    copied_size = 0

    with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
        while True:
            if cancel_flag.is_set():
                os.remove(dst)  # Clean up incomplete file
                return
            buf = fsrc.read(1024 * 1024)  # read in chunks of 1MB
            if not buf:
                break
            fdst.write(buf)
            copied_size += len(buf)
            progress_callback(copied_size / total_size * 100)
    
    os.remove(src)  # remove source file after copying

def update_progress(percentage):
    progress_bar.set(percentage / 100)
    progress_label.configure(text=f"{percentage:.0f}%", font=("Arial Narrow", 12))

def update_files_label(file_path):
    if "AddOns" in file_path:
        parts = file_path.split("AddOns")
        if len(parts) > 1:
            sub_parts = parts[1].split(os.sep)
            if len(sub_parts) > 1:
                addon_folder = sub_parts[1]
                files_label.configure(text=f"Processing: {addon_folder}", wraplength=500)
                return
    files_label.configure(text="")

def select_directory():
    global selected_directory
    selected_directory = filedialog.askdirectory()
    if selected_directory:
        dir_label.configure(text=f"Selected Backup Destination:\n{selected_directory}")

def backup_to_desktop():
    global selected_directory
    selected_directory = os.path.join(os.path.expanduser("~"), "Desktop")
    dir_label.configure(text=f"Selected Backup Destination:\n{selected_directory}")

def main():
    global cancel_flag
    cancel_flag.clear()  # Reset the cancel flag

    if not selected_directory:
        messagebox.showwarning("Warning", "No directory selected!")
        return

    folder_paths = [
        r"C:\Program Files (x86)\World of Warcraft\_classic_\Interface\AddOns",
        r"C:\Program Files (x86)\World of Warcraft\_classic_\WTF"
    ]

    now = datetime.now()
    date_time_str = now.strftime("%m-%d-%y - %I-%M %p")  # Adjusted format for hour and month
    zip_name = f"WTF & Addons Backup - {date_time_str}.zip"

    progress_label.configure(text="Processing...", font=("Arial Narrow", 16, "bold"))
    files_label.configure(text="Processing: ", wraplength=500)

    # Reset progress bar to 0%
    progress_bar.set(0)

    # Thread for zipping and moving
    def backup_process():
        zip_folders(folder_paths, zip_name, update_progress, update_files_label)
        if not cancel_flag.is_set():
            target_path = os.path.join(selected_directory, zip_name)
            move_file(zip_name, target_path, update_progress)
            progress_label.configure(text=f"Completed!", font=("Arial Narrow", 12, "bold"))
        else:
            progress_label.configure(text="Process Cancelled", font=("Arial Narrow", 12, "bold"))

    backup_thread = threading.Thread(target=backup_process)
    backup_thread.start()

def cancel_backup():
    global cancel_flag
    cancel_flag.set()

if __name__ == "__main__":
    ctk.set_appearance_mode("light")  # Set appearance mode to dark
    ctk.set_default_color_theme("green")  # Set color theme to dark-blue

    app = ctk.CTk()
    app.geometry("400x350")  # Adjusted width and height
    app.title("WoW Cataclysm Addons Backup")

    # Modern styling for labels
    progress_frame = ctk.CTkFrame(app)
    progress_frame.pack(pady=20, padx=20, fill="x")

    progress_bar = ctk.CTkProgressBar(progress_frame, orientation="horizontal", mode="determinate")
    progress_bar.pack(side="left", fill="x", expand=True, padx=(20, 20))
    progress_bar.set(0)

    progress_label = ctk.CTkLabel(progress_frame, text="0%", font=("Arial Narrow", 11))
    progress_label.pack(side="left", padx=(0, 20))

    files_label = ctk.CTkLabel(app, text="", font=("Arial Narrow", 14, "bold"))  # Initialize with empty text
    files_label.pack(pady=10, anchor="center")

    dir_label = ctk.CTkLabel(app, text="No Directory Selected", font=("Arial Narrow", 14, "bold"))
    dir_label.pack(pady=10, anchor="center")

    button_frame = ctk.CTkFrame(app)
    button_frame.pack(pady=10)

    desktop_button = ctk.CTkButton(button_frame, text="Backup to Desktop", command=backup_to_desktop, font=("Arial Narrow", 12, "bold"))
    desktop_button.pack(side="left", padx=10, pady=10, ipadx=5)

    select_dir_button = ctk.CTkButton(button_frame, text="Manual Location Backup", command=select_directory, font=("Arial Narrow", 12, "bold"))
    select_dir_button.pack(side="left", padx=10, pady=10, ipadx=5)

    action_button_frame = ctk.CTkFrame(app)
    action_button_frame.pack(pady=20)

    start_button = ctk.CTkButton(action_button_frame, text="Start Backup", command=main, font=("Arial Narrow", 12, "bold"))
    start_button.pack(side="left", padx=10, pady=10, ipadx=5)

    cancel_button = ctk.CTkButton(action_button_frame, text="Cancel Backup", command=cancel_backup, font=("Arial Narrow", 11))
    cancel_button.pack(side="left", padx=10, pady=10, ipadx=5)

    selected_directory = default_directory

    app.mainloop()
