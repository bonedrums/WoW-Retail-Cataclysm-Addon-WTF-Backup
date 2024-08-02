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

ADDONS = [
    ("https://github.com/Hekili/hekili/archive/refs/heads/cataclysm.zip", "Hekili"),
    ("https://github.com/eltreum0/eltruism/archive/refs/heads/main.zip", "Eltruism"),
    ("https://github.com/tukui-org/ElvUI/archive/refs/heads/main.zip", "ElvUI")
]

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def update_addons():
    temp_dir = os.path.join(os.path.dirname(__file__), "temp_addons")
    dest_base_path = r"C:\Program Files (x86)\World of Warcraft\_classic_\Interface\AddOns"

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    def download_and_extract(url, folder_name):
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
                    update_label.configure(text=f"{folder_name} - Updated {replaced_count} Files")
                    if updated_files:
                        logging.info(f"{folder_name} - List of updated files:")
                        for updated_file in updated_files:
                            logging.info(updated_file)
                else:
                    logging.warning(f"{folder_name} - Extracted folder is empty or not found")
                    update_label.configure(text=f"{folder_name} - Extracted folder is empty or not found")
            else:
                logging.error(f"{folder_name} - Downloaded file is not a valid zip file")
                update_label.configure(text=f"{folder_name} - Downloaded file is not a valid zip file")

            update_progress(100)  # Set progress bar to 100% when done

        except Exception as e:
            logging.error(f"Failed to update {folder_name}: {e}")
            update_label.configure(text=f"Failed to update {folder_name}: {e}")
        finally:
            if os.path.exists(local_zip_path):
                os.remove(local_zip_path)
            if os.path.exists(extract_path):
                shutil.rmtree(extract_path)

    threads = []
    for url, folder_name in ADDONS:
        if globals()[f"{folder_name.lower()}_toggle"].get():
            thread = threading.Thread(target=download_and_extract, args=(url, folder_name))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

def zip_folders(folder_paths, zip_path, progress_callback, file_callback):
    logging.info(f"Starting zipping folders: {folder_paths}")
    total_files = sum([len(files) for folder in folder_paths for _, _, files in os.walk(folder)])
    file_count = 0

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
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
                    logging.info(f"Zipped file: {file_path}")

    logging.info(f"Zip file created: {zip_path}")

def copy_file(src, dst, progress_callback):
    logging.info(f"Copying file from {src} to {dst}")
    if not os.path.exists(src):
        logging.error(f"Source file not found: {src}")
        return
    
    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(dst), exist_ok=True)

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

def delete_file(src):
    time.sleep(3)  # Wait for 3 seconds before attempting to delete
    try:
        os.remove(src)
        logging.info(f"Successfully deleted source file: {src}")
    except PermissionError as e:
        logging.error(f"Error deleting file: {e}")

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

def main():
    global cancel_flag
    cancel_flag.clear()  # Reset the cancel flag

    if not selected_directory:
        messagebox.showwarning("Warning", "No directory selected!")
        return

    folder_paths = []
    if addons_toggle.get() == 1:
        folder_paths.append(r"C:\Program Files (x86)\World of Warcraft\_classic_\Interface\AddOns")
    if wtf_toggle.get() == 1:
        folder_paths.append(r"C:\Program Files (x86)\World of Warcraft\_classic_\WTF")

    if not folder_paths:
        messagebox.showwarning("Warning", "No folders selected for backup!")
        return

    now = datetime.now()
    date_time_str = now.strftime("%m-%d-%y - %I-%M %p")  # Adjusted format for hour and month
    zip_name = f"WTF & Addons Backup - {date_time_str}.zip"
    zip_path = os.path.join(selected_directory, zip_name)

    progress_label.configure(text="Processing...", font=("Arial Narrow", 16, "bold"))
    files_label.configure(text="Processing: ", wraplength=500)

    # Reset progress bar to 0%
    progress_bar.set(0)

    # Thread for zipping and moving
    def backup_process():
        logging.info(f"Current working directory: {os.getcwd()}")
        zip_folders(folder_paths, zip_path, update_progress, update_files_label)
        if not cancel_flag.is_set():
            if os.path.exists(zip_path):
                logging.info(f"Zip file exists: {zip_path}")
                progress_label.configure(text=f"Completed!", font=("Arial Narrow", 12, "bold"))
                logging.info(f"Backup completed successfully")
            else:
                progress_label.configure(text="Error: Zip file not created", font=("Arial Narrow", 12, "bold"))
                logging.error("Zip file not created.")
        else:
            progress_label.configure(text="Process Cancelled", font=("Arial Narrow", 12, "bold"))
            logging.info("Backup process cancelled.")

    backup_thread = threading.Thread(target=backup_process)
    backup_thread.start()

