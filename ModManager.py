from typing import List
import ruamel.std.zipfile as zipfile
import os
import shutil
from alive_progress import alive_bar
from common import *
from DatabaseManager import *


def add_to_zip(files: list, zip_path: str):
    copied_files = []

    # Open the ZIP file in append mode
    with zipfile.ZipFile(zip_path, 'a', zipfile.ZIP_DEFLATED) as zipf:
        # Get the list of files already in the ZIP archive
        existing_files = set(zipf.namelist())
        with alive_bar(len(files), title=f"Copying into {zip_path}") as bar:
            for file in files:
                # Get the base name of the file (to match the naming in the ZIP archive)
                base_name = os.path.basename(file)

                # Check if the file already exists in the ZIP archive
                if base_name not in existing_files:
                    # Add the file to the ZIP archive
                    zipf.write(file, arcname=base_name)
                    copied_files.append(base_name)

                bar()

    return copied_files


def remove_from_zip(files: list, zip_path: str):
    zipfile.delete_from_zip_file(zip_path, file_names=files)


def copy_folder(source_dir: str, target_dir: str) -> List[str]:
    copied_files = []
    # Ensure the target directory exists
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Walk through the source directory
    for root, dirs, files in os.walk(source_dir):
        # Determine the relative path to the source directory
        relative_path = os.path.relpath(root, source_dir)
        target_path = os.path.join(target_dir, relative_path)

        # Create corresponding directories in the target directory
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        # Copy files that do not already exist in the target directory
        with alive_bar(len(files), title=f"Copying {root} into {target_path}") as bar:
            for file in files:
                source_file = os.path.join(root, file)
                target_file = os.path.join(target_path, file)

                if not os.path.exists(target_file):
                    shutil.copy2(source_file, target_file)
                    copied_files.append(os.path.abspath(target_file))
                bar()

    return copied_files


def install_mod(mod_name):
    MOD_FOLDER, MEDIA_FOLDER, MESH_ZIP, TEXTURE_ZIP, _ = get_paths()
    print(f"Mod name: {mod_name}")
    media_path = os.path.join(MOD_FOLDER, mod_name, "media")
    try:
        subfolders, _ = read_folder(media_path)
    except FileNotFoundError:
        print(f"No media folder found in {mod_name}")
    mod_table = pd.read_csv(MODS_TABLE)
    mod_info = mod_table[mod_table["mod_name"] == mod_name]
    mod_type = mod_info["type"]
    files_copied = {
        "media": [],
        "mesh": [],
        "texture": []
    }
    if (mod_type == "vehicle").bool():
        media_folders = ["billboards", "classes",
                         "meshes", "sounds", "textures"]

    elif (mod_type == "map").bool():
        media_folders = ["levels", "classes", "meshes", "textures", "strings", "sounds"]

    mesh_folders = ["MeshCache"]
    texture_folders = ["TextureCache"]

    media_copies = []
    for subfolder in subfolders:
        folder_path = os.path.join(media_path, subfolder)
        if subfolder in media_folders:
            media_copies.extend(copy_folder(
                folder_path, os.path.join(MEDIA_FOLDER, subfolder)))
        elif subfolder in mesh_folders:
            _, files = read_folder(folder_path)
            files_copied["mesh"] = add_to_zip(files, MESH_ZIP)
        elif subfolder in texture_folders:
            _, files = read_folder(folder_path)
            files_copied["texture"] = add_to_zip(files, TEXTURE_ZIP)

    files_copied["media"] = media_copies
    enable_mod(mod_name, files_copied)


def uninstall_mod(mod_name, delete):
    MOD_FOLDER, _, MESH_ZIP, TEXTURE_ZIP, _ = get_paths()
    mod_entry = disable_mod(mod_name)
    if not mod_entry.empty:
        media_files = json.loads(mod_entry["media_files"].values[0])
        mesh_files = json.loads(mod_entry["mesh_files"].values[0])
        texture_files = json.loads(mod_entry["texture_files"].values[0])

        with alive_bar(len(media_files), title=f"Removing Media files from {mod_name}") as bar:
            for file in media_files:
                if os.path.exists(file):
                    os.remove(file)
                bar()
        if len(mesh_files) > 0:
            print(f"Removing mesh files for {mod_name}")
            remove_from_zip(mesh_files, MESH_ZIP)
        if len(texture_files) > 0:
            print(f"Removing texture files for {mod_name}")
            remove_from_zip(texture_files, TEXTURE_ZIP)

        if delete:
            shutil.rmtree(os.path.join(MOD_FOLDER, mod_name))
            mods_table = pd.read_csv(MODS_TABLE)
            mods_table = mods_table[mods_table['mod_name'] != mod_name]


def reset():
    _, MEDIA_FOLDER, MESH_ZIP, TEXTURE_ZIP, _ = get_paths()
    if os.path.exists(MEDIA_FOLDER):
        shutil.rmtree(MEDIA_FOLDER)
    os.makedirs(MEDIA_FOLDER)

    if os.path.exists(MESH_ZIP):
        os.remove(MESH_ZIP)
    with open(MESH_ZIP, "w") as f:
        pass

    if os.path.exists(TEXTURE_ZIP):
        os.remove(TEXTURE_ZIP)
    with open(TEXTURE_ZIP, "w") as f:
        pass

    if os.path.exists(MODS_TABLE):
        os.remove(MODS_TABLE)

    if os.path.exists(ENABLED_TABLE):
        os.remove(ENABLED_TABLE)

    if os.path.exists(PATH_TABLE):
        os.remove(PATH_TABLE)

# reset()
