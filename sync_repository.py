"""
GitHub Repository Sync Script for Office PC
Downloads updated files from pic-wlt GitHub repository
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import time
from datetime import datetime

# ============ CONFIGURATION ============
GITHUB_USERNAME = "your-username"  # Replace with your GitHub username
REPO_NAME = "pic-wlt"
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/main/"
LOCAL_BASE_PATH = "C:/work/pic-wlt"  # Change to your local project path
CHROMEDRIVER_PATH = "C:/tools/chromedriver.exe"  # Change to your chromedriver location

# Files to sync (add more as needed)
FILES_TO_SYNC = [
    # Controllers
    "src/controllers/__init__.py",
    "src/controllers/base_instrument.py",
    "src/controllers/vna.py",
    "src/controllers/motion_controller.py",
    "src/controllers/camera_vision.py",
    "src/controllers/lca.py",
    "src/controllers/smu.py",
    
    # Core modules
    "src/core/__init__.py",
    "src/core/device_manager.py",
    "src/core/data_logger.py",
    "src/core/error_handler.py",
    
    # Protocols
    "src/protocols/__init__.py",
    "src/protocols/alignment.py",
    "src/protocols/measurement.py",
    "src/protocols/calibration.py",
    
    # Utils
    "src/utils/__init__.py",
    "src/utils/file_io.py",
    "src/utils/validators.py",
    
    # Config files
    "config/equipment_config.yaml",
    "config/test_parameters.yaml",
    
    # Documentation
    "README.md",
    "CLAUDE.md",
    "requirements.txt",
]

# ============ FUNCTIONS ============

def setup_driver():
    """Initialize Chrome WebDriver with headless option"""
    chrome_options = Options()
    # Uncomment next line to run without opening browser window
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def download_file(driver, github_path, local_path):
    """Download a single file from GitHub"""
    url = BASE_URL + github_path
    
    try:
        driver.get(url)
        time.sleep(1)  # Wait for page to load
        
        # Try to get content from <pre> tag (raw content)
        try:
            content = driver.find_element("tag name", "pre").text
        except:
            # Fallback to body if no <pre> tag
            content = driver.find_element("tag name", "body").text
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Write content to file
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, f"✓ {github_path}"
    
    except Exception as e:
        return False, f"✗ {github_path} - Error: {str(e)}"

def sync_repository():
    """Main function to sync all files"""
    print("=" * 60)
    print("GitHub Repository Sync - pic-wlt")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    driver = setup_driver()
    
    success_count = 0
    fail_count = 0
    results = []
    
    try:
        for github_path in FILES_TO_SYNC:
            local_path = os.path.join(LOCAL_BASE_PATH, github_path)
            success, message = download_file(driver, github_path, local_path)
            
            results.append(message)
            print(message)
            
            if success:
                success_count += 1
            else:
                fail_count += 1
    
    finally:
        driver.quit()
    
    # Summary
    print()
    print("=" * 60)
    print("SYNC SUMMARY")
    print("=" * 60)
    print(f"Total files: {len(FILES_TO_SYNC)}")
    print(f"✓ Success: {success_count}")
    print(f"✗ Failed: {fail_count}")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Save log
    log_path = os.path.join(LOCAL_BASE_PATH, "logs", "sync_log.txt")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Sync at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Success: {success_count}, Failed: {fail_count}\n")
        f.write('\n'.join(results))
        f.write(f"\n{'='*60}\n")

def sync_specific_files(file_list):
    """Sync only specific files (useful for quick updates)"""
    print(f"Syncing {len(file_list)} specific files...")
    
    driver = setup_driver()
    
    try:
        for github_path in file_list:
            local_path = os.path.join(LOCAL_BASE_PATH, github_path)
            success, message = download_file(driver, github_path, local_path)
            print(message)
    finally:
        driver.quit()

# ============ MAIN ============

if __name__ == "__main__":
    # Option 1: Sync all files
    sync_repository()
    
    # Option 2: Sync specific files only (uncomment to use)
    # sync_specific_files([
    #     "src/controllers/vna.py",
    #     "src/controllers/motion_controller.py",
    # ])