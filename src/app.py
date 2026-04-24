import os
import sys
import json
import subprocess
import requests
from settings import cfg
import re
from packaging.version import Version

# --- PATH & MODULE SETUP ---
if getattr(sys, 'frozen', False) or sys.argv[0].endswith('.pyz'):
    current_path = os.path.dirname(os.path.abspath(sys.argv[0]))
else:
    current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_path)

# Import Internal Modules
try:
    import almanac_comp as comp
    import almanac_check as checker
    import string_comp
    import regex_comp
    import auto_github
    import string_check
    import travelbuffs_comp
except ImportError as e:
    INTERNAL_ERROR = str(e)
else:
    INTERNAL_ERROR = None

__version__ = "1.0.1"

# --- UTILITIES ---

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def is_path_valid():
    p = cfg.config["mod_path"]
    return os.path.exists(os.path.join(p, 'Localization')) and os.path.exists(os.path.join(p, 'Dumps'))

def run_build():
    """Triggers build.bat, restarts the app, and closes current process."""
    if os.path.exists("build.bat"):
        print(f"   {cfg.YELLOW}[i] Triggering Auto-Build & Restart...{cfg.END}")
        subprocess.Popen([os.path.join(current_path, "build.bat")])
        sys.exit()
    else:
        print(f"   {cfg.RED}[!] build.bat not found!{cfg.END}")
        input("   Press Enter...")

