import os

ROOT = None

def set_project_root(path):
    global ROOT

    if not os.path.exists(path):
        return f"Failed to set the Project root. Path does not exist.", False

    if not os.path.isdir(path):
        return f"Failed to set the Project root. Path is not a directory.", False

    ROOT = path
    return f"Agent successfully initialised.", True

def get_project_root():
    if not ROOT:
        raise NotADirectoryError(f"Failed to get the project root.")

    return ROOT

