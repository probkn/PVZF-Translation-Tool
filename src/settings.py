import os
import json
import urllib.request
import re
import subprocess
import hashlib
import sys
try:
    from packaging.version import Version
except ImportError:
    # Fallback sederhana kalau packaging tidak tersedia
    class Version:
        def __init__(self, v):
            self.parts = [int(x) for x in v.split('.')]
        def __gt__(self, other):
            return self.parts > other.parts
        def __eq__(self, other):
            return self.parts == other.parts
        def __str__(self):
            return '.'.join(map(str, self.parts))

if os.name == 'nt':
    base_dir = os.path.join(os.getenv('APPDATA'), "PVZF-Translation-Tool")
else:
    base_dir = os.path.join(os.path.expanduser("~"), ".config", "pvzf-translation-tool")

os.makedirs(base_dir, exist_ok=True)
CONFIG_FILE = os.path.join(base_dir, "config.json")

class Settings:
    def __init__(self):
        # Versi lokal
        self.version = "1.0.1"
        self.repo_url = "https://github.com/probkn/PVZF-Translation-Tool/tree/main"
        self.raw_repo_api = "https://api.github.com/repos/probkn/PVZF-Translation-Tool/contents/"

        # Warna hardcoded (tidak bisa diubah user)
        self.CYAN = "\033[96m"
        self.GREEN = "\033[92m"
        self.YELLOW = "\033[93m"
        self.RED = "\033[91m"
        self.BOLD = "\033[1m"
        self.END = "\033[0m"

        self.default_config = {
            "mod_path": "",
            "repo_path": "",
            "blacklist": []
        }
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"   {self.YELLOW}[i] Config corrupted, regenerating default...{self.END}")
                # Pastikan self.config sudah ada sebelum dipakai
                self.config = self.default_config.copy()
                self.save_config()
                return self.config
        else:
            print(f"   {self.YELLOW}[i] Config not found, creating new one...{self.END}")
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            self.config = self.default_config.copy()
            self.save_config()
            return self.config

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)

    def update_path(self, new_path):
        self.config["mod_path"] = os.path.abspath(new_path)
        self.save_config()

    # --- UPDATE SYSTEM ---

    def check_for_updates(self):
        """Checks GitHub for a newer .pyz version."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n   {self.CYAN}{self.BOLD}--- CHECKING FOR UPDATES ---{self.END}")
        print(f"   Current Version: {self.YELLOW}{self.version}{self.END}")
        print("   Connecting to GitHub...")

        try:
            req = urllib.request.Request(self.raw_repo_api, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                files = json.loads(response.read().decode())
                
                download_url = ""
                file_name = ""
                latest_version = Version("0.0.0")

                for f in files:
                    if f['name'].endswith('.pyz'):
                        v_match = re.search(r'(\d+\.\d+\.\d+)', f['name'])
                        if v_match:
                            ver = Version(v_match.group(1))
                            if ver > latest_version:
                                latest_version = ver
                                download_url = f['download_url']
                                file_name = f['name']

                if latest_version > Version(self.version):
                    print(f"\n   {self.GREEN}[!] NEW VERSION FOUND: {latest_version}{self.END}")
                    choice = input("   Download and Update? (Y/N): ").strip().upper()
                    if choice == 'Y':
                        self.download_update(download_url, file_name)
                else:
                    print(f"\n   {self.GREEN}[✓] You are up to date!{self.END}")
                    input("   Press Enter to return...")

        except Exception as e:
            print(f"\n   {self.RED}[!] Failed to check updates: {e}{self.END}")
            input("   Press Enter...")

    def download_update(self, url, filename):
        """Downloads the new .pyz, verifies SHA-256, and triggers a restart."""
        try:
            print(f"   Downloading {filename}...")
            urllib.request.urlretrieve(url, filename)
            print(f"   {self.GREEN}[✓] Download Complete!{self.END}")

            hash_url = "https://raw.githubusercontent.com/probkn/PVZF-Translation-Tool/main/SHA256SUMS.json"
            with urllib.request.urlopen(hash_url) as h:
                hashes = json.loads(h.read().decode())
            print(f"   [DEBUG] filename = {filename}")
            print(f"   [DEBUG] available hashes = {list(hashes.keys())}")

            expected_hash = hashes.get(filename) or hashes.get(filename.replace('.pyz', ''))
            if not expected_hash:
                print(f"   {self.RED}[!] No hash found for {filename}{self.END}")
                input("   Press Enter to abort...")
                return

            sha256 = hashlib.sha256()
            with open(filename, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            file_hash = sha256.hexdigest()

            if file_hash != expected_hash:
                print(f"   {self.RED}[!] SHA mismatch!{self.END}")
                print(f"   Expected: {expected_hash}")
                print(f"   Got     : {file_hash}")
                input("   Press Enter to abort...")
                return

            print(f"   {self.GREEN}[✓] Verified SHA-256 integrity!{self.END}")
            print("   Starting new version...")

            subprocess.Popen([sys.executable, filename])  # gunakan interpreter aktif
            sys.exit(0)

        except Exception as e:
            print(f"   {self.RED}[!] Download failed: {e}{self.END}")
            input()

    # --- UI MENU ---

    def settings_menu_ui(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"\n   {self.CYAN}{self.BOLD}--- GLOBAL SETTINGS ---{self.END}")
            print(f"   {self.CYAN}1.{self.END} Mod Path : {self.YELLOW}{self.config['mod_path'] or 'NOT SET'}{self.END}")
            print(f"   {self.CYAN}2.{self.END} Repo Path : {self.YELLOW}{self.config['repo_path'] or 'NOT SET'}{self.END}")
            print(f"   {self.CYAN}3.{self.END} Check for Updates")
            print(f"   {self.CYAN}4.{self.END} Reset to Default")
            print(f"\n   {self.RED}[B]{self.END} Back to Main Menu")

            choice = input(f"\n   {self.YELLOW}Settings Choice > {self.END}").strip().upper()

            if choice == '1':
                path = input("\n   Enter New Mod Path: ").strip().strip('"')
                if path:
                    self.update_path(path)
            elif choice == '2':
                repo = input("\n   Enter New Repo Path: ").strip().strip('"')
                if repo:
                    self.config["repo_path"] = os.path.abspath(repo)
                    self.save_config()
                    print(f"   {self.GREEN}Repo Path Updated!{self.END}")
                    os.system('timeout /t 1 > nul')
            elif choice == '3':
                self.check_for_updates()
            elif choice == '4':
                self.config = self.default_config.copy()
                self.save_config()
                print(f"   {self.GREEN}Settings Reset!{self.END}")
                os.system('timeout /t 1 > nul')
            elif choice == 'B':
                break

cfg = Settings()
