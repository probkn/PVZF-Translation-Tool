import json
import requests
import os

def load_json_from_url(url):
    """Fetches JSON data directly from GitHub (Raw)"""
    raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    try:
        response = requests.get(raw_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[!] Failed to fetch data from GitHub: {e}")
        return None

def find_missing_strings(target_dict, ref_dict):
    """Finds keys that exist in the reference but are missing in the target"""
    missing = {}
    for key, value in ref_dict.items():
        if key not in target_dict:
            missing[key] = value
    return missing

def string_menu(loc_base, dump_base):
    print("\n" + "="*35)
    print("      STRING COMPARISON MENU")
    print("="*35)
    
    # --- STEP 1: SELECT TARGET (FILE TO BE UPDATED/CHECKED) ---
    print("\nSelect Target (The file you want to check/fill):")
    folders = [f for f in os.listdir(loc_base) if os.path.isdir(os.path.join(loc_base, f))]
    for i, f in enumerate(folders, 1):
        print(f"{i}. Local: {f}")
    
    print(f"{len(folders)+1}. Online: Indonesian (Teyliu GitHub)")
    
    try:
        t_idx = int(input(f"Select (1-{len(folders)+1}): "))
        if t_idx <= len(folders):
            target_lang = folders[t_idx-1]
            target_path = os.path.join(loc_base, target_lang, 'Strings', 'translation_strings.json')
            with open(target_path, 'r', encoding='utf-8') as f:
                target_data = json.load(f)
            mode = "local"
        else:
            url_indo = "https://github.com/Teyliu/PVZF-Translation/blob/main/PvZ_Fusion_Translator/Localization/Indonesian/Strings/translation_strings.json"
            print("[*] Fetching Indonesian Target from GitHub...")
            target_data = load_json_from_url(url_indo)
            mode = "online"
            target_lang = "GitHub-Indo"
    except Exception as e:
        print(f"[!] Failed to load target: {e}")
        return

    # --- STEP 2: SELECT REFERENCE (THE SOURCE OF TRUTH) ---
    print("\nSelect Reference Source (The baseline data):")
    print("1. English (GitHub - Teyliu)")
    print("2. Indonesian (GitHub - Teyliu)")
    
    ref_choice = input("Choice (1/2): ").strip()

    ref_data = None
    if ref_choice == '1':
        url = "https://github.com/Teyliu/PVZF-Translation/blob/main/PvZ_Fusion_Translator/Localization/English/Strings/translation_strings.json"
        ref_data = load_json_from_url(url)
    elif ref_choice == '2':
        url = "https://github.com/Teyliu/PVZF-Translation/blob/main/PvZ_Fusion_Translator/Localization/Indonesian/Strings/translation_strings.json"
        ref_data = load_json_from_url(url)

    if not ref_data: 
        print("[!] Reference data is empty or could not be loaded.")
        return

    # --- STEP 3: COMPARE ---
    missing = find_missing_strings(target_data, ref_data)

    if not missing:
        print(f"\n[✓] {target_lang} is already up to date with the reference!")
    else:
        print(f"\n[!] Found {len(missing)} new strings missing in {target_lang}.")
        
        if mode == "local":
            print("1. Add missing strings to local file")
            print("2. Cancel")
            if input("Choice: ") == '1':
                target_data.update(missing)
                with open(target_path, 'w', encoding='utf-8') as f:
                    json.dump(target_data, f, indent=4, ensure_ascii=False)
                print(f"[✓] {target_lang} file updated successfully!")
        else:
            print("[INFO] Target is Online (GitHub). You can only view the differences.")
            print("Sample of missing strings:")
            for i, (k, v) in enumerate(missing.items()):
                if i >= 5: 
                    print("  ... (and more)")
                    break
                print(f"  - {k}: {v}")