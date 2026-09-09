import os
import zipfile
import sys
import glob
import re
import shutil
import argparse

def parse_versions(filenames):
    stages = []      # (major, minor, patch)
    subversions = [] # (major, minor, patch, sub)
    
    # Matches X.Y.Z.N or vX.Y.Z.N
    p4 = re.compile(r'v?(\d+)\.(\d+)\.(\d+)\.(\d+)')
    # Matches X.Y.Z or vX.Y.Z (not followed by .digit)
    p3 = re.compile(r'v?(\d+)\.(\d+)\.(\d+)(?!\.\d+)')
    
    for f in filenames:
        m4 = p4.search(f)
        if m4:
            subversions.append((int(m4.group(1)), int(m4.group(2)), int(m4.group(3)), int(m4.group(4))))
            continue
        m3 = p3.search(f)
        if m3:
            stages.append((int(m3.group(1)), int(m3.group(2)), int(m3.group(3))))
            
    return stages, subversions

def get_next_version(backup_dir, explicit_version=None, explicit_stage=None, is_new_stage=False):
    if explicit_version:
        return explicit_version.lstrip('v')
        
    if not os.path.exists(backup_dir):
        return explicit_stage.lstrip('v') if explicit_stage else "1.1.0"
        
    filenames = os.listdir(backup_dir)
    stages, subversions = parse_versions(filenames)
    
    if explicit_stage:
        return explicit_stage.lstrip('v')
        
    all_bases = set(stages) | {(s[0], s[1], s[2]) for s in subversions}
    # Filter out legacy runaway versions (1.0.X where X >= 10)
    modern_bases = [b for b in all_bases if not (b[0] == 1 and b[1] == 0 and b[2] >= 10)]
    
    if is_new_stage:
        if not modern_bases:
            return "1.1.0"
        latest_base = sorted(modern_bases)[-1]
        return f"{latest_base[0]}.{latest_base[1] + 1}.0"
        
    if not modern_bases:
        current_base = (1, 1, 0)
    else:
        current_base = sorted(modern_bases)[-1]
        
    current_subs = [s[3] for s in subversions if (s[0], s[1], s[2]) == current_base]
    next_sub = (max(current_subs) + 1) if current_subs else 1
    return f"{current_base[0]}.{current_base[1]}.{current_base[2]}.{next_sub}"

def backup(description, explicit_version=None, explicit_stage=None, is_new_stage=False):
    cwd = os.getcwd()
    backup_dir = os.path.join(cwd, "Версии кода")
    os.makedirs(backup_dir, exist_ok=True)
    
    version = get_next_version(
        backup_dir, 
        explicit_version=explicit_version, 
        explicit_stage=explicit_stage, 
        is_new_stage=is_new_stage
    )
    
    # Clean description for safe filename
    safe_desc = "".join([c for c in description if c.isalpha() or c.isdigit() or c in ' -_().,']).strip()
    if not safe_desc:
        safe_desc = "бэкап"
        
    base_name = f"{version} ({safe_desc})"
    zip_filename = f"{base_name}.zip"
    zip_filepath = os.path.join(backup_dir, zip_filename)
    
    exclude_dirs = {'node_modules', '.gemini', 'Версии кода', '__pycache__', 'autoparts-store', '.git', 'temporary files'}
    
    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(cwd):
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
            for file in files:
                if (file.endswith('.zip') and root == cwd) or file.startswith('~$') or file.endswith('.tmp'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, cwd)
                try:
                    zipf.write(file_path, arcname)
                except Exception as e:
                    print(f"Skipping {file_path}: {e}")
                
    print(f"ZIP Backup created: {zip_filepath}")
    
    # 2. Создаем html файл (копия самого свежего html файла из корня)
    html_files = glob.glob(os.path.join(cwd, '*.html'))
    if html_files:
        latest_html = max(html_files, key=os.path.getmtime)
        html_dest = os.path.join(backup_dir, f"{base_name}.html")
        shutil.copy2(latest_html, html_dest)
        print(f"HTML Backup created: {html_dest}")
        
    return base_name

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Автоматическое резервное копирование проекта с 4-уровневым версионированием.")
    parser.add_argument("description", nargs="?", default="автоматический бэкап", help="Краткое описание изменений")
    parser.add_argument("--stage", dest="stage", default=None, help="Фиксация нового этапа X.Y.Z (например, 1.1.0)")
    parser.add_argument("--new-stage", dest="new_stage", action="store_true", help="Автоматический инкремент этапа (X.Y+1.0)")
    parser.add_argument("--version", dest="version", default=None, help="Явное указание версии (например, 1.1.0.5)")
    
    args = parser.parse_args()
    backup(
        args.description, 
        explicit_version=args.version, 
        explicit_stage=args.stage, 
        is_new_stage=args.new_stage
    )