def cancel_backup():
    global cancel_flag
    cancel_flag.set()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # Set appearance mode
    ctk.set_default_color_theme("blue")  # Set default color theme

    app = ctk.CTk()
    app.geometry("400x550")  # Adjusted height
    app.title("WoW Cataclysm Backup Manager")

    # Backup Section
    backup_frame = ctk.CTkFrame(app)
    backup_frame.pack(pady=10, padx=20, fill="x")

    backup_label = ctk.CTkLabel(backup_frame, text="Backup Addons and Settings", font=("Arial Narrow", 16, "bold"))
    backup_label.pack(pady=10, anchor="center")

    progress_frame = ctk.CTkFrame(backup_frame)
    progress_frame.pack(pady=10, fill="x")

    progress_bar = ctk.CTkProgressBar(progress_frame, orientation="horizontal", mode="determinate")
    progress_bar.pack(side="left", fill="x", expand=True, padx=(20, 20))
    progress_bar.set(0)

    progress_label = ctk.CTkLabel(progress_frame, text="0%", font=("Arial Narrow", 11))
    progress_label.pack(side="left", padx=(0, 20))

    files_label = ctk.CTkLabel(backup_frame, text="", font=("Arial Narrow", 14, "bold"))  # Initialize with empty text
    files_label.pack(pady=10, anchor="center")

    dir_label = ctk.CTkLabel(backup_frame, text="No Directory Selected", font=("Arial Narrow", 14, "bold"))
    dir_label.pack(pady=10, anchor="center")

    action_button_frame = ctk.CTkFrame(backup_frame)
    action_button_frame.pack(pady=5)

    start_button = ctk.CTkButton(action_button_frame, text="Start Backup", command=main, font=("Arial Narrow", 12, "bold"))
    start_button.pack(side="left", padx=10, pady=10, ipadx=5)

    cancel_button = ctk.CTkButton(action_button_frame, text="Cancel Backup", command=cancel_backup, font=("Arial Narrow", 12, "bold"))
    cancel_button.pack(side="left", padx=10, pady=10, ipadx=5)

    toggle_frame = ctk.CTkFrame(backup_frame)
    toggle_frame.pack(pady=5)

    addons_toggle = ctk.CTkCheckBox(toggle_frame, text="AddOns")
    addons_toggle.pack(side="left", padx=10, pady=10)

    wtf_toggle = ctk.CTkCheckBox(toggle_frame, text="WTF")
    wtf_toggle.pack(side="left", padx=10, pady=10)

    select_dir_button = ctk.CTkButton(backup_frame, text="Choose Backup Location", command=select_directory, font=("Arial Narrow", 12, "bold"))
    select_dir_button.pack(pady=10, ipadx=5)

    # Update Section
    update_frame = ctk.CTkFrame(app)
    update_frame.pack(pady=10, padx=20, fill="x")

    update_label = ctk.CTkLabel(update_frame, text="Update Addons", font=("Arial Narrow", 16, "bold"))
    update_label.pack(pady=10, anchor="center")

    addon_toggle_frame = ctk.CTkFrame(update_frame)
    addon_toggle_frame.pack(pady=5)

    hekili_toggle = ctk.CTkCheckBox(addon_toggle_frame, text="Hekili")
    hekili_toggle.pack(side="left", padx=10, pady=10)

    eltruism_toggle = ctk.CTkCheckBox(addon_toggle_frame, text="Eltruism")
    eltruism_toggle.pack(side="left", padx=10, pady=10)

    elvui_toggle = ctk.CTkCheckBox(addon_toggle_frame, text="ElvUI")
    elvui_toggle.pack(side="left", padx=10, pady=10)

    update_addons_button = ctk.CTkButton(update_frame, text="Update Addons", command=lambda: threading.Thread(target=update_addons).start(), font=("Arial Narrow", 12, "bold"))
    update_addons_button.pack(pady=10, ipadx=5)

    app.mainloop()
