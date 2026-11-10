# GameForge Studio — Obsidian Glass Slate (v1.1.0)

Professional Windows desktop application for multi-agent game engineering, autonomous 24-hour generative game pipelines, project control, and safe local AI workflows.

Designed for game creators working across Unreal Engine, Godot, ESP-IDF handhelds, Unity, Three.js, and Blender.

---

## Downloads & Installation

### 1. Windows Installer (`Setup.exe`)
Download **`GameForgeStudio-Setup-v1.1.0.exe`** from [GitHub Releases](https://github.com/CharmCompanion/GameForgeStudio/releases).
- Standard Windows wizard installer created with Inno Setup.
- Digitally signed with Authenticode (`GameForge Studio (CharmCompanion)`).
- Installs to `%LOCALAPPDATA%\Programs\GameForge Studio`.
- Creates Start Menu and optional Desktop shortcuts with the custom Obsidian Forge icon (`app.ico`).
- Includes uninstaller.

### 2. Standalone Portable Executable (`.exe`)
Download **`GameForgeStudio-v1.1.0-win64-portable.zip`** or `GameForgeStudio.exe`.
- Standalone portable Windows application (packaged with embedded Python runtime and Three.js viewport).
- Dark Slate Obsidian Glass UI with native Windows 11 rounded window corners.
- Digitally signed with Authenticode.
- Includes `Trust-Certificate.cmd` to register publisher trust with a single click.

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

## 🚀 What's New in v1.1.0 (Full Automation Upgrade)

1. **🔄 Multi-Turn Autonomous ReAct Loop (Chained Tool Use)**:
   - Agents now operate in a continuous reasoning loop: **Thought $\rightarrow$ Action / Tool Call $\rightarrow$ Real Observation $\rightarrow$ Next Action**.
   - Inspect files (`read_file`), search project code (`search_code`), and modify assets (`write_file`) autonomously across up to 8 iterations without requiring user prompts between steps.
   - If `Ask before edits` is selected, proposals pause for diff review in the Approval Center; if `Full project editing` is enabled, files are modified directly with pre-edit `.bak` rollback history.
   - Cancel anytime with the instant **Stop** button.

2. **🎮 Interactive 3D Three.js Viewport (`viewport3d.py`)**:
   - Hardware-accelerated WebGL 3D asset inspector embedded directly into GameForge Studio via Edge Chromium WebView2.
   - Inspect `.gltf`, `.glb`, and `.obj` meshes with OrbitControls (rotation, pan, zoom).
   - Includes a stylized 3D Samurai character proxy matching the 24-hour generative pipeline.
   - Tools: 4-side camera turnarounds (Front/Side/Back/Perspective), wireframe mode, turntable auto-rotation, floor grid/shadows, and real-time polygon/vertex/FPS diagnostics.

3. **🔐 Authenticode Code Signing & Trust Installer**:
   - Both `GameForgeStudio.exe` and `GameForgeStudio-Setup-v1.1.0.exe` are digitally signed with Authenticode certificates.
   - Packaged with `Trust-Certificate.cmd` and `CharmCompanion_GameForge.cer` for 1-click Windows trust installation to eliminate SmartScreen warnings.

---

## 🎮 The 24-Hour Generative AI Game Pipeline Support

GameForge Studio is built specifically to support the modern iterative AI game pipeline (concept video $\rightarrow$ 3D mesh $\rightarrow$ parallel coding $\rightarrow$ test prototype $\rightarrow$ level world $\rightarrow$ agent bug fixes):

1. **Step 1: Reference Video & Concept Ingestion**
   - Import video frames, concept sheets, and moodboards via the **Attachments** console.
2. **Step 2: 3D World & Mesh Pipeline**
   - Detects local **Blender** installations (`blender.exe`) and launches the **3D Viewport** for `.gltf`, `.glb`, and `.obj` models.
3. **Step 3: Character Generation & Turnarounds**
   - Multi-view 4-side character turnaround sheet attachments are automatically routed to multimodal vision models (GPT-4o / Gemini) for mesh alignment.
4. **Step 4: Real-time Prototype Testing**
   - Direct integration with **Godot** (`godot.exe`), **Unreal Engine** (`.uproject`), and Web project runners.
5. **Step 5: Multi-Level World Building**
   - High-throughput parallel prompts and dynamic workflows for generating environment code and scene manifests.
6. **Step 6: Autonomous Agent Bug-Fix Loop**
   - Autonomous ReAct tool loop (`read_file`, `search_code`, `write_file`) lets agents inspect runtime errors, propose diffs, and fix bugs iteratively.

---

## Key Features & Invariants

### 🧠 Intelligent Auto-Routing (Dynamic Model Switching)
- **Vision & Turnarounds**: Automatically selects **Google Gemini** or **OpenAI GPT-4o** multimodal models.
- **Architecture & Systems**: Automatically routes to **Claude 3.5 Sonnet / Opus** or **GPT-4o**.
- **Fast Syntax Checks & Offline**: Automatically routes to local **Ollama** (`llama3`, `deepseek-coder`).
- **Manual Override**: Always allows the user to pin or switch providers manually at any time.

### ⚡ Real-Time Multi-Provider Token Streaming
- Token-by-token streaming in the Chat & Agents console across Ollama, OpenAI SSE, Anthropic SSE, and Gemini SSE.
- Real-time token velocity (`tok/s`), generation latency, and token counters.

### 🧙 First-Run Setup Wizard with AI Logins
- 4-step introductory wizard detecting system toolchains (Git, Python, Blender, Godot, Unreal, Cursor, VS Code, Ollama, Ninja, CMake).
- Live AI login / credential verification for Google Gemini, Anthropic Claude, OpenAI, and Ollama.
- Auto-populates existing keys from environment variables.

### 🛡️ Recovery Center & Safe Checkpoints
- One-click timestamped ZIP recovery checkpoints for any project.
- **Restore Invariant**: Checkpoint archives can ONLY be restored to a new, empty folder—never overwriting existing directories.
- **Edit Rollback**: Every agent file modification retains a pre-edit backup with sha256 hashes, allowing 1-click rollback from the Approval Center.

### 🔒 GameForge Connect Team Billing Invariants
- Mandatory safety invariant: Team-paid AI resources are strictly **OPT-IN** per member and per project.
- **Disabled by default**.
- Individual spending caps with hard ceiling ($0.00 default).
- Immediate revocation kill-switch.
- Prohibits automatic cost splitting between workspace members.
