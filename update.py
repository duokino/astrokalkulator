import requests
import os
import hashlib
import re
import sys
import time
from colorama import init, Fore

# Initialize colorama (for Windows compatibility)
init(autoreset=True)

# Ensure "database" subfolder exists
db_folder = "database"
os.makedirs(db_folder, exist_ok=True)

def get_github_file_hash(url):
    response = requests.get(url)
    if response.status_code == 200:
        return hashlib.sha256(response.content).hexdigest()
    return None

def get_local_file_hash(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            return hashlib.sha256(file.read()).hexdigest()
    return None

def color_text(text, color_code):
    """Return colored text using colorama."""
    colors = {"31": Fore.RED, "33": Fore.YELLOW, "32": Fore.GREEN}
    return colors.get(color_code, "") + text

def download_file(url, file_path):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    downloaded_size = 0
    bar_length = 40  # Length of progress bar
    start_time = time.time()
    
    if response.status_code == 200:
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    chunk_size = len(chunk)
                    downloaded_size += chunk_size
                    if total_size > 0:
                        progress = min(downloaded_size / total_size, 1)  # Ensure progress is max 100%
                        filled_length = int(bar_length * progress)
                    else:
                        progress = 0  # Avoid division errors
                        filled_length = 0
                    
                    # Calculate download speed
                    elapsed_time = time.time() - start_time
                    speed = (downloaded_size / elapsed_time) / 1024 if elapsed_time > 0 else 0  # KB/s
                    
                    # Colorizing the progress bar
                    green_part = color_text("#" * filled_length, "32")
                    orange_part = color_text("." * (bar_length - filled_length), "33")
                    
                    bar = "[" + green_part + orange_part + "]"
                    
                    sys.stdout.write(f"\rDownloading... [{progress * 100:.0f}%] {bar} {speed:.2f} KB/s")
                    sys.stdout.flush()
        print(f"\n{file_path} downloaded successfully.")
    else:
        print("Failed to download the file.")

def update_location_file():
    github_raw_url = "https://raw.githubusercontent.com/duokino/astrokalkulator/main/database/location.txt"
    local_file_path = "database/location.txt"
    
    github_file_hash = get_github_file_hash(github_raw_url)
    local_file_hash = get_local_file_hash(local_file_path)
    
    if github_file_hash and github_file_hash != local_file_hash:
        user_input = input(Fore.YELLOW + "A newer version of location.txt is available. Do you want to update? (yes/no): " + Fore.RESET)
        if user_input.lower() in ['yes', 'y']:
            print("Downloading location.txt with progress...")
            download_file(github_raw_url, local_file_path)
        else:
            print("Update skipped.")
    else:
        print("Local file is up to date.")

def get_latest_local_file():
    """Get the latest .bsp file from the local database folder."""
    bsp_files = [f for f in os.listdir(db_folder) if f.endswith('.bsp')]
    return max(bsp_files) if bsp_files else None

def check_for_bsp_update():
    url = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/"
    response = requests.get(url)
    
    if response.status_code == 200:
        available_files = re.findall(r'de\d+\.bsp', response.text)
        available_files.sort()
        latest_file = available_files[-1] if available_files else None
        local_file = get_latest_local_file()
        
        if latest_file and latest_file != local_file:
            print(f"\nNewer BSP version found: {latest_file}")
            print(f"Current local version: {local_file if local_file else 'None'}")
            user_input = input(Fore.YELLOW + f"\nWould you like to download {latest_file}? (yes/no): " + Fore.RESET)
            print("")
            
            if user_input.lower() in ['yes', 'y']:
                download_file(url + latest_file, os.path.join(db_folder, latest_file))
        else:
            print("\nNo newer BSP version available. You already have the latest.")
    else:
        print("\nFailed to fetch data from NAIF server.")

def main():
    update_location_file()
    check_for_bsp_update()

if __name__ == "__main__":
    main()
