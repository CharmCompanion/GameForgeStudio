# GameForge Studio — Obsidian Glass Slate (v1.0.0)

Professional Windows desktop application for multi-agent game engineering, 24-hour generative game pipelines, project control, and safe local AI workflows.

Designed for game creators working across Unreal Engine, Godot, ESP-IDF handhelds, Unity, Three.js, and Blender.

---

## Downloads & Installation

### 1. Windows Installer (`Setup.exe`)
Download **`GameForgeStudio-Setup-v1.0.0.exe`** from the [GitHub Releases](https://github.com/CharmCompanion/GameForgeStudio/releases).
- Standard Windows wizard installer created with Inno Setup.
- Installs to `%LOCALAPPDATA%\Programs\GameForge Studio`.
- Creates Start Menu and optional Desktop shortcuts with the custom Obsidian Forge icon (`app.ico`).
- Includes uninstaller.

### 2. Standalone Portable Executable (`.exe`)
Download **`GameForgeStudio-v1.0.0-win64-portable.zip`** or `GameForgeStudio.exe`.
- Standalone portable Windows application (packaged with embedded Python runtime).
- Dark Slate Obsidian Glass UI with native Windows 11 rounded window corners.
- No Python installation required on end-user machines.

### 3. Run from Source
Open PowerShell or Command Prompt in this folder and execute:
```cmd
Run.cmd
```
Or directly with Python 3.10+:
```powershell
python app.py
```

### 4. Run Test Suite
```powershell
python -m unittest -v test_app.py
```

---

## 🎮 The 24-Hour Generative AI Game Pipeline Support

GameForge Studio is built specifically to support the modern iterative AI game pipeline (concept video $\rightarrow$ 3D mesh $\rightarrow$ parallel coding $\rightarrow$ test prototype $\rightarrow$ level world $\rightarrow$ agent bug fixes):

1. **Step 1: Reference Video & Concept Ingestion**
   - Import video frames, concept sheets, and moodboards via the **Attachments** console.
2. **Step 2: 3D World & Mesh Pipeline**
   - Detects local **Blender** installations (`blender.exe`) and manages `.blend`, `.gltf`, `.obj` asset workflows alongside Tripo / Fal.ai.
3. **Step 3: Character Generation & Turnarounds**
   - Multi-view 4-side character turnaround sheet attachments are automatically routed to multimodal vision models (GPT-4o / Gemini) for mesh alignment.
4. **Step 4: Real-time Prototype Testing**
   - Direct integration with **Godot** (`godot.exe`), **Unreal Engine** (`.uproject`), and **Three.js** web project runners.
5. **Step 5: Multi-Level World Building**
   - High-throughput parallel prompts and dynamic workflows for generating environment code and scene manifests.
6. **Step 6: Autonomous Agent Bug-Fixing Loop**
   - Autonomous tool sandbox with `read_file`, `search_code`, and `write_file` lets agents inspect runtime errors, propose diffs, and fix bugs in parallel.

---

## Key Features & Invariants

### 🧠 Intelligent Auto-Routing (Dynamic Model Switching)
- **Automatic Task-Based Selection**: Automatically detects the nature of each task:
  - **Vision / Concept Art / Turnarounds**: Automatically selects **Google Gemini** or **OpenAI GPT-4o** multimodal models.
  - **Architecture / Systems / Complex Logic**: Automatically routes to **Claude 3.5 Sonnet / Opus** or **GPT-4o**.
  - **Fast Syntax Checks / Offline Coding**: Automatically routes to local **Ollama** (`llama3`, `deepseek-coder`, etc.).
- **Manual Override**: Always allows the user to pin or switch providers manually at any time.

### ⚡ Real-Time Multi-Provider Token Streaming
- Token-by-token streaming in the Chat & Agents console.
- Native streaming adapters for:
  - Local **Ollama** (`/api/chat` streaming JSON lines)
  - **OpenAI** SSE (`/v1/chat/completions`)
  - **Anthropic Claude** SSE (`/v1/messages`)
  - **Google Gemini** SSE (`streamGenerateContent`)
- Real-time token velocity (tokens/sec), generation latency, and token counters.

### 🧙 First-Run Setup Wizard with AI Logins
- 4-step introductory wizard detecting system toolchains (Git, Python, Blender, Godot, Unreal, Cursor, VS Code, Ollama, Ninja, CMake, Cargo, ESP-IDF).
- Live AI login / credential verification for Google Gemini, Anthropic Claude, OpenAI, and Ollama.
- Automatic key discovery from environment variables (`GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.).

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

### 🛡️ Recovery Center & Safe Checkpoints
- One-click timestamped ZIP recovery checkpoints for any project.
- **Restore Invariant**: Checkpoint archives can ONLY be restored to a new, empty folder—never overwriting existing directories.
- **Edit Rollback**: Every agent file modification retains a pre-edit backup with sha256 hashes, allowing 1-click rollback from the Approval Center.

### 📋 Master Project List Integration
- Auto-detects and loads `D:\DEVELOPMENT\MASTER_PROJECTS.md` and `PROJECTS.md`.
- In-app Markdown editor with outside modification detection and automatic timestamped backups before saving.
- **Batch Project Importer**: Discovers all 57+ games / projects in the master list and registers existing on-disk projects into GameForge Studio with one click without modifying any files.

### 🔒 GameForge Connect Team Billing Invariants
- Mandatory safety invariant: Team-paid AI resources are strictly **OPT-IN** per member and per project.
- **Disabled by default**.
- Individual spending caps with hard ceiling ($0.00 default).
- Immediate revocation kill-switch.
- Prohibits automatic cost splitting between workspace members.
