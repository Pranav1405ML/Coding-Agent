import os

class AccessDeniedError(Exception):
    pass

# WARNING: This assumes tools.py always lives exactly one folder inside the project root
# (i.e. project_root/agent/tools.py). If this file or the agent/ folder is ever moved
# to a different depth, this calculation will silently point to the wrong location.
# A more robust fix would search upward for a known marker file (like .env) instead
# of assuming a fixed folder depth.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BLOCKED_FOLDERS_RAW = [".git", "venv", "__pycache__", ".idea"]
BLOCKED_FILES_RAW = [".env"]

BLOCKED_LIST = [os.path.join(PROJECT_ROOT, name) for name in BLOCKED_FOLDERS_RAW + BLOCKED_FILES_RAW]
BLOCKED_FOLDERS = BLOCKED_FOLDERS_RAW


def read_file(path):
    full_path = os.path.join(PROJECT_ROOT, path)

    try:
        _check_permission(full_path)
    except AccessDeniedError as e:
        return f"Error: {e}"

    if not os.path.exists(full_path):
        return "Error: The specified path does not exist."

    if not os.path.isfile(full_path):
        return "Error: The path points to a directory, not a readable file."

    char_limit = 10000
    try:
        file_size_bytes = os.path.getsize(full_path)

        # 1 char == 1 byte is true for plain ASCII text, but breaks for files with special characters, emojis,
        # or non-English text (UTF-8 encoding can use multiple bytes per character)

        if file_size_bytes > char_limit:   # As 1 char == 1 byte
            return f"Error: The file is too large to read fully ({file_size_bytes} bytes)."

        with open(full_path, "r") as f:
            return f.read(char_limit) # this will read at max 10k characters and
                                      # stop earlier if file ends without issues

    except PermissionError as e:
        return f"Error: You do not have permission to read this file.{e}"

    except OSError as e:
        return f"System error reading file: {e}"

    except UnicodeDecodeError as e:
        return f"Error: Encoding mismatch. Check the file format.{e}"


def write_file(write_path, content):
    overwrite = False
    full_path = os.path.join(PROJECT_ROOT, write_path)

    try:
        _check_permission(full_path)
    except AccessDeniedError as e:
        return f"Error: {e}"

    try:
        if os.path.exists(full_path):
            if not os.path.isfile(full_path):
                return "Error: The target path is a directory folder, cannot overwrite it as a file."

            save_content = _raw_read(full_path)
            _raw_write(full_path + ".backup", save_content)
            overwrite = True

        _raw_write(full_path, content)

        if overwrite:
                return f"Already existing file has been overwritten. A copy for backup has been saved as {full_path}.backup."

        return f"The content was successfully written in {full_path}."

    except PermissionError as e:
        return f"Permission Error: Lacking write permissions for this path. {e}"

    except UnicodeEncodeError as e:
        return f"Encoding Error: Content contains characters that cannot be saved. {e}"

    except OSError as e:
        return f"System Error writing file: {e}"


def list_files(folder_path):
    full_path = os.path.join(PROJECT_ROOT, folder_path)

    try:
        _check_permission(full_path)
    except AccessDeniedError as e:
        return f"Error: {e}"

    if not os.path.exists(full_path):
        return "Error: The specified path does not exist."

    if not os.path.isdir(full_path):
        return "Error: The path does not point to a directory."

    try:
        items = os.listdir(full_path)
        folders = []
        files = []
        for item in items:
            temp = os.path.join(full_path, item)
            if os.path.isdir(temp):
                folders.append(item)
            elif os.path.isfile(temp):
                files.append(item)

        folders_str = ", ".join(folders)
        files_str = ", ".join(files)

        return f"Folders : {folders_str}\nFiles : {files_str}"

    except PermissionError as e:
        return f"Error: You do not have permission to access this directory. {e}"

    except OSError as e:
        # Catches other OS-level errors like broken drives or system hiccups
        return f"Error: A system error occurred while reading the directory. {e}"


def project_wide_search(content_to_search):
    found_content = []
    search_query = content_to_search.lower()

    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in BLOCKED_FOLDERS]
        for file in files:
            full_path = os.path.join(root, file)

            try:
                _check_permission(full_path)
            except AccessDeniedError:
                continue

            try:
                with open(full_path, "r") as f:
                    for line_number, line in enumerate(f, start=1):
                        if search_query in line.lower():
                            found_content.append(f"Found {content_to_search} in {file} at line {line_number}.")

            except FileNotFoundError:
                found_content.append(f"Skipped: File vanished during scan: {file}")

            except PermissionError as e:
                found_content.append(f"You dont have permission to read {file} file. {e}")

            except OSError as e:
                found_content.append(f"System error reading file: {e}")

            except MemoryError:
                found_content.append(f"Skipped: {file} is too large to fit in memory.")

            except UnicodeDecodeError as e:
                found_content.append(f"Error: Encoding mismatch. Check the file format.{e}")

    if len(found_content) == 0:
        return f"{content_to_search} does not exist anywhere in this project"

    return found_content

# The underscore prefix on _raw_write is a Python convention, by the way —
# it signals "this is an internal helper, not meant to be used directly from outside this file."
def _raw_write(path, content):
    with open(path, "w") as f:
        f.write(content)

def _raw_read(path):
    with open(path, "r") as f:
        return f.read()

def _check_permission(path):
    for blocked in BLOCKED_LIST:
        if path == blocked or path.startswith(blocked + os.sep): # without os.sep, "venv2".startswith("venv") is True as a pure string comparison, even though venv2 is a completely unrelated folder
            raise AccessDeniedError(f"Access to {path} is restricted.")


TOOL_REGISTRY = {
    "read_file": {
        "name": "read_file",
        "description": "Reads the contents of a file at the given path. Returns an error message if the file doesn't exist, is too large, or isn't readable.",
        "function": read_file,
        "parameters":{
            "path": "string - the file path to read"
        }
    },

    "write_file": {
        "name": "write_file",
        "description": "Writes content to a file at the given path. If a file already exists there, it is backed up to the same path with '.backup' added before being overwritten.",
        "function": write_file,
        "parameters": {
            "write_path": "string - the file path to write to",
            "content": "string - the content to write into the file"
        }
    },

    "list_files": {
        "name": "list_files",
        "description": "Lists the immediate files and folders inside the given directory path, one level deep only (does not look inside subfolders).",
        "function": list_files,
        "parameters": {
            "folder_path": "string - the folder path to list contents of"
        }
    },

    "project_wide_search": {
        "name": "project_wide_search",
        "description": "Searches for a specific keyword or phrase (case-insensitive) across all permitted text files in the project workspace recursively and also reports line numbers",
        "function": project_wide_search,
        "parameters": {
            "content_to_search": "string - the text keyword, phrase, or pattern to find inside the files"
        }
    }
}

