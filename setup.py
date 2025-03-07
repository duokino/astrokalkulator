import subprocess
import sys
from tqdm import tqdm

# List of dependencies from the setup.py
dependencies = [
    "numpy",
    "skyfield==1.45",
    "datetime",
    "pytz",
    "pymeeus",
    "astropy",
    "matplotlib"
]

# Function to install a single package with progress bar
def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError:
        print(f"\n❌ Failed to install {package}. Please check for errors.")

# Install dependencies with progress bar
print("\n📦 Starting dependencies installation...\n")
for package in tqdm(dependencies, desc="Installing", unit="pkg", position=0, leave=True, ncols=100, bar_format="{l_bar}{bar:50}{r_bar}{bar:-10b}"):
    install_package(package)

print("\n✅ All dependencies installed successfully!")
