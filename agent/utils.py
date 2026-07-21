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
                encoding="utf-8",
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

