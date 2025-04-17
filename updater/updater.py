import os
import requests
import zipfile
import io
import shutil
import tkinter as tk


CLIENT_DIR = os.path.join("client")
INTERNAL_DIR = os.path.join(CLIENT_DIR, "_internal")

def prompt_user(version):
    root = tk.Tk()
    root.withdraw()  # Hide main window
    result = tk.messagebox.askyesno("Update Available", f"New version {version} available. Download and install?")
    root.destroy()
    return result

def download_and_extract(zip_url):
    print("Downloading...")
    response = requests.get(zip_url)
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        temp_dir = "_temp_extracted"
        z.extractall(temp_dir)
        top_folder = next(os.scandir(temp_dir)).path

        # Replace _internal
        source_internal = os.path.join(top_folder, "client", "_internal")
        if os.path.exists(INTERNAL_DIR):
            shutil.rmtree(INTERNAL_DIR)
        shutil.copytree(source_internal, INTERNAL_DIR)

        # Replace client.exe
        source_exe = os.path.join(top_folder, "client", "client.exe")
        target_exe = os.path.join(CLIENT_DIR, "client.exe")
        shutil.copy2(source_exe, target_exe)

        shutil.rmtree(temp_dir)
    print("Update complete.")


def main():


    if prompt_user():
        download_and_extract()
    # TODO: run main file again

if __name__ == '__main__':
    main()