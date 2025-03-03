import requests
import re
import os
import sys
import time
from colorama import init, Fore

# Initialize colorama (for Windows compatibility)
init(autoreset=True)

# Force ANSI support on Windows
if sys.platform == "win32":
    os.system("")

# Ensure "database" subfolder exists
db_folder = "database"
os.makedirs(db_folder, exist_ok=True)

def get_latest_local_file():
    """Get the latest .bsp file from the local database folder."""
    bsp_files = [f for f in os.listdir(db_folder) if f.endswith('.bsp')]
    return max(bsp_files) if bsp_files else None

def check_for_update():
    url = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/"
    response = requests.get(url)
    
    if response.status_code == 200:
        available_files = re.findall(r'de\d+\.bsp', response.text)
        available_files.sort()  # Sort to get the latest version at the end
        latest_file = available_files[-1] if available_files else None

        local_file = get_latest_local_file()

        if latest_file and latest_file != local_file:
            print(f"\nNewer version found: {latest_file}")
            print(f"Current local version: {local_file if local_file else 'None'}")
            download = input(color_text(f"\nWould you like to download {latest_file}? (y/n): ", "33"))
            
            if download.lower() == "y":
                download_file(url + latest_file, latest_file)
        else:
            print("\nNo newer version available. You already have the latest.")
    else:
        print("\nFailed to fetch data from NAIF server.")

def color_text(text, color_code):
    """Return colored text using colorama."""
    colors = {"31": Fore.RED, "33": Fore.YELLOW, "32": Fore.GREEN}
    return colors.get(color_code, "") + text

def download_file(file_url, file_name):
    response = requests.get(file_url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    downloaded_size = 0
    bar_length = 40  # Length of progress bar
    start_time = time.time()
    
    file_path = os.path.join(db_folder, file_name)
    
    if response.status_code == 200:
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    chunk_size = len(chunk)
                    downloaded_size += chunk_size
                    progress = (downloaded_size / total_size) if total_size else 0
                    filled_length = int(bar_length * progress)
                    
                    # Calculate download speed
                    elapsed_time = time.time() - start_time
                    speed = (downloaded_size / elapsed_time) / 1024 if elapsed_time > 0 else 0  # KB/s
                    
                    # Colorizing the progress bar
                    green_part = color_text("#" * filled_length, "32")
                    orange_part = color_text("." * (bar_length - filled_length), "33")
                    
                    bar = "[" + green_part + orange_part + "]"
                    
                    sys.stdout.write(f"\rDownloading... [{progress * 100:.0f}%] {bar} {speed:.2f} KB/s")
                    sys.stdout.flush()
        print(f"\n{file_name} downloaded successfully to {db_folder}/.")
    else:
        print("Failed to download the file.")

if __name__ == "__main__":
    check_for_update()
