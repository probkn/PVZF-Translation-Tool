import json
import os
import re

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
    except:
        return "Failed to retrieve line context."

def fix_logic(content):
    """Advanced logic for repairing JSON strings"""
    # 1. Fix: Missing comma between closing and opening curly braces
    # Example: } {  becomes }, {
    content = re.sub(r'}\s*{', '},\n{', content)
    
    # 2. Fix: Missing comma between closing and opening square brackets
    # Example: ] [  becomes ], [
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
        
        # Read raw file for later fix processing
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
            print(f"\n[✓] {os.path.basename(file_path)} is Clean!")
            break
        
        print(f"\n[!] Issues found in {os.path.basename(file_path)}:")
        for err in errors:
            print(f"  - {err}")

        # Show Preview if Syntax Error exists
        syntax_err = [e for e in errors if "Syntax Error" in e]
        if syntax_err:
            print("\n--- BROKEN CODE PREVIEW ---")
            print(get_error_context(file_path, error_line))
            
            print("\n--- REPAIR SIMULATION ---")
            fixed_sim = fix_logic(raw_content)
            try:
                # Test if simulation produces valid JSON
                test_json = json.loads(fixed_sim)
                print("[✓] Simulation SUCCESSFUL. The script can auto-fix this.")
                
                tanya = input("\nApply auto-fix? (y/n): ").lower()
                if tanya == 'y':
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(test_json, f, indent=4, ensure_ascii=False)
                    print("[✓] File updated successfully!")
                    continue
            except:
                print("[!] Simulation FAILED. Damage is too severe for auto-fix.")
        
        print("\n1. Re-check")
        print("2. Exit (Manual Fix)")
        pilih = input("Selection: ").strip()
        if pilih != '1': 
            break