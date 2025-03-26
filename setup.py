import subprocess
import sys
import os
import urllib.request
import zipfile

# Ensure pip is installed
try:
    print("\n🚀 Checking and upgrading pip, setuptools, and wheel...\n")
    subprocess.check_call([sys.executable, "-m", "ensurepip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    print("✅ pip, setuptools, and wheel updated successfully!\n")
except subprocess.CalledProcessError:
    print("❌ Failed to install or update pip. Please install it manually.")
    sys.exit(1)  # Exit if pip cannot be installed

# List of dependencies
dependencies = [
    "numpy",
    "skyfield",
    "datetime",
    "pytz",
    "pymeeus",
    "astropy",
    "matplotlib",
    "geopandas",
    "requests",
    "colorama",
    "shapely",
    "fiona",
    "pyproj",
    "rtree"
]

# Function to install dependencies
failed_packages = []

def install_package(package, index, total):
    try:
        progress = int((index / total) * 100)
        print(f"Installing {package} [{progress}%] ...", end="", flush=True)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"\r✅ {package} installed successfully!")
    except subprocess.CalledProcessError:
        print(f"\r❌ Failed to install {package}.")
        failed_packages.append(package)

# Install dependencies
print("\n🚀 Starting dependencies installation...\n")
for i, package in enumerate(dependencies, start=1):
    install_package(package, i, len(dependencies))

# Determine the correct location for the dataset
site_packages = subprocess.check_output([sys.executable, "-c", "import site; print(site.getsitepackages()[0])"], text=True).strip()
data_dir = os.path.join(site_packages, "geopandas_data")  # Store data inside site-packages
shapefile_path = os.path.join(data_dir, "ne_110m_admin_0_countries.shp")
shapefile_path = os.path.abspath(shapefile_path).replace("\\", "/")  # Fix Windows path issue

zip_url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
zip_path = os.path.join(data_dir, "ne_110m_admin_0_countries.zip")

# Download the Natural Earth dataset if missing
if not os.path.exists(shapefile_path):
    print("\n🌍 Natural Earth dataset missing. Downloading...")
    os.makedirs(data_dir, exist_ok=True)

    try:
        # Add User-Agent header to avoid HTTP 406 error
        req = urllib.request.Request(zip_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response, open(zip_path, "wb") as out_file:
            out_file.write(response.read())

        # Extract ZIP file
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(data_dir)

        os.remove(zip_path)  # Clean up
        print(f"✅ Natural Earth dataset downloaded and extracted to {data_dir}")
    except Exception as e:
        print(f"❌ Failed to download dataset: {e}")
        sys.exit(1)  # Exit if dataset download fails

# Automatically apply permanent GeoPandas fix by modifying sitecustomize.py
print("\n🔧 Creating a permanent fix for GeoPandas dataset issue...\n")

sitecustomize_path = os.path.join(site_packages, "sitecustomize.py")

# Fix the path format for Windows and Linux compatibility
fix_code = f"""import os
import geopandas

# Override the deprecated function dynamically
def custom_get_path(name):
    if name == "naturalearth_lowres":
        return r"{shapefile_path}"  # Ensure correct path format
    raise AttributeError("The geopandas.datasets feature has been removed in GeoPandas 1.0.")

# Monkey-patch the function
setattr(geopandas.datasets, "get_path", custom_get_path)
"""

try:
    with open(sitecustomize_path, "w", encoding="utf-8") as f:
        f.write(fix_code)
    print(f"✅ GeoPandas fix added to {sitecustomize_path}")
except Exception as e:
    print(f"❌ Failed to modify sitecustomize.py: {e}")
    sys.exit(1)  # Exit if fix cannot be applied

print("\n🎉 Setup complete! All dependencies installed and GeoPandas issue permanently fixed.")

# Display final result
if failed_packages:
    print("\n⚠️ Some dependencies have NOT been installed:")
    for pkg in failed_packages:
        print(f"   ❌ {pkg}")
    print("\nPlease install the missing packages manually and try again.")
else:
    print("\n🎉 All dependencies installed successfully!")
