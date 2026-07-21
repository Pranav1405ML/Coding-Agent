# Agent Cody
 
A CLI coding agent that reads/writes files, searches your codebase, runs safe commands, and helps you work in any project directory — inspired by Claude Code.
 
Built as a learning project by [Pranav Ganesh](https://github.com/Pranav1405ML), from first principles: APIs, tool calling, agent loops, FastAPI, SQLite, and Python packaging.
 
## Features
 
- 📖 **Read files** — inspect any file in your project
- ✍️ **Write files** — with automatic backups before overwriting
- 📁 **List directories** — one level deep, clean output
- 🔍 **Project-wide search** — find keywords across your entire codebase with line numbers
- ⚡ **Run commands** — safe, allowlisted commands (`git status`, `pytest`, etc.) with human approval for execution-tier commands
- 🌍 **Works anywhere** — dynamically operates on whatever directory you run it from
## Installation
 
Install inside a virtual environment (recommended):
 
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```
 
Then install directly from GitHub:
 
```bash
pip install git+https://github.com/Pranav1405ML/Coding-Agent.git
```
 
> ⚠️ Make sure your virtual environment is **activated** whenever you want to run `myagent` — otherwise the command won't be found on your terminal's PATH.
 
### Requirements
 
- Python 3.11+
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — required for running execution-tier commands (`pytest`) in an isolated sandbox. Without Docker, all other tools (reading, writing, listing, searching files, and read-only commands like `git status`) still work fine.
## Setup
 
Agent Cody uses Google's Gemini API. You'll need a free API key from [Google AI Studio](https://aistudio.google.com/api-keys?).
 
Set it as an environment variable:
 
```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY="your-key-here"
 
# macOS/Linux
export GEMINI_API_KEY="your-key-here"
```
 
## Usage
 
Navigate to any project directory and run:
 
```bash
myagent
```
 
Agent Cody will initialize using your current directory as its workspace:
 
```
Agent successfully initialised.
Workspace: /path/to/your/project
Chat started. Type 'exit' to quit.
 
You: list the files here
Agent Cody: ...
```
 
Type `exit` or press `Ctrl+C` to end the session.
 
## Security Notes
 
- Blocked paths: `.env`, `.git`, `venv`, `__pycache__`, `.idea` are never readable or writable by the agent.
- Command execution uses a strict allowlist. Info commands (`git status`, `git log`, `git diff`) run directly on your machine, read-only; execution commands (`pytest`) require explicit human approval, with the target file's contents shown before you approve.
- Execution-tier commands run inside a **disposable Docker container**, not on your host machine. Each run spins up a fresh, isolated container (built from a custom image with `pytest` pre-installed), mounts only your project folder into it, executes the command, then destroys the container immediately after. Your real project files are visible to the command, but nothing else on your machine is.

## Development
 
This project was built as a mentorship-driven learning exercise, prioritizing understanding fundamentals (APIs, tool calling, agent architecture, packaging) over speed. See commit history for the full build journey.

## Limitations

- A file with more than 100k characters (roughtly >1000 lines of code) might not be readable for the agent.
- This decision was made to preserve the tokens and to use the api limits efficiently.
- The agent cant run any other commands than the ones explicitly allowed (mentioned above).
- The agent cannot run tests without docker being installed on the system.

## License
 
MIT
