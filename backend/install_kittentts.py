"""
Script to manually install kittentts wheel bypassing version checks
"""
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
import os
import shutil

def install_kittentts():
    """Download and install kittentts manually"""
    url = "https://github.com/KittenML/KittenTTS/releases/download/0.8/kittentts-0.8.0-py3-none-any.whl"
    
    print("Downloading kittentts wheel...")
    
    # Create temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        wheel_path = os.path.join(tmpdir, "kittentts.whl")
        
        # Download wheel
        urllib.request.urlretrieve(url, wheel_path)
        print(f"Downloaded to {wheel_path}")
        
        # Extract wheel
        extract_dir = os.path.join(tmpdir, "extracted")
        with zipfile.ZipFile(wheel_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        print(f"Extracted wheel contents")
        
        # Find the kittentts package directory
        dist_info = None
        for item in os.listdir(extract_dir):
            if item.endswith('.dist-info'):
                dist_info = item
            print(f"  - {item}")
        
        # Install using pip with --no-deps to avoid version checks
        print("\nInstalling with pip...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", wheel_path, "--no-deps", "--force-reinstall"],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
        
        if result.returncode == 0:
            print("\n✓ kittentts installed successfully!")
        else:
            print("\n✗ Installation failed")
            return False
    
    return True

if __name__ == "__main__":
    install_kittentts()
