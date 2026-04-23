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

def find_missing_regex(target_dict, ref_dict):
    """Finds regex keys that exist in the reference but are missing in target"""
    missing = {}
    for key, value in ref_dict.items():
        if key not in target_dict:
            missing[key] = value
    return missing

def regex_menu(loc_base, dump_base):
    print("\n" + "="*35)
    print("     REGEX COMPARISON MENU")
    print("="*35)
    
    # --- STEP 1: CHOOSE TARGET (LOCAL FILE OR ONLINE) ---
    print("\nSelect Target (File to be checked/updated):")
    folders = [f for f in os.listdir(loc_base) if os.path.isdir(os.path.join(loc_base, f))]
    for i, f in enumerate(folders, 1):
        print(f"{i}. Local: {f}")
    
    print(f"{len(folders)+1}. Online: Indonesian (Teyliu GitHub)")
    
    try:
        t_idx_input = input(f"Select (1-{len(folders)+1}): ")
        t_idx = int(t_idx_input)
        
        if t_idx <= len(folders):
            target_lang = folders[t_idx-1]
            # Regex location is usually in Strings folder
            target_path = os.path.join(loc_base, target_lang, 'Strings', 'translation_regex.json')
            
            if not os.path.exists(target_path):
                print(f"[!] Regex file not found at: {target_path}")
                return
                
            with open(target_path, 'r', encoding='utf-8') as f:
                target_data = json.load(f)
            mode = "local"
        else:
            url_indo = "https://github.com/Teyliu/PVZF-Translation/blob/main/PvZ_Fusion_Translator/Localization/Indonesian/Strings/translation_regex.json"
            print("[*] Fetching Indonesian Regex Target from GitHub...")
            target_data = load_json_from_url(url_indo)
            mode = "online"
            target_lang = "GitHub-Indo-Regex"
            
    except Exception as e:
        print(f"[!] Failed to load target: {e}")
        return

    # --- STEP 2: CHOOSE REFERENCE (SOURCE OF TRUTH) ---
    print("\nSelect Reference Source (Baseline Data):")
    print("1. English (GitHub - Teyliu)")
    print("2. Indonesian (GitHub - Teyliu)")
    
    ref_choice = input("Choice (1/2): ").strip()

    ref_data = None
    if ref_choice == '1':
        url = "https://github.com/Teyliu/PVZF-Translation/blob/main/PvZ_Fusion_Translator/Localization/English/Strings/translation_regexs.json"
        ref_data = load_json_from_url(url)
    elif ref_choice == '2':
        url = "https://github.com/Teyliu/PVZF-Translation/blob/main/PvZ_Fusion_Translator/Localization/Indonesian/Strings/translation_regexs.json"
        ref_data = load_json_from_url(url)

    if not ref_data: 
        print("[!] Reference data could not be loaded.")
        return

    # --- STEP 3: COMPARE ---
    missing = find_missing_regex(target_data, ref_data)

    if not missing:
        print(f"\n[✓] {target_lang} regex is complete and matches the reference!")
    else:
        print(f"\n[!] Found {len(missing)} new regex patterns missing in {target_lang}.")
        
        if mode == "local":
            print("1. Add missing patterns to local file")
            print("2. Cancel")
            action = input("Selection: ")
            if action == '1':
                target_data.update(missing)
                with open(target_path, 'w', encoding='utf-8') as f:
                    json.dump(target_data, f, indent=4, ensure_ascii=False)
                print(f"[✓] Regex file for {target_lang} has been updated!")
        else:
            print("[INFO] Online comparison complete.")
            print("Preview of missing regex patterns:")
            for i, (k, v) in enumerate(missing.items()):
                if i >= 5: 
                    print("  ... (and more)")
                    break
                print(f"  - {k} -> {v}")