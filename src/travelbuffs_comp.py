import json
import os
import urllib.request
import shutil

GITHUB_URL = "https://raw.githubusercontent.com/Teyliu/PVZF-Translation/main/PvZ_Fusion_Translator/Localization/English/Strings/travel_buffs.json"

# ─────────────────────────────────────────────
#  UTILITY
# ─────────────────────────────────────────────

def simple_translate(text):
    if not isinstance(text, str):
        return text
    rules = {
        '）': ')',
        '（': '(',
        '，': ', ',
        '。': '. ',
        '：': ': '
    }
    for cn, idn in rules.items():
        text = text.replace(cn, idn)
    return text


def fetch_github_json(url):
    print(f"[*] Loading Data from GitHub...")
    try:
        with urllib.request.urlopen(url) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        print("[✓] GitHub Data Loaded Successfully.")
        return data
    except Exception as e:
        print(f"[!] Action Failed: {e}")
        return None


def select_lang_folder(loc_base):
    folders = [f for f in os.listdir(loc_base) if os.path.isdir(os.path.join(loc_base, f))]
    print("\n--- Choose Language Folder ---")
    for i, f in enumerate(folders, 1):
        print(f"  {i}. {f}")
    try:
        idx = int(input(f"Select number (1-{len(folders)}): ")) - 1
        return folders[idx]
    except:
        print("[!] Invalid selection.")
        return None


# ─────────────────────────────────────────────
#  TRAVEL BUFFS LOGIC
# ─────────────────────────────────────────────

def find_missing_buffs(source: dict, target: dict) -> dict:
    """
    Compare source (GitHub/Dumps) vs target (local translation).
    Return dictionary of missing entries.
    """
    missing = {}
    for category, entries in source.items():
        if category not in target:
            missing[category] = entries
        else:
            missing_entries = {}
            for idx, value in entries.items():
                if idx not in target[category]:
                    missing_entries[idx] = value
            if missing_entries:
                missing[category] = missing_entries
    return missing


def count_missing(missing: dict) -> int:
    return sum(len(v) for v in missing.values())


def translate_buffs(missing: dict) -> dict:
    translated = {}
    for category, entries in missing.items():
        translated[category] = {idx: simple_translate(val) for idx, val in entries.items()}
    return translated


def merge_buffs(target: dict, additions: dict) -> dict:
    result = {k: dict(v) for k, v in target.items()}
    for category, entries in additions.items():
        if category not in result:
            result[category] = {}
        result[category].update(entries)
    return result


# ─────────────────────────────────────────────
#  ALMANAC NAME REPLACER
# ─────────────────────────────────────────────

def build_name_map(lawn_data: dict, zombie_data: dict, trans_lawn: dict, trans_zombie: dict) -> dict:
    """
    Create mapping: chinese_name -> translated_name
    """
    name_map = {}

    # Plants
    dump_plants = {p['seedType']: p.get('name', '') for p in lawn_data.get('plants', [])}
    for p in trans_lawn.get('plants', []):
        sid = p.get('seedType')
        cn_name = dump_plants.get(sid, '')
        tr_name = p.get('name', '')
        if cn_name and tr_name and cn_name != tr_name:
            name_map[cn_name] = tr_name

    # Zombies
    dump_zombies = {z['theZombieType']: z.get('name', '') for z in zombie_data.get('zombies', [])}
    for z in trans_zombie.get('zombies', []):
        zid = z.get('theZombieType')
        cn_name = dump_zombies.get(zid, '')
        tr_name = z.get('name', '')
        if cn_name and tr_name and cn_name != tr_name:
            name_map[cn_name] = tr_name

    return name_map


def replace_names_in_buffs(buffs: dict, name_map: dict) -> tuple[dict, int]:
    """
    Replace Chinese names in travel_buffs with translated names.
    """
    result = {}
    total_replaced = 0
    for category, entries in buffs.items():
        result[category] = {}
        for idx, text in entries.items():
            new_text = text
            for cn, tr in name_map.items():
                if cn in new_text:
                    new_text = new_text.replace(cn, tr)
                    total_replaced += 1
            result[category][idx] = new_text
    return result, total_replaced


def almanac_replace_menu(loc_base, dump_base, buffs_data: dict, target_lang: str):
    print("\n" + "="*35)
    print("   ALMANAC NAME REPLACER")
    print("="*35)

    # Load almanac dumps
    try:
        with open(os.path.join(dump_base, 'LawnStrings.json'), 'r', encoding='utf-8') as f:
            lawn_dump = json.load(f)
        with open(os.path.join(dump_base, 'ZombieStrings.json'), 'r', encoding='utf-8') as f:
            zombie_dump = json.load(f)
    except Exception as e:
        print(f"[!] Failed to load Almanac Dumps: {e}")
        return buffs_data

    # Select language folder for source names
    print(f"\n[*] Select Reference Language Folder")
    print(f"    (Used to replace Chinese names in travel_buffs '{target_lang}')")
    alm_lang = select_lang_folder(loc_base)
    if not alm_lang:
        return buffs_data

    try:
        lawn_path = os.path.join(loc_base, alm_lang, 'Almanac', 'LawnStringsTranslate.json')
        zombie_path = os.path.join(loc_base, alm_lang, 'Almanac', 'ZombieStringsTranslate.json')
        with open(lawn_path, 'r', encoding='utf-8') as f:
            trans_lawn = json.load(f)
        with open(zombie_path, 'r', encoding='utf-8') as f:
            trans_zombie = json.load(f)
    except Exception as e:
        print(f"[!] Failed to load almanac translation for '{alm_lang}': {e}")
        return buffs_data

    name_map = build_name_map(lawn_dump, zombie_dump, trans_lawn, trans_zombie)
    print(f"[*] Found {len(name_map)} name mappings from almanac.")

    replaced_buffs, count = replace_names_in_buffs(buffs_data, name_map)
    print(f"[✓] {count} names replaced in travel_buffs successfully.")

    return replaced_buffs


