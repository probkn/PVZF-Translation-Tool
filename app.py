import os
import json
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import almanac_comp as comp
import almanac_check as checker
import string_comp
import regex_comp
import auto_github
import string_check
import travelbuffs_comp

def find_actual_base():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.abspath(os.path.join(script_dir, "..", "PvZ_Fusion_Translator")),
        os.path.abspath(os.path.join(script_dir, "..", "Mods", "PvZ_Fusion_Translator")),
        os.path.abspath(os.path.join(script_dir, "PvZ_Fusion_Translator"))
    ]
    for path in candidates:
        if os.path.exists(os.path.join(path, "Localization")): return path
    
    print("[!] 'PvZ_Fusion_Translator' Folder not found.")
    return input("Enter Path to Mod Folder: ").strip().strip('"')

def select_lang(loc_path):
    folders = [f for f in os.listdir(loc_path) if os.path.isdir(os.path.join(loc_path, f))]
    print("\n--- Choose Language Folder ---")
    for i, f in enumerate(folders, 1): print(f"{i}. {f}")
    try:
        idx = int(input(f"Choose number (1-{len(folders)}): ")) - 1
        return folders[idx]
    except: return None

if __name__ == '__main__':
    base_folder = find_actual_base()
    loc_base = os.path.join(base_folder, 'Localization')
    dump_base = os.path.join(base_folder, 'Dumps')
    report_dir = os.path.join(os.path.dirname(__file__), 'Util Report')
    if not os.path.exists(report_dir): os.makedirs(report_dir)

    BANNER = r"""
    ╔════════════════════════════════════════════════════╗
    ║  ██████╗ ██╗   ██╗███████╗    ███████╗             ║
    ║  ██╔══██╗██║   ██║╚════██║    ██╔════╝             ║
    ║  ██████╔╝██║   ██║    ██╔╝    █████╗               ║
    ║  ██╔═══╝ ╚██╗ ██╔╝   ██╔╝     ██╔══╝               ║
    ║  ██║      ╚████╔╝    ██║      ██║                  ║
    ║  ╚═╝       ╚═══╝     ╚═╝      ╚═╝                  ║
    ║  ███████╗██╗   ██╗███████╗██╗ ██████╗ ███╗  ██╗    ║
    ║  ██╔════╝██║   ██║██╔════╝██║██╔═══██╗████╗ ██║    ║
    ║  █████╗  ██║   ██║███████╗██║██║   ██║██╔██╗██║    ║
    ║  ██╔══╝  ██║   ██║╚════██║██║██║   ██║██║╚████║    ║
    ║  ██║     ╚██████╔╝███████║██║╚██████╔╝██║ ╚███║    ║
    ║  ╚═╝      ╚═════╝ ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚══╝    ║
    ║  ·  ·  ·  ·  T O O L S   ·  ·  ·  ·                ║
    ╚════════════════════════════════════════════════════╝"""

    while True:
        print(BANNER)
        print("1. Almanac Comparison")
        print("2. Almanac Checker")
        print("3. String Comparison")
        print("4. Regex Comparison")
        print("5. Travel Buffs Comparison")      # ← New
        print("6. Sync ke GitHub Desktop (Copy-Replace)")
        print("7. String Checker (New)")
        print("8. Quit")
        
        choice = input("Choose Menu: ").strip()

        if choice == '1':
            try:
                # 1. Tentukan Sumber Data (Dump dari Game)
                with open(os.path.join(dump_base, 'LawnStrings.json'), 'r', encoding='utf-8') as f: dl = json.load(f)
                with open(os.path.join(dump_base, 'ZombieStrings.json'), 'r', encoding='utf-8') as f: dz = json.load(f)
                
                # 2. Pilih Folder Bahasa yang ingin dibandingkan (Target)
                print("\n[Select language folder to compare with Dumps]")
                target_lang = select_lang(loc_base)
                
                if not target_lang:
                    print("[!] No folder selected. Returning to menu.")
                    continue

                # Path ke file target yang dipilih user
                tlp_path = os.path.join(loc_base, target_lang, 'Almanac', 'LawnStringsTranslate.json')
                tzp_path = os.path.join(loc_base, target_lang, 'Almanac', 'ZombieStringsTranslate.json')

                if not os.path.exists(tlp_path) or not os.path.exists(tzp_path):
                    print(f"[!] Files not found in {target_lang}/Almanac/ folder.")
                    continue

                with open(tlp_path, 'r', encoding='utf-8') as f: il = json.load(f)
                with open(tzp_path, 'r', encoding='utf-8') as f: iz = json.load(f)
                
                # 3. Cari Perbedaan
                mp = comp.find_missing_entries(il.get('plants', []), dl.get('plants', []), 'seedType')
                mz = comp.find_missing_entries(iz.get('zombies', []), dz.get('zombies', []), 'theZombieType')
                
                while True:
                    print(f"\n--- Comparison Result: {target_lang} ---")
                    print(f"[ Missing Data: {len(mp)} Plant, {len(mz)} Zombie ]")
                    print("1. Automatic Translate (Memory)")
                    print("2. Create Report File (missing.json)")
                    print(f"3. Add to {target_lang} main JSON")
                    print("4. Back")
                    
                    sub = input("Choose: ").strip()
                    if sub == '1':
                        mp, mz = comp.translate_batch(mp), comp.translate_batch(mz)
                        print("[✓] Translated and saved in memory.")
                    elif sub == '2':
                        with open(os.path.join(report_dir, 'missing.json'), 'w', encoding='utf-8') as f:
                            json.dump({'plants': mp, 'zombies': mz}, f, indent=4, ensure_ascii=False)
                        print("[✓] Created Report file.")
                    elif sub == '3':
                        # Langsung update ke folder yang tadi dipilih di awal
                        il['plants'].extend(mp); iz['zombies'].extend(mz)
                        with open(tlp_path, 'w', encoding='utf-8') as f: json.dump(il, f, indent=4, ensure_ascii=False)
                        with open(tzp_path, 'w', encoding='utf-8') as f: json.dump(iz, f, indent=4, ensure_ascii=False)
                        print(f"[✓] Updated Successfully {target_lang}!")
                        mp, mz = [], []; break
                    elif sub == '4': break
            except Exception as e: print(f"Error Comp: {e}")

        elif choice == '2':
            lang = select_lang(loc_base)
            if lang:
                for fn in ['LawnStringsTranslate.json', 'ZombieStringsTranslate.json']:
                    p = os.path.join(loc_base, lang, 'Almanac', fn)
                    if os.path.exists(p): checker.validator_menu(p)

        elif choice == '3':
            string_comp.string_menu(loc_base, dump_base)
        elif choice == '4':
            regex_comp.regex_menu(loc_base, dump_base)
        elif choice == '5':
            travelbuffs_comp.travelbuffs_menu(loc_base, dump_base)
        elif choice == '6':
            auto_github.auto_github_menu(loc_base)
        if choice == '7':
            string_check.string_checker_menu(loc_base)
        elif choice == '8':
            break