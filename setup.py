import os
import shutil

def create_directory_structure(base_dir, structure):
    for dir_path in structure:
        os.makedirs(os.path.join(base_dir, dir_path), exist_ok=True)

def copy_emoji_pack(src, dest):
    if os.path.exists(src):
        shutil.copytree(src, dest, dirs_exist_ok=True)
    else:
        print(f"Source directory {src} does not exist.")

def copy_base_files(src_dir, dest_dir):
    if os.path.exists(src_dir):
        for item in os.listdir(src_dir):
            item_path = os.path.join(src_dir, item)
            dest_path = os.path.join(dest_dir, item)
            
            # If it's a directory, copy it as a tree
            if os.path.isdir(item_path):
                shutil.copytree(item_path, dest_path, dirs_exist_ok=True)
            # If it's a file, copy it directly
            elif os.path.isfile(item_path):
                shutil.copy2(item_path, dest_path)
    else:
        print(f"Source directory {src_dir} does not exist.")

base_directory = "assets"
directory_structure = [
    "cache",
    "downloads",
    "ios_emoji_pack",
    "output",
    "sounds",
    "storage"
]

if __name__ == "__main__":
    create_directory_structure(base_directory, directory_structure)
    
    # Copy emoji pack
    src_emoji_pack = "./setup/ios_emoji_pack"
    dest_emoji_pack = os.path.join(base_directory, "ios_emoji_pack")
    copy_emoji_pack(src_emoji_pack, dest_emoji_pack)
    
    # Copy other base files from setup directory to base_directory
    src_setup_dir = "./setup"
    copy_base_files(src_setup_dir, base_directory)
