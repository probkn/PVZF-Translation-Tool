import json
import os
import re
import shutil

def get_error_context(file_path, line_no):
    """Fetches 3 lines around the error for preview"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        start = max(0, line_no - 2)
        end = min(len(lines), line_no + 1)
        context = []
        for i in range(start, end):
            prefix = ">>> " if i == line_no - 1 else "    "
            context.append(f"{i+1}{prefix}{lines[i].rstrip()}")
        return "\n".join(context)
    except:
        return "Failed to retrieve context."

def fix_syntax_logic(content):
    """Attempts to fix common JSON syntax errors"""
    # 1. Add missing commas between objects
    content = re.sub(r'"\s*\n\s*"', '",\n"', content)
    # 2. Remove trailing commas before closing braces
    content = re.sub(r',\s*}', '}', content)
    # 3. Balance braces
    open_b = content.count('{')
    close_b = content.count('}')
    if open_b > close_b:
        content += '}' * (open_b - close_b)
    return content

def find_duplicates(file_path):
    dupes = []
    keys_found = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            # Look for "key": pattern
            match = re.search(r'"(.*?)"\s*:', line)
            if match:
                key = match.group(1)
                if key in keys_found:
                    dupes.append({"key": key, "lines": [keys_found[key], i]})
                keys_found[key] = i
    return dupes

def string_checker_menu(loc_base):
    print("\n" + "="*35)
    print("      STRING CHECKER V2")
    print("="*35)
    
    folders = [f for f in os.listdir(loc_base) if os.path.isdir(os.path.join(loc_base, f))]
    for i, f in enumerate(folders, 1): print(f"{i}. {f}")
    
    try:
        idx = int(input("Select folder: ")) - 1
        lang = folders[idx]
        file_path = os.path.join(loc_base, lang, 'Strings', 'translation_strings.json')
    except: return

    if not os.path.exists(file_path):
        print("[!] File not found.")
        return

    while True:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        syntax_error = None
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            syntax_error = e

        # 1. CHECK SYNTAX FIRST
        if syntax_error:
            print(f"\n[!] Syntax Error: {syntax_error.msg} (Line {syntax_error.lineno})")
            print(get_error_context(file_path, syntax_error.lineno))
            if input("\nFix Syntax Errors? (y/n): ").lower() == 'y':
                fixed_content = fix_syntax_logic(content)
                # Backup sebelum rewrite
                backup_path = file_path + ".bak"
                shutil.copy(file_path, backup_path)
                print(f"[i] Backup created: {backup_path}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                print("[✓] Syntax fixed. Re-checking...")
                continue

        # 2. CHECK DUPLICATES (Only runs if syntax is OK)
        dupes = find_duplicates(file_path)
        if dupes:
            print(f"\n[!] Found {len(dupes)} duplicate keys!")
            for d in dupes[:3]: # Show 3 examples
                print(f"  - Key '{d['key']}' found on lines {d['lines'][0]} and {d['lines'][1]}")
            
            print("\nDuplicate Fix Options:")
            print("1. Delete LAST string (Keep original)")
            print("2. Delete FIRST string (Keep newest/bottom)")
            print("3. Skip")
            
            choice = input("Choice (1/2/3): ").strip()
            
            if choice in ['1', '2']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                indices_to_remove = set()
                for d in dupes:
                    if choice == '1':
                        indices_to_remove.add(d['lines'][1] - 1)
                    else:
                        indices_to_remove.add(d['lines'][0] - 1)
                
                new_lines = [line for i, line in enumerate(lines) if i not in indices_to_remove]
                
                # Attempt to clean up and re-save as valid JSON
                try:
                    final_data = json.loads(fix_syntax_logic("".join(new_lines)))
                    # Backup sebelum rewrite ke folder Backups
                    backup_dir = os.path.join(os.path.dirname(__file__), "Backups")
                    os.makedirs(backup_dir, exist_ok=True)

                    backup_name = os.path.basename(file_path) + ".bak"
                    backup_path = os.path.join(backup_dir, backup_name)

                    shutil.copy(file_path, backup_path)
                    print(f"[i] Backup created in Backups: {backup_path}")

                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(final_data, f, indent=4, ensure_ascii=False)
                    print("[✓] Duplicates cleaned successfully!")
                except:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
                    print("[!] Duplicates deleted, but JSON still requires manual syntax repair.")
            else:
                print("[*] Duplicates skipped.")
        else:
            if not syntax_error:
                print("\n[✓] File is CLEAN (No syntax errors or duplicates found)!")
        
        break # Exit loop when finished