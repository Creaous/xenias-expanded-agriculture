import toml
import requests
import hashlib
import glob
import os
import time
import sys # For flushing stdout
from typing import Dict, Any
from tqdm import tqdm

# --- ANSI Color Codes for better "UI" ---
# Use these constants to wrap strings for colored output in the terminal
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_RED = '\033[91m'
C_BLUE = '\033[94m'
C_END = '\033[0m'
# ------------------------------------------

# --- RATE LIMIT CONFIGURATION ---
# The delay in seconds to wait between each file download request.
DOWNLOAD_DELAY_SECONDS = 1 
# --------------------------------

# Define the directory to save the downloaded files
DOWNLOAD_DIR = "downloads"
# Note: INDEX_DIR is used to find TOML files relative to the script
INDEX_DIR = ".." 

def calculate_sha512(filepath: str) -> str:
    """Calculate the SHA-512 hash of a file."""
    sha512 = hashlib.sha512()
    # Use tqdm to show a progress bar for the hash calculation
    # file_size is needed for the total value of the progress bar
    file_size = os.path.getsize(filepath)
    
    with open(filepath, 'rb') as f:
        with tqdm(total=file_size, unit='B', unit_scale=True, 
                  desc=f"{C_BLUE}Verifying{C_END}", ncols=70, leave=False) as pbar:
            while True:
                data = f.read(65536)  # 64KB chunks
                if not data:
                    break
                sha512.update(data)
                pbar.update(len(data))
    return sha512.hexdigest()

def process_toml_file(filepath: str):
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
        expected_hash = download_info['hash'].lower() # Normalize hash immediately
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
    
    # 4. Download the file
    print(f"Attempting to download {C_YELLOW}{filename}{C_END} from: {url}")
    try:
        # Use a stream to download the file
        with requests.get(url, stream=True) as r:
            r.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            
            total_size = int(r.headers.get('content-length', 0))
            
            # Initialize tqdm progress bar for download
            with open(local_filepath, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, 
                          desc=f"{C_BLUE}Downloading{C_END}", ncols=70) as pbar:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk: # filter out keep-alive new chunks
                            f.write(chunk)
                            pbar.update(len(chunk))
                            
        print(f"{C_GREEN}SUCCESS:{C_END} Downloaded to {local_filepath}")

    except requests.exceptions.RequestException as e:
        print(f"{C_RED}ERROR:{C_END} Failed to download {filename}: {e}")
        # Clean up partial download
        if os.path.exists(local_filepath):
            os.remove(local_filepath)
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
            # Optional: Remove the corrupted file
            # os.remove(local_filepath) 
            # print(f"{C_YELLOW}Action:{C_END} Removed corrupted file: {local_filepath}")
            
    except Exception as e:
        print(f"{C_RED}ERROR:{C_END} Failed to calculate hash for {local_filepath}: {e}")


if __name__ == "__main__":
    
    print(f"{C_GREEN}*** Modrinth/CurseForge TOML Downloader v1.2 ***{C_END}")
    
    # Find all .toml files in the specified directory
    toml_files = glob.glob(os.path.join(INDEX_DIR, "*.toml"))
    
    if not toml_files:
        print(f"{C_YELLOW}WARNING:{C_END} No {C_YELLOW}.toml{C_END} files found in '{INDEX_DIR}/'.")
    else:
        print(f"Found {len(toml_files)} TOML files to process.")
        
        for i, file in enumerate(toml_files):
            process_toml_file(file)
            
            # --- Rate Limiting Implementation ---
            if DOWNLOAD_DELAY_SECONDS > 0 and i < len(toml_files) - 1:
                print(f"{C_YELLOW}--- Pausing for {DOWNLOAD_DELAY_SECONDS} second(s) to respect rate limits... ---{C_END}")
                time.sleep(DOWNLOAD_DELAY_SECONDS)
                
        print(f"\n{C_GREEN}*** All {len(toml_files)} TOML files processed. Exiting. ***{C_END}")
        
    sys.exit(0)