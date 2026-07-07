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

## Setup

Agent Cody uses Google's Gemini API. You'll need a free API key from [Google AI Studio](https://aistudio.google.com/api-keys?).

Set it as an environment variable:

```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY="your-key-here"

# Windows (cmd)
set GEMINI_API_KEY=your-key-here

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
Gemini: ...
```

Type `exit` or press `Ctrl+C` to end the session.

## Security Notes

- Blocked paths: `.env`, `.git`, `venv`, `__pycache__`, `.idea` are never readable or writable by the agent.
- Command execution uses a strict allowlist. Info commands (`git status`, `git log`, `git diff`) run freely; execution commands (`pytest`) require explicit human approval, with the target file's contents shown before you approve.
- Docker-based sandboxing for command execution is planned (currently a placeholder using allowlist + human approval).

## Roadmap

- [ ] Docker sandboxing for command execution
- [ ] Conversation history summarization for long sessions
- [ ] Multi-Step planning and self-correction
- [ ] PyPI publication

## Development

This project was built as a curiosity-driven learning exercise, prioritizing understanding fundamentals (APIs, tool calling, agent architecture, packaging) over speed. See commit history for the full build journey.

## License

MIT