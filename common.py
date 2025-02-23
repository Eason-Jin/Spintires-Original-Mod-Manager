import os

TEST = False

DB_PATH = "database"
MODS_TABLE = os.path.join(DB_PATH, "mods.csv")
ENABLED_TABLE = os.path.join(DB_PATH, "enabled.csv")
PATH_TABLE = os.path.join(DB_PATH, "paths.csv")


def read_folder(folder: str):
    subfolders = []
    files = []

    for entry in os.listdir(folder):
        full_path = os.path.join(folder, entry)
        if os.path.isdir(full_path):
            subfolders.append(entry)
        elif os.path.isfile(full_path):
            files.append(os.path.abspath(full_path))

    return subfolders, files
