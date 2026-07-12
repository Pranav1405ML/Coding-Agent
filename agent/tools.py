import os
import subprocess
from agent.config import get_project_root

class AccessDeniedError(Exception):
    pass

ALLOWED_EXECUTION_COMMANDS = ["pytest"]
ALLOWED_INFO_COMMANDS = ["git status", "git log", "git diff"]

TIER_INFO = "info"
TIER_EXECUTION = "execution"

_image_built = False

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

# The underscore prefix on _raw_write is a Python convention, by the way —
# it signals "this is an internal helper, not meant to be used directly from outside this file."
def _raw_write(path, content):
    with open(path, "w") as f:
        f.write(content)

def _raw_read(path):
    with open(path, "r") as f:
        return f.read()

def _check_permission(path, BLOCKED_LIST):
    for blocked in BLOCKED_LIST:
        if path == blocked or path.startswith(blocked + os.sep): # without os.sep, "venv2".startswith("venv") is True as a pure string comparison, even though venv2 is a completely unrelated folder
            raise AccessDeniedError(f"Access to {path} is restricted.")


# KNOWN LIMITATION: If _get_verified_root() fails (agent not initialized),
# this returns (False, None, None) silently, causing run_command to say
# "no permission" instead of "agent not initialized" — misleading but not dangerous.
# Fix: raise an exception here instead of returning a tuple, letting
# run_command's except Exception catch it with the real message.

def _is_allowed(command_list):
    project_root, isvalid = _get_verified_root()

    if not isvalid:
        return False, None, None

    joined = " ".join(command_list)
    if joined in ALLOWED_INFO_COMMANDS:
        return True, TIER_INFO, None

    elif len(command_list) == 2 and command_list[0] in ALLOWED_EXECUTION_COMMANDS:
        abs_target_path = os.path.join(project_root, command_list[1])
        blocked_list = _get_blocked_list(project_root)

        if os.path.exists(abs_target_path) and abs_target_path.startswith(project_root + os.sep):
                try:
                    _check_permission(abs_target_path, blocked_list)
                    return True, TIER_EXECUTION, abs_target_path

                except AccessDeniedError:
                    return False, None, None
    return False, None, None

def _command_output(command_list, tier, project_root):
    if tier == TIER_EXECUTION:
        built, error = _ensure_image_built()
        if not built:
            return error

        docker_command = [
            "docker", "run", "--rm",
            "-v", f"{project_root}:/workspace",
            "-w", "/workspace",
            "agent-cody-sandbox",
            *command_list
        ]

        try:
            result = subprocess.run(
                docker_command,
                capture_output=True,
                text=True,
                timeout=10
            )
            return f"Output: {result.stdout}\nError: {result.stderr}\nReturn Code: {result.returncode}\n"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out."

    else:
        result = subprocess.run(
            command_list,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=project_root
        )
        return f"Output: {result.stdout}\nError: {result.stderr}\nReturn Code: {result.returncode}\n"

def _ensure_image_built():
    global _image_built
    if _image_built:
        return True, None

    dockerfile_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        result = subprocess.run(
            ["docker", "build", "-t", "agent-cody-sandbox", dockerfile_dir],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode != 0:
            return False, f"Docker build failed: {result.stderr}"

        _image_built = True
        return True, None

    except FileNotFoundError:
        return False, "Docker is not installed or not found on this system. Execution-tier commands require Docker."
    except subprocess.TimeoutExpired:
        return False, "Docker build timed out."

def _get_verified_root():
    try:
        project_root = get_project_root()
        return project_root, True

    except NotADirectoryError as e:
        return f"Error: Agent not initialized. {e}", False

def _get_blocked_list(project_root):
    return [
        os.path.join(project_root, ".env"),
        os.path.join(project_root, ".git"),
        os.path.join(project_root, "venv"),
        os.path.join(project_root, "__pycache__"),
        os.path.join(project_root, ".idea"),
    ]

def _get_blocked_folders():
    return [".git", "venv", "__pycache__", ".idea"]


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

