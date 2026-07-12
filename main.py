# result = subprocess.run([
#     "docker", "run", "--rm",
#     "-v", f"{project_root}:/workspace",
#     "-w", "/workspace",
#     "python:3.11-slim",  # or some image with what we need
#     *command_list
# ], capture_output=True, text=True, timeout=10)
#
#
#
#
# dockerfile_dir = os.path.dirname(os.path.abspath(__file__))
# dockerfile_path = os.path.join(dockerfile_dir, "Dockerfile")