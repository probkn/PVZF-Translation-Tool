import os
import json

CONFIG_FILE = "config.json"

class Settings:
    def __init__(self):
        self.default_config = {
            "mod_path": "",
            "colors": {
                "CYAN": "\033[96m",
                "GREEN": "\033[92m",
                "YELLOW": "\033[93m",
                "RED": "\033[91m",
                "BOLD": "\033[1m",
                "END": "\033[0m"
            }
        }
        self.config = self.load_config()
        self.apply_colors()

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

    def apply_colors(self):
        """Map config colors to easy-to-use variables."""
        self.CYAN = self.config["colors"]["CYAN"]
        self.GREEN = self.config["colors"]["GREEN"]
        self.YELLOW = self.config["colors"]["YELLOW"]
        self.RED = self.config["colors"]["RED"]
        self.BOLD = self.config["colors"]["BOLD"]
        self.END = self.config["colors"]["END"]

    def update_path(self, new_path):
        self.config["mod_path"] = os.path.abspath(new_path)
        self.save_config()

    def update_color(self, key, code):
        """Update specific color code (e.g., 'GREEN', '\033[94m')."""
        if key in self.config["colors"]:
            self.config["colors"][key] = code
            self.save_config()
            self.apply_colors()
            return True
        return False

    def settings_menu_ui(self):
        """Handles the entire Settings UI within settings.py."""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{self.CYAN}{self.BOLD}--- GLOBAL SETTINGS ---{self.END}")
            print(f"1. Mod Path : {self.YELLOW}{self.config['mod_path'] or 'NOT SET'}{self.END}")
            print(f"2. Edit UI Colors")
            print(f"3. Reset to Default")
            print(f"\n{self.RED}[B] Back to Main Menu{self.END}")

            choice = input(f"\n{self.YELLOW}Settings > {self.END}").strip().upper()

            if choice == '1':
                path = input("\nEnter New Mod Path: ").strip().strip('"')
                if path: self.update_path(path)
            
            elif choice == '2':
                self.color_menu_ui()
            
            elif choice == '3':
                self.config = self.default_config.copy()
                self.save_config()
                self.apply_colors()
                print(f"{self.GREEN}Settings Reset!{self.END}")
                os.system('timeout /t 1 > nul')
            
            elif choice == 'B':
                break

    def color_menu_ui(self):
        """Sub-menu to change ANSI color codes."""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{self.CYAN}{self.BOLD}--- COLOR CUSTOMIZATION ---{self.END}")
            print(f"Current Palette:")
            for key, val in self.config["colors"].items():
                if key == "END": continue
                print(f"- {key}: {val}EXAMPLE{self.END} (Code: {val.replace('\033', '\\033')})")
            
            print(f"\n{self.YELLOW}Instructions:{self.END} Enter the Key name to change its ANSI code.")
            print(f"Example: Type 'GREEN' then enter '\\033[92m'")
            print(f"{self.RED}[B] Back{self.END}")

            key_choice = input(f"\nKey to Edit > {self.END}").strip().upper()
            if key_choice == 'B': break
            
            if key_choice in self.config["colors"]:
                new_code = input(f"Enter new ANSI code for {key_choice}: ").strip()
                # Support raw string input for '\033'
                new_code = new_code.replace('\\033', '\033')
                self.update_color(key_choice, new_code)
            else:
                print(f"{self.RED}Invalid Key!{self.END}")
                os.system('timeout /t 1 > nul')

# Global instance
cfg = Settings()