def check_latest_release():
    try:
        api_url = "https://api.github.com/repos/probkn/PVZF-Translation-Tool/contents/"
        req = requests.get(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        files = req.json()

        latest_version = Version("0.0.0")
        file_name = None
        for f in files:
            if f['name'].endswith('.pyz'):
                v_match = re.search(r'(\d+\.\d+\.\d+)', f['name'])
                if v_match:
                    ver = Version(v_match.group(1))
                    if ver > latest_version:
                        latest_version = ver
                        file_name = f['name']

        # Ambil changelog singkat
        changelog_url = "https://raw.githubusercontent.com/probkn/PVZF-Translation-Tool/main/simple-changelog.txt"
        cl_resp = requests.get(changelog_url, headers={'User-Agent': 'Mozilla/5.0'})
        changelog = cl_resp.text.strip().splitlines()[0] if cl_resp.ok else "No changelog available."

        return latest_version, changelog
    except Exception:
        return None, None

def select_lang(loc_path):
    """Helper to select language folder."""
    try:
        folders = [f for f in os.listdir(loc_path) if os.path.isdir(os.path.join(loc_path, f))]
        if not folders: return None
        print(f"\n   {cfg.CYAN}--- Available Languages ---{cfg.END}")
        for i, f in enumerate(folders, 1): print(f"   [{i}]. {f}")
        idx = int(input(f"\n   Select number: ")) - 1
        return folders[idx] if 0 <= idx < len(folders) else None
    except: return None

# --- SUB-MENUS ---

def translator_tool_menu():
    """Menu 2: Checker & Auto Translate Features."""
    if not is_path_valid():
        print(f"   {cfg.RED}[!] Path invalid. Set it in Settings first!{cfg.END}")
        input("   Press Enter..."); return

    loc_base = os.path.join(cfg.config["mod_path"], 'Localization')
    dump_base = os.path.join(cfg.config["mod_path"], 'Dumps')

    while True:
        clear_screen()
        print(f"\n   {cfg.GREEN}{cfg.BOLD}--- CHECKER & AUTO TRANSLATE TOOL ---{cfg.END}")
        print(f"   {cfg.CYAN}[1]{cfg.END} Almanac Comparison (Auto Add Missing)")
        print(f"   {cfg.CYAN}[2]{cfg.END} Almanac Validator (Symbol Check)")
        print(f"   {cfg.CYAN}[3]{cfg.END} Travel Buffs Comparison")
        print(f"   {cfg.CYAN}[4]{cfg.END} String Checker (Scan All)")
        print(f"\n   {cfg.RED}[B] Back to Main Menu{cfg.END}")

        choice = input(f"\n   {cfg.YELLOW}Tool Choice > {cfg.END}").strip().upper()
        if choice == 'B': break
        
        clear_screen()
        if choice == '1':
            try:
                with open(os.path.join(dump_base, 'LawnStrings.json'), 'r', encoding='utf-8') as f: dl = json.load(f)
                with open(os.path.join(dump_base, 'ZombieStrings.json'), 'r', encoding='utf-8') as f: dz = json.load(f)
                lang = select_lang(loc_base)
                if not lang: continue
                
                tlp = os.path.join(loc_base, lang, 'Almanac', 'LawnStringsTranslate.json')
                tzp = os.path.join(loc_base, lang, 'Almanac', 'ZombieStringsTranslate.json')
                
                with open(tlp, 'r', encoding='utf-8') as f: il = json.load(f)
                with open(tzp, 'r', encoding='utf-8') as f: iz = json.load(f)

                mp = comp.find_missing_entries(il.get('plants', []), dl.get('plants', []), 'seedType')
                mz = comp.find_missing_entries(iz.get('zombies', []), dz.get('zombies', []), 'theZombieType')

                print(f"\n   {cfg.YELLOW}Missing: {len(mp)} Plants, {len(mz)} Zombies.{cfg.END}")
                print("   [1] Auto Translate | [2] Apply Changes | [3] Cancel")
                sub = input("   Action > ")
                if sub == '1':
                    mp, mz = comp.translate_batch(mp), comp.translate_batch(mz)
                if sub in ['1', '2'] and (mp or mz):
                    il['plants'].extend(mp); iz['zombies'].extend(mz)
                    with open(tlp, 'w', encoding='utf-8') as f: json.dump(il, f, indent=4, ensure_ascii=False)
                    with open(tzp, 'w', encoding='utf-8') as f: json.dump(iz, f, indent=4, ensure_ascii=False)
                    print(f"   {cfg.GREEN}[✓] Updated!{cfg.END}")
                input("\n   Press Enter...")
            except Exception as e: print(f"   Error: {e}"); input("   Press Enter...")
        
        elif choice == '2':
            lang = select_lang(loc_base)
            if lang:
                for fn in ['LawnStringsTranslate.json', 'ZombieStringsTranslate.json']:
                    p = os.path.join(loc_base, lang, 'Almanac', fn)
                    if os.path.exists(p): checker.validator_menu(p)
            input("\n   Press Enter...")

        elif choice == '3':
            travelbuffs_comp.travelbuffs_menu(loc_base, dump_base)
            input("\n   Press Enter...")

        elif choice == '4':
            string_check.string_checker_menu(loc_base)
            input("\n   Press Enter...")

# --- MAIN ENGINE ---

def main():
    secret_unlocked = False
    
    # Auto-detect default path if empty
    if not cfg.config["mod_path"]:
        default_p = os.path.abspath(os.path.join(current_path, "..", "Mods", "PvZ_Fusion_Translator"))
        cfg.update_path(default_p)

    latest_version, changelog = check_latest_release()

    while True:
        clear_screen()
        print(f"\n   {cfg.GREEN}{cfg.BOLD}PvZ Fusion Translation Tool v{__version__}{cfg.END}")
        
        if INTERNAL_ERROR:
            print(f"   {cfg.RED}[!] MODULE ERROR: {INTERNAL_ERROR}{cfg.END}")
        
        if not is_path_valid():
            print(f"   {cfg.RED}{cfg.BOLD}[!] WARNING: MOD FOLDER NOT FOUND!{cfg.END}")
            print(f"   {cfg.YELLOW}Check Settings to set the correct path.{cfg.END}\n")
        if latest_version and latest_version > Version(__version__):
            print(f"\n   {cfg.YELLOW}New version {latest_version} is available!{cfg.END}")
            print(f"   {cfg.CYAN}Changelog:{cfg.END} {changelog}\n")
        
        print(f"   {cfg.CYAN}[1]{cfg.END} Compare Tool (String/Regex)")
        print(f"   {cfg.CYAN}[2]{cfg.END} Checker & Auto Translate")
        print(f"   {cfg.CYAN}[3]{cfg.END} Settings")
        print(f"   {cfg.CYAN}[4]{cfg.END} Sync to GitHub Desktop")
        print(f"   {cfg.CYAN}[5]{cfg.END} Update {__version__} Changelog")
        
        if secret_unlocked:
            print(f"   {cfg.YELLOW}[8]{cfg.END} Update & Restart (Build)")
            
        print(f"   {cfg.RED}[6]{cfg.END} Exit")

        choice = input(f"\n   {cfg.YELLOW}Main Choice > {cfg.END}").strip()

        if choice == '970854':
            secret_unlocked = True
            print(f"   {cfg.GREEN}Developer Build Menu Unlocked!{cfg.END}")
            os.system('timeout /t 1 > nul')
            continue

        if choice == '1':
            if is_path_valid():
                while True:
                    clear_screen()
                    
                    print(f"\n   {cfg.CYAN}{cfg.BOLD}--- COMPARE TOOL SELECTION ---{cfg.END}")
                    print(f"   {cfg.GREEN}[1]{cfg.END} String Comparison")
                    print(f"   {cfg.GREEN}[2]{cfg.END} Regex Comparison")
                    print(f"\n   {cfg.RED}[B]{cfg.END} Back to Main Menu")
                    
                    sub = input(f"\n   {cfg.YELLOW}Select Tool > {cfg.END}").strip().upper()
                    
                    l_p = os.path.join(cfg.config["mod_path"], 'Localization')
                    d_p = os.path.join(cfg.config["mod_path"], 'Dumps')
                    
                    if sub == '1':
                        clear_screen()
                        string_comp.string_menu(l_p, d_p)
                        break 
                    elif sub == '2':
                        clear_screen()
                        regex_comp.regex_menu(l_p, d_p)
                        break 
                    elif sub == 'B':
                        break
                    else:
                        print(f"   {cfg.RED}Invalid selection!{cfg.END}")
                        os.system('timeout /t 1 > nul')
            else:
                print(f"\n   {cfg.RED}[!] Error: Invalid Path! Fix it in Settings.{cfg.END}")
                input("   Press Enter to continue...")
        
        elif choice == '2':
            clear_screen()
            translator_tool_menu()
        
        elif choice == '3':
            clear_screen()
            cfg.settings_menu_ui()
            
        elif choice == '4':
            if is_path_valid():
                clear_screen()
                auto_github.auto_github_menu(os.path.join(cfg.config["mod_path"], 'Localization'), cfg)
            else:
                input(f"   {cfg.RED}Fix path in Settings!{cfg.END}")

        elif choice == '8' and secret_unlocked:
            run_build()
        elif choice == '5':
            while True:
                clear_screen()
                print(f"\n   {cfg.GREEN}{cfg.BOLD}--- Updates (Changelog) ----{cfg.END}")
                print(f"   Current Version: {cfg.YELLOW}{__version__}{cfg.END}")
                print(f"   {cfg.YELLOW}1. Fixed some {cfg.BOLD}security{cfg.END}{cfg.YELLOW} issues{cfg.END}")
                print(f"   2. Added more colors to the UI")
                print(f"\n   {cfg.RED}[B]{cfg.END} Back to Main Menu")

                sub = input(f"\n   {cfg.YELLOW}Choice > {cfg.END}").strip().upper()
                if sub == 'B':
                    break
        elif choice == '6':
            print(f"   {cfg.YELLOW}Exiting... Goodbye!{cfg.END}")
            break

if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        print("\n   " + "="*50)
        traceback.print_exc()
        input("\n   Press Enter to close terminal...")