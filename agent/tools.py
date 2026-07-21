import os
import subprocess
from agent.utils import AccessDeniedError, TIER_INFO, TIER_EXECUTION, _raw_read, _raw_write, _check_permission, _is_allowed, _command_output, _get_verified_root, _get_blocked_list, _get_blocked_folders


def read_file(path):
    project_root, isvalid = _get_verified_root()

    if not isvalid:
        return project_root

    full_path = os.path.join(project_root, path)
    blocked_list = _get_blocked_list(project_root)

    try:
        _check_permission(full_path, blocked_list)
    except AccessDeniedError as e:
        return f"Error: {e}"

    if not os.path.exists(full_path):
        return "Error: The specified path does not exist."

    if not os.path.isfile(full_path):
        return "Error: The path points to a directory, not a readable file."

    char_limit = 100000
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

    project_root, isvalid = _get_verified_root()

    if not isvalid:
        return project_root

    full_path = os.path.join(project_root, write_path)
    blocked_list = _get_blocked_list(project_root)

    try:
        _check_permission(full_path, blocked_list)
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
    project_root, isvalid = _get_verified_root()

    if not isvalid:
        return project_root

    full_path = os.path.join(project_root, folder_path)
    blocked_list = _get_blocked_list(project_root)

    try:
        _check_permission(full_path, blocked_list)
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

    project_root, isvalid = _get_verified_root()

    if not isvalid:
        return project_root

    blocked_folders = _get_blocked_folders()
    blocked_list = _get_blocked_list(project_root)

    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in blocked_folders]
        for file in files:
            full_path = os.path.join(root, file)

            try:
                _check_permission(full_path, blocked_list)
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


def run_command(command):
    project_root, ok = _get_verified_root()
    if not ok:
        return project_root  # this is the error string in the failure case

    command_list = command.split()
    allowed, tier, valid_path = _is_allowed(command_list)

    if not allowed:
        return f"You do not have permission to run this command."

    try:
        if tier == TIER_INFO:
            return _command_output(command_list, tier, project_root)

        elif tier == TIER_EXECUTION:
            content = _raw_read(valid_path)
            print()
            print(content)
            print()
            choice = input("Do you want to give the permission to agent to run this file? [Y/N]:")
            if choice.lower() == "y":
                return _command_output(command_list, tier, project_root)
            else:
                return f"User did not give permission to run this file."

    except subprocess.TimeoutExpired as e:
        return f"This process was killed as it took more than 10 second to respond."

    except Exception as e:
        return f"Unexpected error occurred. {e}"


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
    },

"run_command": {
    "name": "run_command",
    "description": (
        "Executes a single allowed command from a restricted allowlist [git status, git log, git diff, pytest]"
        "and returns its standard output or error output. This tool should be used only when runtime "
        "information is required and cannot be determined by reading project files alone. "
        "Supported informational commands (such as safe Git status, log, and diff operations) execute "
        "immediately. Commands that execute project code or tests (such as pytest on an allowed file) "
        "require explicit human approval before execution. The tool automatically rejects any command "
        "outside the allowlist and enforces a timeout to prevent indefinitely running processes. "
        "Typical use cases include checking repository status, viewing commit history, verifying code "
        "changes with tests, observing runtime errors, debugging failing test cases, and validating "
        "whether recent modifications behave as expected."
    ),
    "function": run_command,
    "parameters": {
        "command": (
            "string - A single command to execute exactly as it would be typed in the terminal. "
            "The command must belong to the allowed command set (for example, safe git commands "
            "or approved pytest invocations)."
        )
    }
   }

}

