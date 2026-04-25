import json
import os
import re
import shutil

def get_error_context(file_path, line_no):
    """Retrieves 3 lines around the error for preview"""
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
    except Exception as e:
        return f"   \033[91m[!] Failed to retrieve line context: {e}\033[0m"

def fix_logic(content):
    """Advanced logic for repairing JSON strings"""
    # 1. Fix: Missing comma between closing and opening curly braces
    content = re.sub(r'}\s*{', '},\n{', content)
    # 2. Fix: Missing comma between closing and opening square brackets
    content = re.sub(r']\s*\[', '],\n[', content)
    # 3. Remove trailing commas before closing brackets
    content = re.sub(r',\s*([\]}])', r'\1', content)
    # 4. Add missing closing brackets at end of file
    for open_char, close_char in [('{', '}'), ('[', ']')]:
        diff = content.count(open_char) - content.count(close_char)
        if diff > 0:
            content += close_char * diff
    return content

def validator_menu(file_path):
    while True:
        errors = []
        raw_content = ""

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            data = json.loads(raw_content)

            # Check for duplicates if JSON is valid
            for sec, key in [('plants', 'seedType'), ('zombies', 'theZombieType')]:
                if sec in data:
                    seen = set()
                    for item in data[sec]:
                        val = item.get(key)
                        if val in seen:
                            errors.append(f"Duplicate ID: {val}")
                        seen.add(val)
        except json.JSONDecodeError as e:
            errors.append(f"Syntax Error: {e.msg} (Line {e.lineno})")
            error_line = e.lineno
        except Exception as e:
            errors.append(f"Error: {str(e)}")

        if not errors:
            print(f"\n   \033[92m[✓]\033[0m {os.path.basename(file_path)} is Clean!")
            break

        print(f"\n   \033[91m[!]\033[0m Issues found in {os.path.basename(file_path)}:")
        for err in errors:
            print(f"   - {err}")

        syntax_err = [e for e in errors if "Syntax Error" in e]
        if syntax_err:
            print("\n   \033[96m--- BROKEN CODE PREVIEW ---\033[0m")
            print(get_error_context(file_path, error_line))

            print("\n   \033[93m--- REPAIR SIMULATION ---\033[0m")
            fixed_sim = fix_logic(raw_content)
            try:
                test_json = json.loads(fixed_sim)
                print("   \033[92m[✓] Simulation SUCCESSFUL. The script can auto-fix this.\033[0m")

                ask = input("\n   Apply auto-fix? (y/n): ").lower()
                if ask == 'y':
                    # --- BACKUP SYSTEM ---
                    backup_dir = os.path.join(os.path.dirname(__file__), "Backups")
                    os.makedirs(backup_dir, exist_ok=True)

                    backup_name = os.path.basename(file_path) + ".bak"
                    backup_path = os.path.join(backup_dir, backup_name)

                    try:
                        shutil.copy(file_path, backup_path)
                        print(f"   \033[93m[i]\033[0m Backup created in Backups: {backup_path}")
                    except Exception as e:
                        print(f"   \033[91m[!] Failed to create backup: {e}\033[0m")

                    # --- VALIDATION & SAVE ---
                    try:
                        test_json = json.loads(fixed_sim)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(test_json, f, indent=4, ensure_ascii=False)
                        print(f"   \033[92m[✓] File updated successfully!\033[0m")
                    except json.JSONDecodeError as e:
                        print(f"   \033[91m[!] Validation failed: {e}\033[0m")
                        print(f"   \033[93m[i]\033[0m Backup preserved, file not overwritten.")
                    continue
            except Exception as e:
                print(f"   \033[91m[!] Simulation FAILED: {e}\033[0m")
                print("   \033[93m[i]\033[0m Damage is too severe for auto-fix.")

        print("\n   1. Re-check")
        print("   2. Exit (Manual Fix)")
        pilih = input("   Selection: ").strip()
        if pilih != '1':
            break
