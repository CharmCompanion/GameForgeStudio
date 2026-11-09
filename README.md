# GameForge Studio — Obsidian Glass Slate

Professional Windows desktop application for multi-agent game engineering, project control, and safe local AI workflows.

Designed for game creators working across Unreal Engine, Godot, ESP-IDF handhelds, Unity, and Blender.

---

## Quick Run

### 1. Portable Executable (.exe)
Double-click `Release/GameForgeStudio.exe`.
- Standalone portable Windows application (packaged with embedded Python runtime).
- Dark Slate Obsidian Glass UI with native Windows 11 rounded window corners.
- No installation required. Unsigned executable (standard Windows SmartScreen notice may appear on first launch).

### 2. Run from Source
Open PowerShell or Command Prompt in this folder and execute:
```cmd
Run.cmd
```
Or directly with Python 3.10+:
```powershell
python app.py
```

### 3. Run Test Suite
```powershell
python -m unittest -v test_app.py
```

### 4. Rebuild Standalone Executable (.exe)
```powershell
powershell -ExecutionPolicy Bypass -File .\Build.ps1
```

---

## Key Features & Capabilities

### ⚡ Real-Time Token Streaming
- Token-by-token streaming in the Chat & Agents console.
- Supports both local Ollama streaming API and OpenAI / Anthropic / Gemini streaming SSE endpoints.
- Real-time token velocity (tokens/sec), generation latency, and token counters.

### 📎 Context Attachments
- One-click attachment of game code (.gd, .py, .cpp, .h), configuration files (.json, .ini), logs, and game bibles.
- Visual attachment pills with easy removal.
- Content is safely sandboxed and formatted into the agent's context.

### 🌐 Connected Providers & Local Models
- **Ollama (Local)**: default connection to `http://127.0.0.1:11434`. Includes model discovery (`/api/tags`), live ping check, and model switcher.
- **Hosted Providers**: OpenAI-compatible, Anthropic Claude, and Google Gemini with secure local credential storage in `%LOCALAPPDATA%\GameForgeStudio\settings.json`.
- In-app connection tester verifying endpoint status and latency.

### 🛠️ Autonomous Tool Engine & Sandboxed Execution
- Real multi-step agent execution with built-in tools:
  - `read_file(path)`: Safe project file reader.
  - `list_dir(path)`: Directory explorer.
  - `search_code(query)`: High-performance code search across project assets.
  - `write_file(path, content)`: Controlled file creation/edits with sha256 checksum review.
  - `run_safe_command(cmd)`: Whitelisted build/check commands (git, python, godot, cargo, ninja, cmake).
- **Three Project Access Modes**:
  - `Read only`: Denies all write/command tool executions.
  - `Ask before edits` (Default): Pauses for user approval with a syntax-colored unified diff viewer.
  - `Full project editing`: Allows autonomous multi-step code generation inside the project sandbox.

### ⏹️ Instant Cancellation
- Immediate "Stop" button that cancels ongoing HTTP streams and aborts autonomous execution threads instantly.

### 📋 Master Project List Integration
- Auto-detects and loads `D:\DEVELOPMENT\MASTER_PROJECTS.md` and `PROJECTS.md`.
- In-app Markdown editor with outside modification detection and automatic timestamped backups before saving.
- **Batch Project Importer**: Discovers all 57+ games / projects in the master list and registers existing on-disk projects into GameForge Studio with one click without modifying any files.

### 🛡️ Recovery Center & Safe Checkpoints
- One-click timestamped ZIP recovery checkpoints for any project.
- **Restore Invariant**: Checkpoint archives can ONLY be restored to a new, empty folder—never overwriting existing directories.
- **Edit Rollback**: Every agent file modification retains a pre-edit backup with sha256 hashes, allowing 1-click rollback from the Approval Center.

### 🧙 First-Run Setup Wizard
- 4-step introductory wizard detecting system toolchains (Git, Python, Blender, Godot, Unreal, Cursor, VS Code, Ollama, Ninja, CMake, Cargo, ESP-IDF).
- Confirms workspace paths, AI agent discovery, and team billing safety guarantees.

### 🔒 GameForge Connect Team Billing Invariants
- Mandatory safety invariant: Team-paid AI resources are strictly **OPT-IN** per member and per project.
- **Disabled by default**.
- Individual spending caps with hard ceiling ($0.00 default).
- Immediate revocation kill-switch.
- Prohibits automatic cost splitting between workspace members.
