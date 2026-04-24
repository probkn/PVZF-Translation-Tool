import os
import json
import shutil

def get_config_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "Data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return os.path.join(data_dir, "config.json")

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

def manage_blacklist(all_files, current_blacklist, cfg):
    pages = paginate_files(all_files)
    current_page = 0
    
    while True:
        print(f"\n{cfg.CYAN}{cfg.BOLD}--- Blacklist Settings (Page {current_page + 1}/{len(pages)}) ---{cfg.END}")
        print(f"{cfg.YELLOW}Select a file to toggle (Ignored files will not be copied):{cfg.END}")
        
        for i, file in enumerate(pages[current_page], 1):
            if file in current_blacklist:
                status = f"{cfg.RED}[IGNORED]{cfg.END}"
            else:
                status = f"{cfg.GREEN}[INCLUDE]{cfg.END}"
            print(f"{cfg.CYAN}{i}.{cfg.END} {status} {file}")
        
        print(f"\n{cfg.YELLOW}N:{cfg.END} Next Page | {cfg.YELLOW}P:{cfg.END} Previous Page | {cfg.YELLOW}S:{cfg.END} Save & Finish | {cfg.YELLOW}B:{cfg.END} Back")
        cmd = input(f"{cfg.YELLOW}Enter Number or Navigation:{cfg.END} ").strip().lower()
        
        if cmd == 'n' and current_page < len(pages) - 1:
            current_page += 1
        elif cmd == 'p' and current_page > 0:
            current_page -= 1
        elif cmd == 's':
            break
        elif cmd == 'b':
            # keluar tanpa menyimpan perubahan
            return current_blacklist
        elif cmd.isdigit():
            idx = int(cmd) - 1
            if 0 <= idx < len(pages[current_page]):
                selected_file = pages[current_page][idx]
                if selected_file in current_blacklist:
                    current_blacklist.remove(selected_file)
                else:
                    current_blacklist.append(selected_file)
    return current_blacklist

def auto_github_menu(loc_base, cfg):
    print("\n" + "="*35)
    print(f"      {cfg.CYAN}{cfg.BOLD}Auto GitHub Sync{cfg.END}")
    print("="*35)

    config = load_config()
    repo_path = ""
    blacklist = []

    if config:
        repo_path = config.get('repo_path', "")
        blacklist = config.get('blacklist', [])
        print(f"{cfg.YELLOW}Repo Path:{cfg.END} {repo_path}")
        print(f"{cfg.YELLOW}Blacklisted Files:{cfg.END} {len(blacklist)}")
        print(f"\n{cfg.CYAN}1.{cfg.END} Start Sync")
        print(f"{cfg.CYAN}2.{cfg.END} Change Directory / Manage Blacklist")
        choice = input(f"{cfg.YELLOW}Choice:{cfg.END} ").strip()
        if choice == '2':
            repo_path = input(f"{cfg.CYAN}Enter Local Repository Path:{cfg.END} ").strip().strip('"')
            # simpan langsung setelah diubah
            save_config(repo_path, blacklist)
    else:
        repo_path = input(f"{cfg.CYAN}Enter Local Repository Path:{cfg.END} ").strip().strip('"')
        # simpan path baru pertama kali
        save_config(repo_path, blacklist)

    if not os.path.exists(repo_path):
        print(f"{cfg.RED}[!] Path is invalid!{cfg.END}")
        return

    # Select Source Folder
    folders = [f for f in os.listdir(loc_base) if os.path.isdir(os.path.join(loc_base, f))]
    print(f"\n{cfg.BOLD}Select Source Folder:{cfg.END}")
    for i, f in enumerate(folders, 1): 
        print(f"{cfg.CYAN}{i}.{cfg.END} {f}")
    print(f"{cfg.RED}B.{cfg.END} Back")

    try:
        choice = input(f"{cfg.YELLOW}Select (1-{len(folders)} or B):{cfg.END} ").strip().upper()
        if choice == 'B':
            return  # keluar dari menu tanpa lanjut
        f_idx = int(choice) - 1
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
    loc_repo = os.path.join(repo_path, "PvZ_Fusion_Translator", "Localization")
    if not os.path.exists(loc_repo):
        print(f"{cfg.RED}[!] Localization folder not found in repo!{cfg.END}")
        return

    # Pilih folder bahasa di repo
    repo_folders = [f for f in os.listdir(loc_repo) if os.path.isdir(os.path.join(loc_repo, f))]
    print(f"\n{cfg.BOLD}Select Target Language Folder in Repo:{cfg.END}")
    for i, f in enumerate(repo_folders, 1):
        print(f"{cfg.CYAN}{i}.{cfg.END} {f}")
    print(f"{cfg.RED}B.{cfg.END} Back")

    try:
        choice = input(f"{cfg.YELLOW}Select (1-{len(repo_folders)} or B):{cfg.END} ").strip().upper()
        if choice == 'B':
            return
        t_idx = int(choice) - 1
        target_lang = repo_folders[t_idx]
    except:
        return

    target_base = os.path.join(loc_repo, target_lang)

    confirm = input(f"\n{cfg.YELLOW}Sync files into '{target_lang}' folder in Repo? (y/n):{cfg.END} ").lower()
    if confirm == 'y':
        os.makedirs(target_base, exist_ok=True)
        for root, dirs, files in os.walk(src_path):
            rel_root = os.path.relpath(root, src_path)
            dest_root = os.path.join(target_base, rel_root)
            os.makedirs(dest_root, exist_ok=True)

            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), src_path)
                if rel_path in blacklist:
                    print(f"{cfg.YELLOW}Skip:{cfg.END} {rel_path}")
                    continue
                shutil.copy2(os.path.join(root, f), os.path.join(dest_root, f))
                print(f"{cfg.GREEN}Copied:{cfg.END} {rel_path}")

        print(f"\n{cfg.GREEN}[✓] Sync Complete!{cfg.END}")
    else:
        print(f"{cfg.RED}[*] Cancelled.{cfg.END}")
