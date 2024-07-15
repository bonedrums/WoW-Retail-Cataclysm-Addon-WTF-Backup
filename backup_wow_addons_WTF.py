import os
import zipfile
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import requests
import shutil
import logging
import hashlib
import webbrowser

default_directory = ""
selected_directory = ""
cancel_flag = threading.Event()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def update_addons():
    script_dir = os.path.dirname(__file__)
    temp_dir = os.path.join(script_dir, "temp_addons")
    dest_base_path = r"C:\Program Files (x86)\World of Warcraft\_classic_\Interface\AddOns"

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    url = "https://github.com/Hekili/hekili/archive/refs/heads/cataclysm.zip"
    folder_name = "Hekili"

    try:
        logging.info(f"Processing addon: {folder_name}")

        local_zip_path = os.path.join(temp_dir, f"{folder_name}.zip")
        extract_path = os.path.join(temp_dir, folder_name)
        dest_path = os.path.join(dest_base_path, folder_name)

        logging.info(f"Downloading {folder_name} from {url}")

        response = requests.get(url)
        response.raise_for_status()
        with open(local_zip_path, 'wb') as file:
            file.write(response.content)

        if zipfile.is_zipfile(local_zip_path):
            with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            if os.listdir(extract_path):
                extracted_folder = os.listdir(extract_path)[0]
                source_dir = os.path.join(extract_path, extracted_folder)

                if not os.path.exists(dest_path):
                    os.makedirs(dest_path)

                replaced_count = 0
                updated_files = []

                for root, dirs, files in os.walk(source_dir):
                    relative_path = os.path.relpath(root, source_dir)
                    dest_dir = os.path.join(dest_path, relative_path)

                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)

                    for file in files:
                        src_file = os.path.join(root, file)
                        dest_file = os.path.join(dest_dir, file)

                        if os.path.exists(dest_file):
                            src_hash = calculate_md5(src_file)
                            dest_hash = calculate_md5(dest_file)
                            if src_hash != dest_hash:
                                shutil.copy2(src_file, dest_file)
                                replaced_count += 1
                                updated_files.append(dest_file)
                        else:
                            shutil.copy2(src_file, dest_file)
                            replaced_count += 1
                            updated_files.append(dest_file)

                logging.info(f"{folder_name} - Updated {replaced_count} files")
                if updated_files:
                    logging.info(f"{folder_name} - List of updated files:")
                    for updated_file in updated_files:
                        logging.info(updated_file)
            else:
                logging.warning(f"{folder_name} - Extracted folder is empty or not found")
        else:
            logging.error(f"{folder_name} - Downloaded file is not a valid zip file")

        update_progress(100)  # Set progress bar to 100% when done

    except Exception as e:
        logging.error(f"Failed to update {folder_name}: {e}")
    finally:
        if os.path.exists(local_zip_path):
            os.remove(local_zip_path)
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    logging.info("Hekili has been successfully updated.")
    messagebox.showinfo("Update Results", "Hekili has been successfully updated.")

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

def open_clip():
    webbrowser.open("https://clips.twitch.tv/MotionlessFitLegRitzMitz-YTDsJM6oh6an4D0N")

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
    ctk.set_appearance_mode("light")  # Set appearance mode
    ctk.set_default_color_theme("blue")  # Set default color theme

    app = ctk.CTk()
    app.geometry("400x410")  # Adjusted width and height
    app.title("WoW Cataclysm Addons Backup v1.01")

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

    cancel_button = ctk.CTkButton(action_button_frame, text="Cancel Backup", command=cancel_backup, font=("Arial Narrow", 12, "bold"))
    cancel_button.pack(side="left", padx=10, pady=10, ipadx=5)

    action_button_frame = ctk.CTkFrame(app)
    action_button_frame.pack(pady=20)

    # Add the button to update addons
    update_addons_button = ctk.CTkButton(action_button_frame, text="Update Hekili Profiles", command=update_addons, font=("Arial Narrow", 12, "bold"))
    update_addons_button.pack(side="left", padx=10, pady=10, ipadx=5)

    # Lidond is a Dumbass
    update_addons_button = ctk.CTkButton(action_button_frame, text="Lidond is a Dumbass", command=open_clip, font=("Arial Narrow", 12, "bold"))
    update_addons_button.pack(side="left", padx=10, pady=10, ipadx=5)

    selected_directory = default_directory

    app.mainloop()
