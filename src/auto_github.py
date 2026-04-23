import os
import json
import shutil

def get_config_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "Data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return os.path.join(data_dir, "repo_config.json")

def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_config(repo_path, blacklist):
    config_path = get_config_path()
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump({"repo_path": repo_path, "blacklist": blacklist}, f, indent=4)

def paginate_files(files, page_size=10):
    pages = [files[i:i + page_size] for i in range(0, len(files), page_size)]
    return pages

def manage_blacklist(all_files, current_blacklist):
    pages = paginate_files(all_files)
    current_page = 0
    
    while True:
        print(f"\n--- Blacklist Settings (Page {current_page + 1}/{len(pages)}) ---")
        print("Select a file to toggle (Ignored files will not be copied):")
        
        for i, file in enumerate(pages[current_page], 1):
            status = "[IGNORED]" if file in current_blacklist else "[INCLUDE]"
            print(f"{i}. {status} {file}")
        
        print("\nN: Next Page | P: Previous Page | S: Save & Finish")
        cmd = input("Enter Number or Navigation: ").strip().lower()
        
        if cmd == 'n' and current_page < len(pages) - 1:
            current_page += 1
        elif cmd == 'p' and current_page > 0:
            current_page -= 1
        elif cmd == 's':
            break
        elif cmd.isdigit():
            idx = int(cmd) - 1
            if 0 <= idx < len(pages[current_page]):
                selected_file = pages[current_page][idx]
                if selected_file in current_blacklist:
                    current_blacklist.remove(selected_file)
                else:
                    current_blacklist.append(selected_file)
    return current_blacklist

def auto_github_menu(loc_base):
    print("\n" + "="*35)
    print("      AUTO GITHUB SYNC V2")
    print("="*35)

    config = load_config()
    repo_path = ""
    blacklist = []

    if config:
        repo_path = config.get('repo_path', "")
        blacklist = config.get('blacklist', [])
        print(f"Repo Path: {repo_path}")
        print(f"Blacklisted Files: {len(blacklist)}")
        print("\n1. Start Sync")
        print("2. Change Directory / Manage Blacklist")
        choice = input("Choice: ").strip()
        if choice == '2':
            repo_path = input("Enter Local Repository Path: ").strip().strip('"')
    else:
        repo_path = input("Enter Local Repository Path: ").strip().strip('"')

    if not os.path.exists(repo_path):
        print("[!] Path is invalid!")
        return

    # Select Source Folder
    folders = [f for f in os.listdir(loc_base) if os.path.isdir(os.path.join(loc_base, f))]
    print("\nSelect Source Folder:")
    for i, f in enumerate(folders, 1): 
        print(f"{i}. {f}")
    
    try:
        f_idx = int(input(f"Select (1-{len(folders)}): ")) - 1
        src_path = os.path.join(loc_base, folders[f_idx])
    except: 
        return

    # Gather all files for blacklist management
    all_files = []
    for root, dirs, filenames in os.walk(src_path):
        for f in filenames:
            all_files.append(os.path.relpath(os.path.join(root, f), src_path))
    
    blacklist = manage_blacklist(all_files, blacklist)
    save_config(repo_path, blacklist)

    # Execution Configuration
    target_base = os.path.join(repo_path, "PvZ_Fusion_Translator", "Localization", "Indonesian")
    
    confirm = input(f"\nReplace 'Indonesian' folder in Repo? (y/n): ").lower()
    if confirm == 'y':
        if os.path.exists(target_base): 
            shutil.rmtree(target_base)
        
        # Ignore function for shutil.copytree
        def ignore_files(folder, files):
            ignored = []
            for f in files:
                full_path = os.path.join(folder, f)
                rel_path = os.path.relpath(full_path, src_path)
                if rel_path in blacklist:
                    ignored.append(f)
            return ignored

        shutil.copytree(src_path, target_base, ignore=ignore_files)
        print("\n[✓] Sync Successful (Blacklisted files were skipped)!")
    else:
        print("[*] Cancelled.")