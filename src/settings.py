import os
import json
import urllib.request
import re
import subprocess
from packaging.version import Version

CONFIG_FILE = "config.json"

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

        # Config default hanya untuk path
        self.default_config = {
            "mod_path": ""
        }
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                return self.default_config
        return self.default_config

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
        """Downloads the new .pyz and triggers a restart."""
        try:
            print(f"   Downloading {filename}...")
            urllib.request.urlretrieve(url, filename)
            print(f"   {self.GREEN}[✓] Download Complete!{self.END}")
            print("   Starting new version...")
            
            subprocess.Popen(["python", filename])  # tanpa shell=True
            os._exit(0) 
        except Exception as e:
            print(f"   {self.RED}[!] Download failed: {e}{self.END}")
            input()

    # --- UI MENU ---

    def settings_menu_ui(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"\n   {self.CYAN}{self.BOLD}--- GLOBAL SETTINGS ---{self.END}")
            print(f"   {self.CYAN}1.{self.END} Mod Path : {self.YELLOW}{self.config['mod_path'] or 'NOT SET'}{self.END}")
            print(f"   {self.CYAN}2.{self.END} Check for Updates")
            print(f"   {self.CYAN}3.{self.END} Reset to Default")
            print(f"\n   {self.RED}[B]{self.END} Back to Main Menu")

            choice = input(f"\n   {self.YELLOW}Settings Choice > {self.END}").strip().upper()

            if choice == '1':
                path = input("\n   Enter New Mod Path: ").strip().strip('"')
                if path: self.update_path(path)
            elif choice == '2':
                self.check_for_updates()
            elif choice == '3':
                self.config = self.default_config.copy()
                self.save_config()
                print(f"   {self.GREEN}Settings Reset!{self.END}")
                os.system('timeout /t 1 > nul')
            elif choice == 'B':
                break

cfg = Settings()
