import os
import pandas as pd
from common import *
import json


def save_mods_table(table):
    table.to_csv(MODS_TABLE, index=False)


def save_enabled_table(table):
    table.to_csv(ENABLED_TABLE, index=False)


def save_path_table(table):
    table.to_csv(PATH_TABLE, index=False)


def get_paths():
    path_table = pd.read_csv(PATH_TABLE)
    path_list = path_table["path"].to_list()
    if len(path_list) != 4:
        assert ValueError(
            "Path table does not have 4 paths! (mod_folder, media_folder, mesh_zip, texture_zip)")
    return path_list[0], path_list[1], path_list[2], path_list[3]


def update_paths(mod_folder=None, media_folder=None, mesh_zip=None, texture_zip=None):
    path_table = pd.read_csv(PATH_TABLE)
    if mod_folder is not None and mod_folder:
        path_table.loc[path_table["var_name"] ==
                       "mod_folder", "path"] = mod_folder
    if media_folder is not None and media_folder:
        path_table.loc[path_table["var_name"] ==
                       "media_folder", "path"] = media_folder
    if mesh_zip is not None and mesh_zip:
        path_table.loc[path_table["var_name"] ==
                       "mesh_zip", "path"] = mesh_zip
    if texture_zip is not None and texture_zip:
        path_table.loc[path_table["var_name"] ==
                       "texture_zip", "path"] = texture_zip
    save_path_table(path_table)


def init_database():
    # Table: MODS
    # Columns: mod_name:str, enabled:bool

    # Table: ENABLED_MODS
    # Columns: mod_name:str, media_files:list[str], mesh_files:list[str], texture_files:list[str]

    # Table: PATHS
    # Columns: var_name:str, path:str
    # var_names: mod_folder, media_folder, mesh_zip, texture_zip

    if not os.path.isfile(MODS_TABLE):
        mods_table = pd.DataFrame(columns=["mod_name", "enabled"])
        save_mods_table(mods_table)

    if not os.path.isfile(ENABLED_TABLE):
        enabled_table = pd.DataFrame(
            columns=["mod_name", "media_files", "mesh_files", "texture_files"])
        save_enabled_table(enabled_table)

    if not os.path.isfile(PATH_TABLE):
        data = {
            "var_name": ["mod_folder", "media_folder", "mesh_zip", "texture_zip"],
            "path": ["mod" if TEST else "C:\Games\Spintires Original\mod", "Media" if TEST else "C:\Games\Spintires Original\Media", "MeshCache.zip" if TEST else "C:\Games\Spintires Original\MeshCache.zip", "TextureCache.zip" if TEST else "C:\Games\Spintires Original\TextureCache.zip"]
        }
        path_table = pd.DataFrame(data=data)
        save_path_table(path_table)

    MOD_FOLDER, MEDIA_FOLDER, MESH_ZIP, TEXTURE_ZIP = get_paths()
    init_mods(MOD_FOLDER)


def init_mods(mod_folder):
    mods_table = pd.read_csv(MODS_TABLE)
    mods, _ = read_folder(mod_folder)
    mods_table = mods_table[mods_table["mod_name"].isin(mods)]
    for mod in mods:
        if mod not in mods_table["mod_name"].values:
            new_row = {"mod_name": mod, "enabled": False}
            mods_table.loc[len(mods_table)] = new_row
    save_mods_table(mods_table)


def enable_mod(mod_name, files_copied):
    mods_table = pd.read_csv(MODS_TABLE)
    enabled_table = pd.read_csv(ENABLED_TABLE)

    mods_table.loc[mods_table["mod_name"] == mod_name, "enabled"] = True

    new_row = {"mod_name": mod_name, "media_files": json.dumps(files_copied["media"]), "mesh_files": json.dumps(
        files_copied["mesh"]), "texture_files": json.dumps(files_copied["texture"])}
    enabled_table.loc[len(enabled_table)] = new_row

    save_mods_table(mods_table)
    save_enabled_table(enabled_table)


def disable_mod(mod_name):
    mods_table = pd.read_csv(MODS_TABLE)
    enabled_table = pd.read_csv(ENABLED_TABLE)

    mods_table.loc[mods_table["mod_name"] == mod_name, "enabled"] = False
    mod_entry = enabled_table[enabled_table["mod_name"] == mod_name]
    enabled_table = enabled_table[enabled_table["mod_name"] != mod_name]

    save_mods_table(mods_table)
    save_enabled_table(enabled_table)

    return mod_entry
