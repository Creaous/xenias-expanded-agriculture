import toml
import requests
import hashlib
import glob
import os
import time
import sys
from typing import Dict, Any, List
from tqdm import tqdm

# --- ANSI Color Codes for better "UI" ---
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_RED = '\033[91m'
C_BLUE = '\033[94m'
C_END = '\033[0m'
# ------------------------------------------

# --- CONFIGURATION ---
DOWNLOAD_DELAY_SECONDS = 1 
DELETE_CORRUPTED_FILES = True # RECOMMENDED FOR SECURITY AND INTEGRITY PURPOSES!!
DOWNLOAD_DIR = "downloads"
INDEX_DIR = ".." 
# ---------------------

def calculate_sha512(filepath: str) -> str:
    """Calculate the SHA-512 hash of a file."""
    sha512 = hashlib.sha512()
    
    try:
        file_size = os.path.getsize(filepath)
    except OSError:
        # Handle case where file might not exist (e.g., if deleted)
        return "" 
    
    with open(filepath, 'rb') as f:
        with tqdm(total=file_size, unit='B', unit_scale=True, 
                  desc=f"{C_BLUE}Verifying{C_END}", ncols=70, leave=False) as pbar:
            while True:
                data = f.read(65536)
                if not data:
                    break
                sha512.update(data)
                pbar.update(len(data))
    return sha512.hexdigest()

# Added failed_mods_list parameter to log failures
def process_toml_file(filepath: str, failed_mods_list: List[str]):
    """Read a TOML file, download the mod, and verify its hash."""
    
    # 1. Start Processing with a clear, colored header
    print(f"\n{C_BLUE}==================================================")
    print(f"| Processing: {os.path.basename(filepath)} |")
    print(f"=================================================={C_END}")
    
    try:
        # 2. Read the TOML file
        with open(filepath, 'r') as f:
            data: Dict[str, Any] = toml.load(f)
            
    except toml.TomlDecodeError as e:
        print(f"{C_RED}ERROR:{C_END} Failed to decode TOML file {filepath}: {e}")
        return
    except FileNotFoundError:
        print(f"{C_RED}ERROR:{C_END} File not found at {filepath}")
        return
        
    # Extract necessary information with checks
    try:
        filename = data['filename']
        download_info = data['download']
        url = download_info['url']
        expected_hash = download_info['hash'].lower()
        hash_format = download_info['hash-format'].lower()
        
    except KeyError as e:
        print(f"{C_RED}ERROR:{C_END} Missing required key in {filepath}: {e}")
        return

    # Check for supported hash format
    if hash_format != 'sha512':
        print(f"{C_YELLOW}WARNING:{C_END} Skipping download for {filename}. Only '{C_GREEN}sha512{C_END}' is supported, found '{hash_format}'.")
        return

    # 3. Prepare download path
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
        
    local_filepath = os.path.join(DOWNLOAD_DIR, filename)
    
    # Check if file exists and hash matches before downloading (Optimization)
    if os.path.exists(local_filepath):
        print(f"{C_YELLOW}INFO:{C_END} File {filename} already exists. Checking hash...")
        try:
            actual_hash_existing = calculate_sha512(local_filepath)
            if actual_hash_existing == expected_hash:
                print(f"{C_GREEN}VERIFICATION SUCCESS:{C_END} Existing file hash matches. Skipping download.")
                return
            else:
                print(f"{C_YELLOW}WARNING:{C_END} Existing file hash mismatch. Redownloading...")
                os.remove(local_filepath)
        except Exception as e:
            print(f"{C_RED}ERROR:{C_END} Could not verify existing file: {e}. Attempting redownload.")
            if os.path.exists(local_filepath):
                os.remove(local_filepath)
    
    # 4. Download the file
    print(f"Attempting to download {C_YELLOW}{filename}{C_END} from: {url}")
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            
            with open(local_filepath, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, 
                          desc=f"{C_BLUE}Downloading{C_END}", ncols=70) as pbar:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
                            
        print(f"{C_GREEN}SUCCESS:{C_END} Downloaded to {local_filepath}")

    except requests.exceptions.RequestException as e:
        print(f"{C_RED}ERROR:{C_END} Failed to download {filename}: {e}")
        if os.path.exists(local_filepath):
            os.remove(local_filepath)
        # Log the failure before returning
        failed_mods_list.append(f"{filename} (Download Error)")
        return

    # 5. Verify the hash
    print("Starting hash verification...")
    try:
        actual_hash = calculate_sha512(local_filepath)
        
        if actual_hash == expected_hash:
            print(f"{C_GREEN}VERIFICATION SUCCESS:{C_END} The downloaded file's hash matches.")
        else:
            print(f"{C_RED}VERIFICATION FAILED:{C_END} File integrity check failed!")
            print(f"  Expected Hash: {expected_hash}")
            print(f"  Actual Hash:   {actual_hash}")
            
            # Log the failure
            failed_mods_list.append(f"{filename} (Hash Mismatch)")
            
            if DELETE_CORRUPTED_FILES == True:
                os.remove(local_filepath) 
                print(f"{C_YELLOW}Action:{C_END} Removed corrupted file: {local_filepath}")
            
    except Exception as e:
        print(f"{C_RED}ERROR:{C_END} Failed to calculate hash for {local_filepath}: {e}")
        failed_mods_list.append(f"{filename} (Hash Calculation Error)")
        
        
if __name__ == "__main__":
    
    # --- List to store failed mods ---
    FAILED_MODS: List[str] = []
    
    print(f"{C_GREEN}*** Modrinth/CurseForge TOML Downloader v1.3 ***{C_END}")
    
    toml_files = glob.glob(os.path.join(INDEX_DIR, "*.toml"))
    
    if not toml_files:
        print(f"{C_YELLOW}WARNING:{C_END} No {C_YELLOW}.toml{C_END} files found in '{INDEX_DIR}/'.")
    else:
        print(f"Found {len(toml_files)} TOML files to process.")
        
        for i, file in enumerate(toml_files):
            # Pass the list to the processing function
            process_toml_file(file, FAILED_MODS)
            
            # --- Rate Limiting Implementation ---
            if DOWNLOAD_DELAY_SECONDS > 0 and i < len(toml_files) - 1:
                print(f"{C_YELLOW}--- Pausing for {DOWNLOAD_DELAY_SECONDS} second(s) to respect rate limits... ---{C_END}")
                time.sleep(DOWNLOAD_DELAY_SECONDS)
                
        print(f"\n{C_GREEN}*** All {len(toml_files)} TOML files processed. ***{C_END}")

        # --- Summary of Failures ---
        if FAILED_MODS:
            print(f"\n{C_RED}*** SUMMARY OF FAILED CHECKS ({len(FAILED_MODS)} MODS) ***{C_END}")
            for failure in FAILED_MODS:
                print(f"{C_RED}- {failure}{C_END}")
            print(f"\n{C_YELLOW}Please review the errors above and check the corresponding .toml files or download URLs.{C_END}")
        else:
            print(f"\n{C_GREEN}*** ALL MODS PASSED HASH VERIFICATION CHECKS! ***{C_END}")
        
    sys.exit(0)