# ─────────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────────

def travelbuffs_menu(loc_base, dump_base):
    print("\n" + "="*35)
    print("   TRAVEL BUFFS COMPARISON")
    print("="*35)

    report_dir = os.path.join(os.path.dirname(__file__), 'Util Report')
    os.makedirs(report_dir, exist_ok=True)

    # -- Data Source Selection ------------------
    print("\n[*] Travel Buffs Source")
    print("  1. From GitHub (Online)")
    print("  2. From Dumps Folder (Local)")
    src_choice = input("Select (1/2): ").strip()

    source_data = None
    if src_choice == '1':
        source_data = fetch_github_json(GITHUB_URL)
    elif src_choice == '2':
        local_path = os.path.join(dump_base, 'travel_buffs.json')
        if os.path.exists(local_path):
            with open(local_path, 'r', encoding='utf-8') as f:
                source_data = json.load(f)
            print(f"[✓] Local Dumps Loaded Successfully.")
        else:
            print(f"[!] File not found: {local_path}")
            return
    else:
        print("[!] Invalid option.")
        return

    if source_data is None:
        return

    # -- Target Language Selection --------------
    print("\n[*] Select Target Language Folder:")
    target_lang = select_lang_folder(loc_base)
    if not target_lang:
        return

    target_path = os.path.join(loc_base, target_lang, 'Strings', 'travel_buffs.json')

    target_data = {}
    if os.path.exists(target_path):
        with open(target_path, 'r', encoding='utf-8') as f:
            target_data = json.load(f)
        print(f"[✓] Target file found.")
    else:
        print(f"[!] Target file not found in '{target_lang}'. A new one will be created.")

    # -- Analysis -------------------------------
    missing = find_missing_buffs(source_data, target_data)
    total_missing = count_missing(missing)

    print(f"\n[*] Comparison Result for '{target_lang}':")
    if total_missing == 0:
        print("[✓] All strings are up to date! No missing entries.")
        # We don't return here so user can still access sub-menus if needed
    else:
        print(f"[!] Found {total_missing} missing strings:")
        for cat, entries in missing.items():
            print(f"    - {cat}: {len(entries)} strings")

    # -- Sub Menu -------------------------------
    current_missing = missing 

    while True:
        print("\n--- Options ---")
        print("1. Generate Report File (missing_buffs.json)")
        print("2. Append Missing Strings to Target File")
        print("3. Auto-Translate (Fix Chinese Punctuation)")
        print("4. Replace Chinese Names with Translated Almanac Names")
        print("5. Back")

        sub = input("Select: ").strip()

        if sub == '1':
            report_path = os.path.join(report_dir, 'missing_buffs.json')
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(current_missing, f, indent=2, ensure_ascii=False)
            print(f"[✓] Report saved to: {report_path}")

        elif sub == '2':
            if not current_missing and total_missing != 0:
                print("   \033[91m[!] No pending strings to add (already merged or empty).\033[0m")
            else:
                merged = merge_buffs(target_data, current_missing)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)

                # --- BACKUP SYSTEM ---
                backup_dir = os.path.join(os.path.dirname(__file__), "Backups")
                os.makedirs(backup_dir, exist_ok=True)
                backup_name = os.path.basename(target_path) + ".bak"
                backup_path = os.path.join(backup_dir, backup_name)

                try:
                    shutil.copy(target_path, backup_path)
                    print(f"   \033[93m[i]\033[0m Backup created in Backups: {backup_path}")
                except Exception as e:
                    print(f"   \033[91m[!] Failed to create backup: {e}\033[0m")

                # --- VALIDATION & SAVE ---
                try:
                    json.loads(json.dumps(merged))  # quick validation
                    with open(target_path, 'w', encoding='utf-8') as f:
                        json.dump(merged, f, indent=2, ensure_ascii=False)
                    print(f"   \033[92m[✓] {len(current_missing)} categories updated in '{target_lang}'!\033[0m")
                except Exception as e:
                    print(f"   \033[91m[!] Write failed: {e}\033[0m")
                    print(f"   \033[93m[i]\033[0m Backup preserved, file not overwritten.")

                target_data = merged
                current_missing = {}
                break

        elif sub == '3':
            current_missing = translate_buffs(current_missing)
            print("[✓] Chinese punctuation replaced in memory.")
            print("    (Choose option 1 or 2 to save changes)")

        elif sub == '4':
            current_missing = almanac_replace_menu(loc_base, dump_base, current_missing, target_lang)
            print("    (Choose option 1 or 2 to save changes)")

        elif sub == '5':
            break
        else:
            print("[!] Invalid selection.")