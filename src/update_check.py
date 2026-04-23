import os
import requests
import subprocess
import sys
import socket

# Konfigurasi
VERSION_URL = "https://raw.githubusercontent.com/probkn/PVZF-Translation-Tool/main/latest_ver.txt"
REPO_API_URL = "https://api.github.com/repos/probkn/PVZF-Translation-Tool/contents/"
LOCAL_VERSION_FILE = "ver.txt"
# File yang tidak akan disentuh/dihapus
IGNORE_FILES = ["readme.md", "update_check.py", "Util Report", "Data", "_pycache_"]

def check_internet():
    """Memeriksa apakah perangkat terhubung ke internet"""
    try:
        # Mencoba menghubungkan ke DNS Google
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def get_remote_version():
    try:
        response = requests.get(VERSION_URL, timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except Exception:
        return None

def get_local_version():
    if os.path.exists(LOCAL_VERSION_FILE):
        with open(LOCAL_VERSION_FILE, 'r') as f:
            return f.read().strip()
    return "0"

def download_updates():
    print("[*] Downloading updates...")
    try:
        response = requests.get(REPO_API_URL, timeout=10)
        response.raise_for_status()
        files = response.json()

        for file_info in files:
            file_name = file_info['name']
            download_url = file_info['download_url']

            # Hanya proses jika itu file (bukan folder) dan tidak ada di daftar abaikan
            if file_info['type'] == 'file' and file_name.lower() not in IGNORE_FILES:
                
                # HAPUS FILE LAMA JIKA ADA
                if os.path.exists(file_name):
                    try:
                        os.remove(file_name)
                    except Exception as e:
                        print(f"[!] Could not delete old file {file_name}: {e}")

                print(f"    -> Downloading: {file_name}")
                file_res = requests.get(download_url)
                with open(file_name, 'wb') as f:
                    f.write(file_res.content)
        
        print("[✓] Update complete.")
        return True
    except Exception as e:
        print(f"[!] Error during update: {e}")
        return False

def main():
    print("[*] Checking for updates...")
    
    # 1. CEK INTERNET
    if not check_internet():
        print("[!] No internet connection. Skipping update check.")
    else:
        # 2. CEK VERSI
        remote_ver = get_remote_version()
        local_ver = get_local_version()

        if remote_ver and remote_ver > local_ver:
            print(f"\nNew Update is available (v{remote_ver})")
            print("1. Yes")
            print("2. No")
            
            choice = input("Want to update? (1/2): ").strip()
            
            if choice == '1':
                if download_updates():
                    # Update file versi lokal setelah sukses
                    with open(LOCAL_VERSION_FILE, 'w') as f:
                        f.write(remote_ver)
            else:
                print("[*] Update cancelled by user.")
        else:
            print("[✓] Your version is up to date.")

    # 3. JALANKAN APP.PY
    if os.path.exists("app.py"):
        print("\n[*] Starting app.py...")
        try:
            subprocess.run([sys.executable, "app.py"])
        except Exception as e:
            print(f"[!] Failed to run app.py: {e}")
    else:
        print("[!] app.py not found. Please check your files.")

if __name__ == "__main__":
    main()