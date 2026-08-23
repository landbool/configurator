import os
import zipfile
import sys
import glob
import re
import shutil

def get_next_version(backup_dir):
    if not os.path.exists(backup_dir):
        return "1.0.0"
    
    versions = []
    # match vX.Y.Z
    pattern = re.compile(r'v(\d+)\.(\d+)\.(\d+)')
    for f in os.listdir(backup_dir):
        match = pattern.search(f)
        if match:
            versions.append((int(match.group(1)), int(match.group(2)), int(match.group(3))))
    
    if not versions:
        return "1.0.0"
    
    versions.sort()
    major, minor, patch = versions[-1]
    return f"{major}.{minor}.{patch + 1}"

def backup(description):
    cwd = os.getcwd()
    backup_dir = os.path.join(cwd, "Версии кода")
    os.makedirs(backup_dir, exist_ok=True)
    
    version = get_next_version(backup_dir)
    safe_desc = "".join([c for c in description if c.isalpha() or c.isdigit() or c==' ' or c=='-' or c=='_']).rstrip()
    
    # 1. Создаем zip архив
    zip_filename = f"v{version} ({safe_desc}).zip"
    zip_filepath = os.path.join(backup_dir, zip_filename)
    
    exclude_dirs = {'node_modules', '.gemini', 'Версии кода', '__pycache__', 'autoparts-store', '.git'}
    
    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(cwd):
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
            for file in files:
                if file.endswith('.zip') and root == cwd:
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, cwd)
                zipf.write(file_path, arcname)
                
    print(f"ZIP Backup created: {zip_filepath}")
    
    # 2. Создаем html файл (копия самого свежего html файла из корня)
    html_files = glob.glob(os.path.join(cwd, '*.html'))
    if html_files:
        latest_html = max(html_files, key=os.path.getmtime)
        html_dest = os.path.join(backup_dir, f"v{version} ({safe_desc}).html")
        shutil.copy2(latest_html, html_dest)
        print(f"HTML Backup created: {html_dest}")

if __name__ == "__main__":
    desc = sys.argv[1] if len(sys.argv) > 1 else "автоматический бекап"
    backup(desc)
