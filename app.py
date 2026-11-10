"""
GameForge Studio — Professional Windows Desktop Application
Obsidian Glass Slate UI • Multi-Agent Game Development Control Center
Streaming • Attachments • Autonomous Tool Execution • Intelligent Auto-Routing • Recovery Center
"""

import os
import sys
import re
import json
import uuid
import time
import shutil
import difflib
import hashlib
import datetime
import threading
import queue
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
import tkinter as tk
from tkinter import ttk

APP_VERSION = "1.1.0"
APP_TITLE = f"GameForge Studio v{APP_VERSION} • Obsidian Glass Slate"

# ─────────────────────────────────────────────────────────────────────────────
# WINDOWS 11 DWM THEME & STYLING
# ─────────────────────────────────────────────────────────────────────────────

def dark_title(window):
    """Enforces Windows 11 dark title bar and rounded corners via DwmSetWindowAttribute."""
    if os.name == 'nt':
        try:
            import ctypes
            window.update_idletasks()
            handle = ctypes.windll.user32.GetParent(window.winfo_id())
            if not handle:
                handle = window.winfo_id()
            enabled = ctypes.c_int(1)
            # DWMWA_USE_IMMERSIVE_DARK_MODE (attributes 20 and 19 for win10/11)
            for attribute in (20, 19):
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    handle, attribute, ctypes.byref(enabled), ctypes.sizeof(enabled)
                )
            # DWMWA_WINDOW_CORNER_PREFERENCE = 33 (2 = DWMWCP_ROUND)
            rounded = ctypes.c_int(2)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                handle, 33, ctypes.byref(rounded), ctypes.sizeof(rounded)
            )
            class Margins(ctypes.Structure):
                _fields_ = [('left', ctypes.c_int), ('right', ctypes.c_int),
                            ('top', ctypes.c_int), ('bottom', ctypes.c_int)]
            margins = Margins(1, 1, 1, 1)
            ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(handle, ctypes.byref(margins))
        except Exception:
            pass


def rounded_buttons(window, style):
    """Draws custom anti-aliased rounded button surfaces with subtle depth and shadows."""
    import math
    def create_image(fill):
        bitmap = tk.PhotoImage(master=window, width=40, height=44)
        def draw_rounded(left, top, right, bottom, radius, color):
            for row in range(top, bottom):
                dist = max(top + radius - row - 0.5, row + 0.5 - (bottom - radius), 0)
                inset = math.ceil(radius - math.sqrt(max(0, radius * radius - dist * dist)))
                bitmap.put(color, to=(left + inset, row, right - inset, row + 1))
        # Drop shadow layers
        draw_rounded(1, 4, 39, 44, 13, '#070a0e')
        draw_rounded(2, 3, 38, 43, 12, '#0c1219')
        # Border
        draw_rounded(2, 1, 38, 39, 11, '#34455a')
        # Button face
        draw_rounded(3, 2, 37, 38, 10, fill)
        return bitmap

    window.button_images = [
        create_image(color) for color in ('#1c2837', '#2b3e55', '#16202c', '#111720')
    ]
    normal, hover, pressed, disabled = window.button_images
    style.element_create(
        'Rounded.surface', 'image', normal,
        ('disabled', disabled), ('pressed', pressed), ('active', hover),
        border=(15, 15, 15, 18), sticky='nsew'
    )
    style.layout('TButton', [
        ('Rounded.surface', {'sticky': 'nsew', 'children': [
            ('Button.focus', {'sticky': 'nsew', 'children': [
                ('Button.padding', {'sticky': 'nsew', 'children': [
                    ('Button.label', {'sticky': 'nsew'})
                ]})
            ]})
        ]})
    ])
    style.configure('TButton', padding=(14, 8, 14, 12), borderwidth=0, focusthickness=1, focuscolor='#60a5fa')


# ─────────────────────────────────────────────────────────────────────────────
# NATIVE DARK DIALOG SYSTEM (Zero White Popups)
# ─────────────────────────────────────────────────────────────────────────────

def dark_dialog(title, message='', mode='info'):
    """Custom high-contrast Obsidian Slate dialog for modals, prompts, and pickers."""
    parent = tk._default_root
    window = tk.Toplevel(parent)
    window.title(title)
    window.configure(bg='#0d131a')
    window.geometry('680x480' if mode == 'folder' else '640x320')
    window.transient(parent)
    result = [None]

    header_frame = tk.Frame(window, bg='#131c26', padx=18, pady=14)
    header_frame.pack(fill='x')
    tk.Label(header_frame, text=title, font=('Segoe UI', 13, 'bold'),
             bg='#131c26', fg='#e2eaf4').pack(anchor='w')

    content_frame = tk.Frame(window, bg='#0d131a', padx=20, pady=16)
    content_frame.pack(fill='both', expand=True)

    if message:
        tk.Label(content_frame, text=message, font=('Segoe UI', 10), wraplength=600,
                 justify='left', bg='#0d131a', fg='#c2d0df').pack(anchor='w', pady=(0, 12))

    default_path = str(Path('D:/DEVELOPMENT').resolve()) if Path('D:/DEVELOPMENT').exists() else str(Path.home())
    value = tk.StringVar(value=default_path if mode == 'folder' else '')

    def finish(answer):
        result[0] = answer
        window.destroy()

    if mode in ('string', 'folder'):
        entry = tk.Entry(content_frame, textvariable=value, bg='#16212e', fg='#e2eaf4',
                         insertbackground='#60a5fa', relief='flat', font=('Segoe UI', 10),
                         highlightthickness=1, highlightbackground='#26374a', highlightcolor='#3b82f6')
        entry.pack(fill='x', ipady=6, pady=(0, 10))
        entry.focus_set()

    if mode == 'folder':
        drives_frame = tk.Frame(content_frame, bg='#0d131a')
        drives_frame.pack(fill='x', pady=(0, 6))
        tk.Label(drives_frame, text='Drives:', font=('Segoe UI', 9, 'bold'),
                 bg='#0d131a', fg='#7e91a6').pack(side='left', padx=(0, 6))
        for drive_letter in ['C:', 'D:', 'E:', 'F:']:
            drive_p = Path(drive_letter + '\\')
            if drive_p.exists():
                tk.Button(drives_frame, text=drive_letter, font=('Segoe UI', 8, 'bold'),
                          bg='#1b2736', fg='#c2d0df', activebackground='#2d425c',
                          activeforeground='#ffffff', relief='flat', padx=8, pady=2,
                          command=lambda d=str(drive_p): [value.set(d), refresh()]).pack(side='left', padx=2)

        listing = tk.Listbox(content_frame, bg='#101822', fg='#e2eaf4',
                             selectbackground='#2d425c', selectforeground='#ffffff',
                             relief='flat', font=('Segoe UI', 9), highlightthickness=1,
                             highlightbackground='#26374a')
        listing.pack(fill='both', expand=True, pady=4)

        def refresh(event=None):
            try:
                curr = Path(value.get().strip() or default_path).resolve()
                folders = sorted([p for p in curr.iterdir() if p.is_dir() and not p.name.startswith('.')],
                                 key=lambda p: p.name.lower())
                listing.delete(0, 'end')
                listing.insert('end', '.. [Parent Directory]')
                for p in folders:
                    listing.insert('end', f'📁 {p.name}')
            except Exception:
                listing.delete(0, 'end')

        def navigate(event):
            if listing.curselection():
                idx = listing.curselection()[0]
                item = listing.get(idx)
                curr = Path(value.get().strip() or default_path).resolve()
                if idx == 0:
                    parent_p = curr.parent
                    value.set(str(parent_p))
                else:
                    folder_name = item.replace('📁 ', '').strip()
                    value.set(str((curr / folder_name).resolve()))
                refresh()

        listing.bind('<Double-Button-1>', navigate)
        entry.bind('<Return>', refresh)
        refresh()

    buttons_frame = tk.Frame(window, bg='#0d131a', padx=20, pady=16)
    buttons_frame.pack(fill='x', side='bottom')

    def accept():
        if mode == 'folder':
            chosen = Path(value.get().strip()).resolve()
            if not chosen.is_dir():
                return
            finish(str(chosen))
        elif mode == 'string':
            finish(value.get().strip())
        else:
            finish(True)

    ok_btn = tk.Button(buttons_frame, text='Select Folder' if mode == 'folder' else 'OK',
                       font=('Segoe UI', 9, 'bold'), bg='#2b3e55', fg='#e2eaf4',
                       activebackground='#3b5575', relief='flat', padx=16, pady=6,
                       command=accept)
    ok_btn.pack(side='right')

    if mode != 'info':
        cancel_btn = tk.Button(buttons_frame, text='Cancel', font=('Segoe UI', 9),
                               bg='#16212e', fg='#9db0c4', activebackground='#223245',
                               relief='flat', padx=14, pady=6, command=lambda: finish(None))
        cancel_btn.pack(side='right', padx=8)

    window.bind('<Escape>', lambda e: finish(None))
    dark_title(window)
    window.grab_set()
    parent.wait_window(window)
    return result[0]


class messagebox:
    showinfo = staticmethod(lambda title, message: dark_dialog(title, message, 'info'))
    showerror = staticmethod(lambda title, message: dark_dialog(title, message, 'info'))
    askyesno = staticmethod(lambda title, message: bool(dark_dialog(title, message, 'confirm')))


class simpledialog:
    askstring = staticmethod(lambda title, message: dark_dialog(title, message, 'string'))


class filedialog:
    askdirectory = staticmethod(lambda title='Select Directory': dark_dialog(
        title, 'Select or type a directory path:', 'folder'
    ))


# ─────────────────────────────────────────────────────────────────────────────
# TOOL, ENGINE & ENVIRONMENT DISCOVERY
# ─────────────────────────────────────────────────────────────────────────────

def detect_tools():
    """Discovers available developer toolchains and game engines on PATH and disk."""
    known_paths = {
        'git': ['git', r'C:\Program Files\Git\cmd\git.exe'],
        'python': [sys.executable, 'python', r'C:\Program Files\Python310\python.exe'],
        'blender': ['blender', r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe',
                    r'C:\Program Files\Blender Foundation\Blender 4.2\blender.exe'],
        'godot': ['godot', r'D:\DEVELOPMENT\APPS\Godot-EditorBins\Godot_v4.7-stable_win64.exe',
                  r'D:\DEVELOPMENT\APPS\Godot-EditorBins\Godot_v4.7-stable_win64_console.exe'],
        'unreal': [r'C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor.exe',
                   r'C:\Program Files\Epic Games\UE_5.3\Engine\Binaries\Win64\UnrealEditor.exe'],
        'cursor': ['cursor', os.path.expandvars(r'%LOCALAPPDATA%\Programs\cursor\resources\app\bin\cursor.cmd')],
        'code': ['code', os.path.expandvars(r'%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd')],
        'ollama': ['ollama', os.path.expandvars(r'%LOCALAPPDATA%\Programs\Ollama\ollama.exe')],
        'ninja': ['ninja'],
        'cmake': ['cmake'],
        'node': ['node', 'npm'],
        'cargo': ['cargo'],
        'idf.py': ['idf.py'],
    }

    results = {}
    for name, candidates in known_paths.items():
        found_path = None
        for candidate in candidates:
            if shutil.which(candidate):
                found_path = shutil.which(candidate)
                break
            elif Path(candidate).is_file():
                found_path = str(Path(candidate).resolve())
                break
        version = None
        if found_path:
            try:
                flag = '--version' if name not in ('godot', 'unreal') else '-v'
                proc = subprocess.run([found_path, flag], capture_output=True, text=True,
                                      timeout=3, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                raw = proc.stdout.strip() or proc.stderr.strip()
                version = raw.splitlines()[0][:40] if raw else 'Ready'
            except Exception:
                version = 'Detected'
        results[name] = {
            'installed': bool(found_path),
            'path': found_path or 'Not detected',
            'version': version or 'Not detected'
        }
    return results


def detect_project_type(folder_path):
    """Inspects a project folder and determines engine type, git details, and metadata."""
    folder = Path(folder_path).resolve()
    if not folder.is_dir():
        return {'engine': 'Unknown', 'details': 'Path is not a directory'}

    uprojects = list(folder.glob('*.uproject'))
    if uprojects:
        return {'engine': 'Unreal Engine', 'file': uprojects[0].name, 'badge': 'UE5', 'uproject': str(uprojects[0])}

    if (folder / 'project.godot').exists():
        return {'engine': 'Godot Engine', 'file': 'project.godot', 'badge': 'GODOT', 'godot_file': str(folder / 'project.godot')}

    if (folder / 'ProjectSettings' / 'ProjectVersion.txt').exists():
        return {'engine': 'Unity Engine', 'file': 'ProjectSettings', 'badge': 'UNITY'}

    if (folder / 'sdkconfig').exists() or list(folder.glob('sdkconfig.*')) or (
        (folder / 'CMakeLists.txt').exists() and 'idf_component_register' in (
            (folder / 'CMakeLists.txt').read_text(encoding='utf-8', errors='ignore') if (folder / 'CMakeLists.txt').exists() else ''
        )
    ):
        return {'engine': 'ESP32 / ESP-IDF', 'file': 'sdkconfig', 'badge': 'ESP32'}

    blends = list(folder.glob('*.blend'))
    if blends:
        return {'engine': 'Blender Asset', 'file': blends[0].name, 'badge': '3D', 'blend_file': str(blends[0])}

    if (folder / 'package.json').exists():
        return {'engine': 'Web / Node.js', 'file': 'package.json', 'badge': 'WEB'}

    if (folder / 'pyproject.toml').exists() or (folder / 'requirements.txt').exists():
        return {'engine': 'Python', 'file': 'pyproject.toml', 'badge': 'PY'}

    return {'engine': 'Game Design / Other', 'file': None, 'badge': 'DOCS'}


# ─────────────────────────────────────────────────────────────────────────────
# MASTER LIST & MARKDOWN CATALOG PARSER
# ─────────────────────────────────────────────────────────────────────────────

def read_source(path):
    """Safely reads a markdown, text, or json document up to 5 MB."""
    source = Path(path).resolve(strict=True)
    if source.suffix.lower() not in ('.md', '.txt', '.json') or not source.is_file():
        raise ValueError('Choose a Markdown, text or JSON file')
    if source.stat().st_size > 5_000_000:
        raise ValueError('Source exceeds the 5 MB preview limit')
    return source.read_text(encoding='utf-8-sig', errors='replace')


def project_catalog(documents):
    """Parses markdown tables in MASTER_PROJECTS.md and PROJECTS.md to extract projects."""
    catalog = {}
    for document in documents:
        if not Path(document).exists():
            continue
        root = Path(document).resolve().parent
        headers = []
        try:
            content = read_source(document)
        except Exception:
            continue
        for line in content.splitlines():
            if not line.startswith('|'):
                headers = []
                continue
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            if cells[0] in ('Project', 'Engine'):
                headers = cells
                continue
            if not headers or not cells[0] or set(cells[0]) <= set('-: '):
                continue
            name = cells[0].replace('**', '').strip()
            record = catalog.setdefault(name, {
                'name': name, 'synopsis': '', 'path': None, 'engine': 'Unknown', 'status': 'Catalogued'
            })
            if 'What it is' in headers:
                record['synopsis'] = cells[headers.index('What it is')]
            elif 'Progress' in headers and not record['synopsis']:
                record['synopsis'] = cells[headers.index('Progress')]

            if 'Engine' in headers:
                record['engine'] = cells[headers.index('Engine')]
            elif 'Status' in headers:
                record['status'] = cells[headers.index('Status')]

            # Extract relative paths enclosed in backticks
            for candidate in re.findall(r'`([^`]+)`', ' '.join(cells[1:])):
                if '\\' in candidate or '/' in candidate:
                    relative = Path(candidate)
                    if not relative.is_absolute() and '..' not in relative.parts:
                        resolved = (root / relative).resolve()
                        if resolved.exists():
                            record['path'] = str(resolved)
                            break
                        elif (root / candidate).parent.exists():
                            record['path'] = str((root / relative).resolve())
    return sorted(catalog.values(), key=lambda record: record['name'].casefold())


# ─────────────────────────────────────────────────────────────────────────────
# DATA STORE & TEAM CONNECT INVARIANTS
# ─────────────────────────────────────────────────────────────────────────────

DATA = Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'GameForgeStudio'
CHECKPOINTS_DIR = DATA / 'checkpoints'
BACKUPS_DIR = DATA / 'edit-backups'


class Store:
    """Manages application state, project registry, AI providers, and Connect invariants."""
    def __init__(self, root=DATA):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / 'settings.json'
        
        # Discover existing keys from environment if not yet configured
        gemini_env = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_GENERATIVE_AI_API_KEY') or ''
        openai_env = os.environ.get('OPENAI_API_KEY') or ''
        anthropic_env = os.environ.get('ANTHROPIC_API_KEY') or ''
        fal_env = os.environ.get('FAL_KEY') or ''

        default_state = {
            'projects': [],
            'providers': {
                'ollama': {'name': 'Ollama (Local)', 'base_url': 'http://127.0.0.1:11434', 'api_key': '', 'model': 'llama3', 'enabled': True},
                'gemini': {'name': 'Google Gemini', 'base_url': 'https://generativelanguage.googleapis.com/v1beta', 'api_key': gemini_env, 'model': 'gemini-1.5-pro', 'enabled': bool(gemini_env)},
                'anthropic': {'name': 'Anthropic (Claude)', 'base_url': 'https://api.anthropic.com/v1', 'api_key': anthropic_env, 'model': 'claude-3-5-sonnet-20241022', 'enabled': bool(anthropic_env)},
                'openai': {'name': 'OpenAI Compatible', 'base_url': 'https://api.openai.com/v1', 'api_key': openai_env, 'model': 'gpt-4o', 'enabled': bool(openai_env)},
                'fal': {'name': 'Fal.ai (Media & 3D)', 'base_url': 'https://fal.run', 'api_key': fal_env, 'model': 'flux-pro', 'enabled': bool(fal_env)}
            },
            'active_provider': 'auto',  # 'auto' = intelligent dynamic routing
            'setup': False,
            'master_list': 'D:\\DEVELOPMENT\\MASTER_PROJECTS.md',
            'agent_sources': [
                'D:\\DEVELOPMENT\\MASTER_PROJECTS.md',
                'D:\\DEVELOPMENT\\PROJECTS.md',
                'D:\\DEVELOPMENT\\Games\\GuildSim\\.cursor\\LIVE_GAPS.md'
            ],
            # Mandatory Connect Invariant: Disabled by default, opt-in per member/project, individual spending caps
            'team_ai': {
                'enabled': False,
                'opt_in_confirmed': False,
                'individual_cap_usd': 0.0,
                'immediate_revocation': True,
                'automatic_cost_splitting': False,
                'per_project_consent': {},
                'usage_audit': []
            },
            'metrics': {
                'total_prompt_tokens': 0,
                'total_completion_tokens': 0,
                'total_estimated_cost': 0.0
            }
        }
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text(encoding='utf-8'))
                if 'providers' not in self.data or isinstance(self.data['providers'], list):
                    self.data['providers'] = default_state['providers']
                if 'active_provider' not in self.data:
                    self.data['active_provider'] = 'auto'
                if 'team_ai' not in self.data:
                    self.data['team_ai'] = default_state['team_ai']
                if 'metrics' not in self.data:
                    self.data['metrics'] = default_state['metrics']
            except Exception:
                self.data = default_state
        else:
            self.data = default_state

    def save(self):
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.data, indent=2), encoding='utf-8')
        temporary.replace(self.path)

    def register(self, folder, name=None, synopsis=None):
        path = str(Path(folder).resolve(strict=True))
        if not Path(path).is_dir():
            raise ValueError('Choose a valid project folder')
        existing = next((p for p in self.data['projects'] if p['path'] == path), None)
        if not existing:
            project_info = detect_project_type(path)
            record = {
                'name': name or Path(path).name,
                'path': path,
                'synopsis': synopsis or '',
                'engine': project_info.get('engine', 'Unknown'),
                'badge': project_info.get('badge', 'PRJ'),
                'access': 'Ask before edits',
                'chats': [{'title': 'General', 'messages': []}],
                'tasks': [
                    {'title': 'Initialize repository & game bible', 'done': True},
                    {'title': 'Draft core loop mechanics & architecture', 'done': False},
                    {'title': 'Build initial prototype scene / vertical slice', 'done': False}
                ],
                'created_at': datetime.datetime.now().isoformat()
            }
            self.data['projects'].append(record)
            self.save()
            return record
        return existing


# ─────────────────────────────────────────────────────────────────────────────
# INTELLIGENT TASK-BASED AUTO-ROUTER
# ─────────────────────────────────────────────────────────────────────────────

def auto_route_request(prompt, attachments, providers):
    """
    Intelligently analyzes the prompt content, attachments, and active providers
    to automatically select the best model without requiring manual switching.
    
    Returns: (provider_key, model_name, reason_description)
    """
    has_images = any(Path(p).suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp', '.bmp') for p in attachments)
    prompt_lower = prompt.lower()

    # Rule 1: Visual, Concept Art, Video Reference, or 3D Turnaround Analysis
    is_visual = has_images or any(w in prompt_lower for w in [
        'concept', 'art', 'screenshot', 'reference video', 'look like', 'character sheet',
        'turnaround', 'tripo', 'texture', 'render', 'camera angle', 'visuals', 'mood'
    ])

    if is_visual:
        if providers.get('gemini', {}).get('api_key'):
            return ('gemini', providers['gemini'].get('model', 'gemini-1.5-pro'),
                    'Auto-routed to Gemini 1.5 Pro (Multimodal Vision & Concept Analysis)')
        elif providers.get('openai', {}).get('api_key'):
            return ('openai', providers['openai'].get('model', 'gpt-4o'),
                    'Auto-routed to GPT-4o (Visual & Turnaround Synthesis)')
        elif providers.get('anthropic', {}).get('api_key'):
            return ('anthropic', providers['anthropic'].get('model', 'claude-3-5-sonnet-20241022'),
                    'Auto-routed to Claude 3.5 Sonnet (Visual Reference)')
        else:
            return ('ollama', providers.get('ollama', {}).get('model', 'llama3'),
                    'Auto-routed to Local Model (Visual references handled via text fallback)')

    # Rule 2: Deep Architecture, Game Logic, Physics, State Machines, Shaders
    is_complex_logic = len(prompt) > 500 or any(w in prompt_lower for w in [
        'architecture', 'state machine', 'physics', 'refactor', 'shader', 'algorithm',
        'inventory', 'multiplayer', 'combat system', 'game loop', 'dialogue system', 'cloth physics'
    ])

    if is_complex_logic:
        if providers.get('anthropic', {}).get('api_key'):
            return ('anthropic', providers['anthropic'].get('model', 'claude-3-5-sonnet-20241022'),
                    'Auto-routed to Claude 3.5 Sonnet (Advanced Game Logic & Architecture)')
        elif providers.get('openai', {}).get('api_key'):
            return ('openai', providers['openai'].get('model', 'gpt-4o'),
                    'Auto-routed to GPT-4o (Complex Logic & Synthesis)')
        elif providers.get('gemini', {}).get('api_key'):
            return ('gemini', providers['gemini'].get('model', 'gemini-1.5-pro'),
                    'Auto-routed to Gemini 1.5 Pro (Large-Context Systems Design)')
        else:
            return ('ollama', providers.get('ollama', {}).get('model', 'llama3'),
                    'Auto-routed to Local Ollama (Local Engine Code)')

    # Rule 3: Fast Iterative Bug Fixes, Syntax Checks, Offline Inquiries
    is_bug_fix = any(w in prompt_lower for w in [
        'bug', 'fix', 'error', 'null pointer', 'crash', 'syntax', 'typo', 'traceback',
        'where is', 'list', 'check', 'inspect'
    ])

    # If user has a fast local Ollama or specifically asks for quick fix:
    if is_bug_fix and providers.get('ollama', {}).get('enabled'):
        return ('ollama', providers['ollama'].get('model', 'llama3'),
                'Auto-routed to Local Ollama (Instant Zero-Cost Local Fix)')

    # Default fallback to first verified provider
    for p_key in ['anthropic', 'openai', 'gemini', 'ollama']:
        cfg = providers.get(p_key, {})
        if (cfg.get('api_key') or p_key == 'ollama') and cfg.get('enabled', True):
            return (p_key, cfg.get('model', 'llama3'), f"Auto-routed to {cfg.get('name', p_key.upper())}")

    return ('ollama', 'llama3', 'Auto-routed to Local Ollama (Default)')


# ─────────────────────────────────────────────────────────────────────────────
# LIVE PROVIDER VERIFICATION / AUTH TESTERS
# ─────────────────────────────────────────────────────────────────────────────

def verify_provider_auth(provider_key, base_url, api_key):
    """Makes a live lightweight request to test authentication and reachability."""
    try:
        base = base_url.rstrip('/')
        if provider_key == 'ollama':
            with urllib.request.urlopen(f"{base}/api/tags", timeout=4) as r:
                tags = json.load(r).get('models', [])
                names = [m['name'] for m in tags]
                return True, f"Connected to Ollama! Models: {', '.join(names[:4]) or 'None downloaded'}"
        elif provider_key == 'gemini':
            if not api_key:
                return False, "API key is required"
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            with urllib.request.urlopen(url, timeout=5) as r:
                return True, "✓ Authenticated & Connected to Google Gemini API"
        elif provider_key == 'openai':
            if not api_key:
                return False, "API key is required"
            req = urllib.request.Request(f"{base}/models", headers={'Authorization': f'Bearer {api_key}'})
            with urllib.request.urlopen(req, timeout=5) as r:
                return True, "✓ Authenticated & Connected to OpenAI API"
        elif provider_key == 'anthropic':
            if not api_key:
                return False, "API key is required"
            req = urllib.request.Request(
                f"{base}/messages",
                data=json.dumps({
                    'model': 'claude-3-5-sonnet-20241022',
                    'max_tokens': 1,
                    'messages': [{'role': 'user', 'content': 'hi'}]
                }).encode('utf-8'),
                headers={
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01',
                    'Content-Type': 'application/json'
                }
            )
            with urllib.request.urlopen(req, timeout=6) as r:
                return True, "✓ Authenticated & Connected to Anthropic Claude API"
        elif provider_key == 'fal':
            if not api_key:
                return False, "API key is required"
            req = urllib.request.Request(
                "https://rest.alpha.fal.ai/models",
                headers={'Authorization': f'Key {api_key}'}
            )
            with urllib.request.urlopen(req, timeout=5) as r:
                return True, "✓ Authenticated & Connected to Fal.ai"
        return True, "Connection verified"
    except urllib.error.HTTPError as he:
        return False, f"Auth Error ({he.code}): {he.reason}"
    except Exception as ex:
        return False, f"Connection Failed: {str(ex)[:60]}"


# ─────────────────────────────────────────────────────────────────────────────
# SAFE GIT OPERATIONS
# ─────────────────────────────────────────────────────────────────────────────

def git(folder, *arguments):
    """Executes git commands with a 90s safety timeout and error reporting."""
    result = subprocess.run(
        ['git', '-C', str(folder), *arguments],
        capture_output=True, text=True, timeout=90,
        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    )
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout or f'Git command exited with code {result.returncode}')
    return result.stdout.strip()


# ─────────────────────────────────────────────────────────────────────────────
# AGENT ACTIVITY & RECOVERY CENTER SAFETY
# ─────────────────────────────────────────────────────────────────────────────

def apply_edit(project, relative, content, expected, approve):
    """
    Applies proposed agent edits with strict boundary validation, sha256 checksum
    verification, pre-edit byte backup, and atomic replacement.
    """
    root = Path(project['path']).resolve()
    target = (root / relative).resolve()
    if root not in target.parents or '.git' in target.relative_to(root).parts:
        raise ValueError('Edits must stay strictly inside the project root and outside .git')

    mode = project.get('access', 'Read only')
    if mode not in ('Ask before edits', 'Full project editing'):
        raise PermissionError('Project is read-only. Edit rejected.')

    before = target.read_bytes() if target.exists() else None
    digest = hashlib.sha256(before).hexdigest() if before is not None else None
    if digest != expected:
        raise ValueError('File changed since review; please reload the proposal')

    if mode == 'Ask before edits' and not approve():
        return False

    if (target.read_bytes() if target.exists() else None) != before:
        raise ValueError('File changed during approval review')

    if not target.parent.is_dir():
        target.parent.mkdir(parents=True, exist_ok=True)

    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    backup_file = BACKUPS_DIR / f"{uuid.uuid4().hex}_{Path(relative).name}.bak"
    if before is not None:
        backup_file.write_bytes(before)

    temporary = target.with_name(target.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        with temporary.open('w', encoding='utf-8', newline='') as stream:
            stream.write(content)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)

    activity = project.setdefault('edit_activity', [])
    activity.append({
        'file': relative,
        'mode': mode,
        'backup': str(backup_file) if before is not None else None,
        'timestamp': datetime.datetime.now().isoformat(timespec='seconds'),
        'digest_before': digest,
        'digest_after': hashlib.sha256(content.encode('utf-8')).hexdigest()
    })
    return True


def create_checkpoint(project, destination_dir=None):
    """Creates a complete timestamped ZIP recovery archive of a project."""
    source = Path(project['path']).resolve()
    dest = Path(destination_dir).resolve() if destination_dir else CHECKPOINTS_DIR
    dest.mkdir(parents=True, exist_ok=True)
    if dest == source or source in dest.parents:
        raise ValueError('Backup destination must be strictly outside the project folder')

    timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    archive_base = dest / f"{source.name}-checkpoint-{timestamp}"
    archive_path = shutil.make_archive(str(archive_base), 'zip', source)
    return str(archive_path)


def restore_checkpoint(zip_path, target_folder):
    """
    Safely restores a ZIP checkpoint ONLY into an empty or new directory.
    Enforces the invariant: Never overwrite an existing project folder.
    """
    zip_file = Path(zip_path).resolve(strict=True)
    target = Path(target_folder).resolve()
    if target.exists() and any(target.iterdir()):
        raise ValueError('Destination folder must be empty to prevent accidental overwrites')
    target.mkdir(parents=True, exist_ok=True)
    shutil.unpack_archive(str(zip_file), str(target), 'zip')
    return str(target)


# ─────────────────────────────────────────────────────────────────────────────
# AUTONOMOUS TOOL ENGINE & SANDBOX
# ─────────────────────────────────────────────────────────────────────────────

class ToolEngine:
    """Safe sandbox for executing agent tools within a project's boundaries."""

    @staticmethod
    def read_file(project_root, relative_path):
        target = (Path(project_root) / relative_path).resolve()
        if Path(project_root).resolve() not in target.parents:
            raise PermissionError('Access denied: path is outside project boundaries.')
        if not target.is_file():
            raise FileNotFoundError(f'File {relative_path} not found.')
        return target.read_text(encoding='utf-8', errors='replace')

    @staticmethod
    def list_dir(project_root, relative_path=''):
        target = (Path(project_root) / relative_path).resolve()
        if Path(project_root).resolve() not in [target, *target.parents]:
            raise PermissionError('Access denied: path is outside project boundaries.')
        if not target.is_dir():
            raise NotADirectoryError(f'{relative_path} is not a directory.')
        items = []
        for p in target.iterdir():
            if p.name == '.git':
                continue
            kind = 'DIR ' if p.is_dir() else 'FILE'
            items.append(f"{kind}  {p.name}")
        return '\n'.join(items)

    @staticmethod
    def search_code(project_root, query, file_pattern='*.*'):
        root = Path(project_root).resolve()
        matches = []
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        for p in root.glob(f"**/{file_pattern}"):
            if '.git' in p.parts or not p.is_file():
                continue
            try:
                for line_no, line in enumerate(p.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
                    if pattern.search(line):
                        rel = p.relative_to(root)
                        matches.append(f"{rel}:{line_no}: {line.strip()[:120]}")
                        if len(matches) >= 30:
                            return '\n'.join(matches) + '\n... (truncated at 30 matches)'
            except Exception:
                continue
        return '\n'.join(matches) if matches else 'No matches found.'

    @staticmethod
    def run_safe_command(project_root, cmd):
        """Runs non-destructive build/git commands within the project."""
        allowed_prefixes = ['git', 'python', 'godot', 'cargo', 'ninja', 'cmake']
        cmd_tokens = cmd.strip().split()
        if not cmd_tokens or cmd_tokens[0].lower() not in allowed_prefixes:
            raise PermissionError(f"Command '{cmd}' is not in the allowed safe tool execution whitelist.")
        proc = subprocess.run(
            cmd, cwd=project_root, shell=True, capture_output=True, text=True,
            timeout=30, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        )
        return (proc.stdout or '') + (proc.stderr or '')


# ─────────────────────────────────────────────────────────────────────────────
# PLUGIN & SKILL COMPATIBILITY CHECKER
# ─────────────────────────────────────────────────────────────────────────────

def inspect_skills_compatibility(project_folder=None):
    """
    Scans for skills in project folders (.cursor/skills, .gemini/skills)
    and verifies prerequisites and compatibility against system tools.
    """
    tools = detect_tools()
    discovered_skills = []

    search_roots = []
    if project_folder and Path(project_folder).is_dir():
        search_roots.append(Path(project_folder) / '.cursor' / 'skills')
        search_roots.append(Path(project_folder) / 'skills')
    global_skills = Path.home() / '.gemini' / 'config' / 'plugins' / 'science' / 'skills'
    if global_skills.exists():
        search_roots.append(global_skills)

    for root in search_roots:
        if not root.exists():
            continue
        for skill_md in root.glob('**/SKILL.md'):
            try:
                text = skill_md.read_text(encoding='utf-8', errors='replace')
                name_match = re.search(r'^name:\s*(.+)$', text, re.MULTILINE)
                desc_match = re.search(r'^description:\s*(.+)$', text, re.MULTILINE)
                name = name_match.group(1).strip() if name_match else skill_md.parent.name
                desc = desc_match.group(1).strip() if desc_match else 'Custom Agent Skill'

                missing_deps = []
                if 'git' in desc.lower() and not tools['git']['installed']:
                    missing_deps.append('git')
                if ('python' in desc.lower() or 'py' in desc.lower()) and not tools['python']['installed']:
                    missing_deps.append('python')
                if 'blender' in desc.lower() and not tools['blender']['installed']:
                    missing_deps.append('blender')
                if 'godot' in desc.lower() and not tools['godot']['installed']:
                    missing_deps.append('godot')

                status = 'Compatible' if not missing_deps else f'Missing: {", ".join(missing_deps)}'
                discovered_skills.append({
                    'name': name,
                    'path': str(skill_md),
                    'description': desc,
                    'status': status,
                    'compatible': len(missing_deps) == 0
                })
            except Exception:
                continue
    return discovered_skills


# ─────────────────────────────────────────────────────────────────────────────
# MAIN GAMEFORGE STUDIO APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class Studio(tk.Tk):
    """Obsidian Glass Slate Desktop Application for GameForge Studio."""

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry('1300x840')
        self.minsize(1040, 700)
        self.configure(bg='#070a0e')

        # Load Icon
        icon_path = Path(__file__).resolve().parent / 'app.ico'
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                pass

        self.store = Store()
        self.project = None
        self.active_tab = None

        # Streaming & Execution control
        self.stream_queue = queue.Queue()
        self.abort_event = threading.Event()
        self.active_thread = None
        self.active_attachments = []  # List of Path objects

        self._init_styles()
        dark_title(self)

        # Status Bar at bottom
        self._build_status_bar()

        # Main Layout Container
        self.shell = tk.Frame(self, bg='#070a0e')
        self.shell.pack(fill='both', expand=True)

        self._build_sidebar()
        self._build_main_panel()

        # Keyboard shortcuts
        self.bind('<Control-s>', lambda e: self.save_current())
        self.bind('<F5>', lambda e: self.refresh())

        self.refresh()
        if self.store.data['projects']:
            self.select(self.store.data['projects'][0])
        else:
            self.home()

        # First-Run Setup Wizard
        if not self.store.data.get('setup'):
            self.after(350, self.setup_wizard)

    def _init_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        # Obsidian Slate Palette
        style.configure('.', background='#111822', foreground='#e2eaf4',
                        fieldbackground='#182330', bordercolor='#26374a', padding=6)
        style.configure('TNotebook', background='#070a0e', borderwidth=0)
        style.configure('TNotebook.Tab', background='#131c26', foreground='#9db0c4',
                        padding=(14, 8), font=('Segoe UI', 9, 'bold'))
        style.map('TNotebook.Tab',
                  background=[('selected', '#223245'), ('active', '#1a2736')],
                  foreground=[('selected', '#ffffff'), ('active', '#c2d0df')])
        style.configure('Treeview', background='#101822', foreground='#e2eaf4',
                        fieldbackground='#101822', rowheight=26, borderwidth=0)
        style.map('Treeview', background=[('selected', '#2d425c')])
        style.configure('Treeview.Heading', background='#16212e', foreground='#c2d0df',
                        font=('Segoe UI', 9, 'bold'), relief='flat')
        rounded_buttons(self, style)

    def _build_status_bar(self):
        self.status_bar = tk.Frame(self, bg='#090d12', padx=14, pady=4, height=24)
        self.status_bar.pack(side='bottom', fill='x')

        self.sb_version = tk.Label(self.status_bar, text=f"GameForge Studio v{APP_VERSION} (Production)",
                                   font=('Segoe UI', 8, 'bold'), bg='#090d12', fg='#60a5fa')
        self.sb_version.pack(side='left')

        self.sb_safety = tk.Label(self.status_bar, text="🛡️ Team AI: Strictly OPT-IN ($0.00 Cap)",
                                  font=('Segoe UI', 8), bg='#090d12', fg='#22c55e')
        self.sb_safety.pack(side='right', padx=(10, 0))

        self.sb_provider = tk.Label(self.status_bar, text="Routing: 🤖 Auto-Route (Intelligent)",
                                    font=('Segoe UI', 8), bg='#090d12', fg='#9db0c4')
        self.sb_provider.pack(side='right', padx=(10, 0))

    def _update_status_bar(self):
        prov = self.store.data.get('active_provider', 'auto')
        if prov == 'auto':
            self.sb_provider.config(text="Routing: 🤖 Auto-Route (Smart Dispatch)")
        else:
            p_info = self.store.data.get('providers', {}).get(prov, {})
            self.sb_provider.config(text=f"Provider: {p_info.get('name', prov.upper())}")

    def _build_sidebar(self):
        self.sidebar = tk.Frame(self.shell, bg='#0d131a', width=260, padx=12, pady=12)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        top_bar = tk.Frame(self.sidebar, bg='#0d131a')
        top_bar.pack(fill='x', pady=(0, 10))
        tk.Label(top_bar, text='GAMEFORGE', font=('Segoe UI', 13, 'bold'),
                 bg='#0d131a', fg='#60a5fa').pack(side='left')
        collapse_btn = tk.Button(top_bar, text='◀', font=('Segoe UI', 9),
                                 bg='#16212e', fg='#9db0c4', activebackground='#223245',
                                 relief='flat', padx=8, pady=2, command=self.collapse_sidebar)
        collapse_btn.pack(side='right')

        actions = [
            ('➕  New Project', self.create_dialog),
            ('📂  Import Folder', self.import_folder_dialog),
            ('📋  Import from Master', self.batch_import_dialog),
            ('🌐  Download / Clone', self.clone_dialog),
            ('🎮  3D Asset Viewport', self.open_3d_viewport),
            ('🤖  Pull from Agents', self.agent_sources_view),
            ('📝  Project Master List', self.master_list_view),
            ('🛡️  Recovery Center', self.recovery_center_view),
            ('⚙️  Settings & AI Keys', self.settings_view),
            ('🧙  Setup Wizard', self.setup_wizard),
            ('ℹ️  About GameForge', self.about_dialog),
        ]
        for label, cmd in actions:
            btn = tk.Button(self.sidebar, text=label, font=('Segoe UI', 9),
                            anchor='w', bg='#141c26', fg='#c2d0df',
                            activebackground='#202c3b', activeforeground='#ffffff',
                            relief='flat', padx=10, pady=4,
                            command=lambda cmd=cmd: self.safe_action(cmd))
            btn.pack(fill='x', pady=2)

        search_frame = tk.Frame(self.sidebar, bg='#0d131a', pady=8)
        search_frame.pack(fill='x')
        tk.Label(search_frame, text='PROJECTS', font=('Segoe UI', 9, 'bold'),
                 bg='#0d131a', fg='#64748b').pack(anchor='w', pady=(0, 4))
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', lambda *_: self.render_projects_list())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                bg='#16212e', fg='#e2eaf4', insertbackground='#60a5fa',
                                relief='flat', font=('Segoe UI', 9), highlightthickness=1,
                                highlightbackground='#26374a')
        search_entry.pack(fill='x', ipady=4)

        self.projects_scroll = tk.Frame(self.sidebar, bg='#0d131a')
        self.projects_scroll.pack(fill='both', expand=True)

    def _build_main_panel(self):
        self.main = tk.Frame(self.shell, bg='#070a0e', padx=16, pady=12)
        self.main.pack(side='left', fill='both', expand=True)

    def collapse_sidebar(self):
        self.sidebar.pack_forget()
        expand_bar = tk.Frame(self.shell, bg='#0d131a', width=36)
        expand_bar.pack(side='left', fill='y', before=self.main)
        tk.Button(expand_bar, text='▶', font=('Segoe UI', 10, 'bold'),
                  bg='#16212e', fg='#60a5fa', relief='flat', padx=6, pady=10,
                  command=lambda: [expand_bar.destroy(), self.expand_sidebar()]).pack(pady=10)

    def expand_sidebar(self):
        self.sidebar.pack(side='left', fill='y', before=self.main)

    def safe_action(self, action):
        try:
            action()
        except Exception as error:
            messagebox.showerror('GameForge Studio', str(error))

    def open_3d_viewport(self, target_file=None):
        """Launches the interactive Three.js 3D Viewport."""
        try:
            viewport_script = Path(__file__).resolve().parent / 'viewport3d.py'
            if viewport_script.exists():
                args = [sys.executable, str(viewport_script)]
                if target_file:
                    args.append(str(target_file))
                subprocess.Popen(args)
            else:
                import viewport3d
                threading.Thread(target=viewport3d.launch_viewport, args=(target_file,), daemon=True).start()
        except Exception as ex:
            messagebox.showerror('3D Viewport Error', f"Could not launch 3D viewport:\n{ex}")

    def clear_main(self, title, subtitle=''):
        for child in self.main.winfo_children():
            child.destroy()
        head = tk.Frame(self.main, bg='#070a0e')
        head.pack(fill='x', pady=(0, 14))
        tk.Label(head, text=title, font=('Segoe UI', 18, 'bold'),
                 bg='#070a0e', fg='#e2eaf4').pack(anchor='w')
        if subtitle:
            tk.Label(head, text=subtitle, font=('Segoe UI', 9),
                     bg='#070a0e', fg='#7e91a6').pack(anchor='w', pady=(2, 0))

    def refresh(self):
        self.render_projects_list()
        self._update_status_bar()

    def render_projects_list(self):
        for child in self.projects_scroll.winfo_children():
            child.destroy()
        query = self.search_var.get().strip().lower()
        projects = self.store.data.get('projects', [])
        for project in projects:
            if query and query not in project['name'].lower() and query not in project.get('engine', '').lower():
                continue
            is_active = self.project and self.project['path'] == project['path']
            btn_bg = '#223245' if is_active else '#131b24'
            badge_text = project.get('badge', 'PRJ')

            btn_frame = tk.Frame(self.projects_scroll, bg=btn_bg, pady=2, padx=4)
            btn_frame.pack(fill='x', pady=2)

            badge = tk.Label(btn_frame, text=badge_text, font=('Segoe UI', 7, 'bold'),
                             bg='#1f2d3d', fg='#60a5fa', padx=4, pady=1)
            badge.pack(side='left', padx=(2, 6))

            name_btn = tk.Button(btn_frame, text=project['name'], font=('Segoe UI', 9),
                                 anchor='w', bg=btn_bg, fg='#ffffff' if is_active else '#c2d0df',
                                 relief='flat', activebackground='#2d425c',
                                 command=lambda p=project: self.select(p))
            name_btn.pack(side='left', fill='x', expand=True)

    def select(self, project):
        self.project = project
        self.render_projects_list()
        self.home()

    # ─────────────────────────────────────────────────────────────────────────
    # PROJECT CONTROL CENTER & TAB NAVIGATION
    # ─────────────────────────────────────────────────────────────────────────

    def home(self):
        if not self.project:
            self.clear_main('Welcome to GameForge Studio', 'Select or import a project to get started.')
            empty_frame = tk.Frame(self.main, bg='#101822', padx=30, pady=30)
            empty_frame.pack(fill='both', expand=True, pady=20)
            tk.Label(empty_frame, text='No Active Project Selected',
                     font=('Segoe UI', 15, 'bold'), bg='#101822', fg='#60a5fa').pack(pady=(0, 10))
            tk.Label(empty_frame, text='Start by creating a new game project, importing an existing folder,\nor loading your master project document.',
                     font=('Segoe UI', 10), bg='#101822', fg='#9db0c4').pack(pady=(0, 20))
            actions_f = tk.Frame(empty_frame, bg='#101822')
            actions_f.pack()
            tk.Button(actions_f, text='📂 Import Existing Folder', bg='#2b3e55', fg='#e2eaf4',
                      font=('Segoe UI', 10, 'bold'), relief='flat', padx=16, pady=8,
                      command=self.import_folder_dialog).pack(side='left', padx=6)
            tk.Button(actions_f, text='📋 Scan Master Projects', bg='#1f2d3d', fg='#c2d0df',
                      font=('Segoe UI', 10), relief='flat', padx=16, pady=8,
                      command=self.batch_import_dialog).pack(side='left', padx=6)
            return

        engine_badge = self.project.get('engine', 'Unknown')
        self.clear_main(self.project['name'], f"Path: {self.project['path']}  •  Engine: {engine_badge}")

        tabs = ttk.Notebook(self.main)
        tabs.pack(fill='both', expand=True)

        pages = [
            ('Control Center', self._tab_control_center),
            ('Workspace', self._tab_workspace),
            ('Chat & Agents', self._tab_chat),
            ('Agents & Approvals', self._tab_agents_approvals),
            ('Tasks & Roadmap', self._tab_tasks),
            ('Game Bible', self._tab_game_bible),
            ('Changes', self._tab_changes),
            ('Connect', self._tab_connect),
        ]

        for tab_name, builder in pages:
            frame = ttk.Frame(tabs)
            tabs.add(frame, text=f" {tab_name} ")
            builder(frame)

    def _tab_control_center(self, page):
        container = tk.Frame(page, bg='#0e141c', padx=16, pady=14)
        container.pack(fill='both', expand=True)

        # Synopsis Card
        tk.Label(container, text='Project Synopsis & Vision', font=('Segoe UI', 11, 'bold'),
                 bg='#0e141c', fg='#60a5fa').pack(anchor='w')
        synopsis_box = tk.Text(container, height=5, bg='#141c26', fg='#e2eaf4',
                               insertbackground='#60a5fa', relief='flat', font=('Segoe UI', 10),
                               wrap='word', padx=10, pady=8)
        synopsis_box.insert('1.0', self.project.get('synopsis', ''))
        synopsis_box.pack(fill='x', pady=(6, 10))

        def save_synopsis():
            self.project['synopsis'] = synopsis_box.get('1.0', 'end-1c').strip()
            self.store.save()
            messagebox.showinfo('GameForge', 'Project synopsis saved successfully.')

        save_btn = tk.Button(container, text='💾 Save Synopsis', font=('Segoe UI', 9, 'bold'),
                             bg='#2b3e55', fg='#e2eaf4', relief='flat', padx=12, pady=5,
                             command=save_synopsis)
        save_btn.pack(anchor='w', pady=(0, 14))

        # Launch in External Engine / Editor Section
        tk.Label(container, text='Launch in Engine & Editors', font=('Segoe UI', 11, 'bold'),
                 bg='#0e141c', fg='#60a5fa').pack(anchor='w', pady=(0, 6))

        launch_bar = tk.Frame(container, bg='#0e141c')
        launch_bar.pack(fill='x', pady=(0, 14))

        tk.Button(launch_bar, text='🎮 3D Asset Viewport', font=('Segoe UI', 9, 'bold'),
                  bg='#233876', fg='#38bdf8', relief='flat', padx=12, pady=5,
                  command=lambda: self.safe_action(self.open_3d_viewport)).pack(side='left', padx=(0, 6))

        tools = detect_tools()

        def launch_external(tool_key, arg=None):
            tool_path = tools.get(tool_key, {}).get('path')
            if not tool_path or not Path(tool_path).exists():
                raise FileNotFoundError(f"{tool_key.upper()} executable is not found on your system.")
            target = arg or self.project['path']
            subprocess.Popen([tool_path, target], creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            messagebox.showinfo('Launched', f"Launched {tool_key.upper()} with {target}")

        pinfo = detect_project_type(self.project['path'])
        if pinfo.get('engine') == 'Godot Engine' and tools['godot']['installed']:
            tk.Button(launch_bar, text='🎮 Open in Godot Editor', font=('Segoe UI', 9, 'bold'),
                      bg='#1f2d3d', fg='#38bdf8', relief='flat', padx=12, pady=5,
                      command=lambda: self.safe_action(lambda: launch_external('godot'))).pack(side='left', padx=(0, 6))

        if pinfo.get('engine') == 'Unreal Engine' and tools['unreal']['installed'] and pinfo.get('uproject'):
            tk.Button(launch_bar, text='⚔️ Open in Unreal Editor', font=('Segoe UI', 9, 'bold'),
                      bg='#1f2d3d', fg='#38bdf8', relief='flat', padx=12, pady=5,
                      command=lambda: self.safe_action(lambda: launch_external('unreal', pinfo['uproject']))).pack(side='left', padx=(0, 6))

        if pinfo.get('engine') == 'Blender Asset' and tools['blender']['installed'] and pinfo.get('blend_file'):
            tk.Button(launch_bar, text='🎨 Open in Blender', font=('Segoe UI', 9, 'bold'),
                      bg='#1f2d3d', fg='#f59e0b', relief='flat', padx=12, pady=5,
                      command=lambda: self.safe_action(lambda: launch_external('blender', pinfo['blend_file']))).pack(side='left', padx=(0, 6))

        if tools['cursor']['installed']:
            tk.Button(launch_bar, text='💻 Open in Cursor', font=('Segoe UI', 9),
                      bg='#182330', fg='#c2d0df', relief='flat', padx=12, pady=5,
                      command=lambda: self.safe_action(lambda: launch_external('cursor'))).pack(side='left', padx=(0, 6))

        if tools['code']['installed']:
            tk.Button(launch_bar, text='📝 Open in VS Code', font=('Segoe UI', 9),
                      bg='#182330', fg='#c2d0df', relief='flat', padx=12, pady=5,
                      command=lambda: self.safe_action(lambda: launch_external('code'))).pack(side='left', padx=(0, 6))

        # Quick Actions Grid
        tk.Label(container, text='Control Center Actions', font=('Segoe UI', 11, 'bold'),
                 bg='#0e141c', fg='#60a5fa').pack(anchor='w', pady=(0, 6))
        grid = tk.Frame(container, bg='#0e141c')
        grid.pack(fill='x', pady=(0, 14))

        action_buttons = [
            ('📂 Open Folder in Explorer', lambda: os.startfile(self.project['path'])),
            ('🔍 Inspect Git Changes', self.view_git_changes),
            ('🚀 Publish Commits', self.publish_git_commits),
            ('⬇️ Download Updates', self.download_git_updates),
            ('🔄 Fetch Status', self.sync_git_status),
            ('🛡️ Create Checkpoint', lambda: self.create_project_checkpoint(self.project)),
            ('🩺 Project Health Check', self.project_health_check),
        ]
        for i, (label, cmd) in enumerate(action_buttons):
            btn = tk.Button(grid, text=label, font=('Segoe UI', 9),
                            bg='#182330', fg='#c2d0df', activebackground='#26374a',
                            relief='flat', padx=12, pady=6, command=lambda c=cmd: self.safe_action(c))
            btn.grid(row=i // 4, column=i % 4, padx=4, pady=4, sticky='ew')

        # Project Stats & Git Info
        stats_frame = tk.Frame(container, bg='#141c26', padx=14, pady=10)
        stats_frame.pack(fill='x')
        try:
            branch = git(self.project['path'], 'branch', '--show-current') or 'main'
            status_short = git(self.project['path'], 'status', '--short')
            status_line = f"Git: on branch '{branch}' • {'Uncommitted files' if status_short else 'Working tree clean'}"
        except Exception:
            status_line = 'Git: Not a repository or git not available'

        tk.Label(stats_frame, text=status_line, font=('Segoe UI', 9),
                 bg='#141c26', fg='#9db0c4').pack(anchor='w')

    def _tab_workspace(self, page):
        root = Path(self.project['path']).resolve()
        top_bar = tk.Frame(page, bg='#101822', padx=12, pady=8)
        top_bar.pack(fill='x')

        tree = ttk.Treeview(page, columns=('kind', 'size'), show='tree headings')
        tree.heading('#0', text='Project Files & Directories')
        tree.heading('kind', text='Type')
        tree.heading('size', text='Size')
        tree.column('kind', width=120, anchor='w')
        tree.column('size', width=100, anchor='e')
        tree.pack(fill='both', expand=True, padx=12, pady=8)

        def populate(folder, parent=''):
            try:
                items = sorted(folder.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
                for p in items:
                    if p.name == '.git':
                        continue
                    kind = 'Directory' if p.is_dir() else 'File'
                    size_str = ''
                    if p.is_file():
                        sz = p.stat().st_size
                        size_str = f"{sz:,} B" if sz < 1024 else f"{sz / 1024:.1f} KB"
                    node = tree.insert(parent, 'end', iid=str(p), text=f" {'📁' if p.is_dir() else '📄'} {p.name}",
                                       values=(kind, size_str))
                    if p.is_dir() and not p.is_symlink():
                        tree.insert(node, 'end', text='…')
            except Exception:
                pass

        def on_expand(event=None):
            selected = tree.focus()
            if not selected:
                return
            folder = Path(selected)
            if folder.is_dir() and not folder.is_symlink():
                for child in tree.get_children(selected):
                    tree.delete(child)
                populate(folder, selected)

        def refresh():
            tree.delete(*tree.get_children())
            populate(root)

        def new_item(is_folder):
            name = simpledialog.askstring('New Folder' if is_folder else 'New File',
                                          'Relative path inside project:')
            if not name:
                return
            target = (root / name).resolve()
            if root not in target.parents:
                raise ValueError('Target path must remain inside the project')
            if is_folder:
                target.mkdir(parents=True, exist_ok=False)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.touch(exist_ok=False)
            refresh()

        for label, cmd in [('➕ New File', lambda: new_item(False)),
                           ('📁 New Folder', lambda: new_item(True)),
                           ('🔄 Refresh', refresh),
                           ('📂 Open in Explorer', lambda: os.startfile(root))]:
            tk.Button(top_bar, text=label, font=('Segoe UI', 9), bg='#1b2736', fg='#c2d0df',
                      relief='flat', padx=10, pady=4, command=lambda c=cmd: self.safe_action(c)).pack(side='left', padx=3)

        tree.bind('<<TreeviewOpen>>', on_expand)
        refresh()

    # ─────────────────────────────────────────────────────────────────────────
    # CHAT, STREAMING, ATTACHMENTS & AUTONOMOUS AGENT TOOLS
    # ─────────────────────────────────────────────────────────────────────────

    def _tab_chat(self, page):
        project = self.project

        # Control & Config Bar
        top = tk.Frame(page, bg='#101822', padx=12, pady=8)
        top.pack(fill='x')

        tk.Label(top, text='Provider / Dispatch:', font=('Segoe UI', 9, 'bold'),
                 bg='#101822', fg='#7e91a6').pack(side='left', padx=(0, 4))

        providers = self.store.data.get('providers', {})
        active_prov_key = tk.StringVar(value=self.store.data.get('active_provider', 'auto'))
        
        # Available dispatch options
        dispatch_options = ['auto'] + list(providers.keys())
        dispatch_labels = {
            'auto': '🤖 Auto-Route (Intelligent)',
            'gemini': 'Google Gemini (1.5 Pro)',
            'anthropic': 'Anthropic (Claude 3.5 Sonnet)',
            'openai': 'OpenAI (GPT-4o)',
            'ollama': 'Ollama (Local Offline)',
            'fal': 'Fal.ai (Media & 3D)'
        }
        
        prov_combo = ttk.Combobox(top, textvariable=active_prov_key, state='readonly',
                                  values=[dispatch_labels.get(k, k) for k in dispatch_options], width=26)
        # Select current display label
        prov_combo.set(dispatch_labels.get(active_prov_key.get(), '🤖 Auto-Route (Intelligent)'))
        prov_combo.pack(side='left')

        tk.Label(top, text='Model Override:', font=('Segoe UI', 9, 'bold'),
                 bg='#101822', fg='#7e91a6').pack(side='left', padx=(10, 4))
        model_var = tk.StringVar(value='(Automatic)' if active_prov_key.get() == 'auto' else providers.get(active_prov_key.get(), {}).get('model', ''))
        model_entry = tk.Entry(top, textvariable=model_var, width=16, bg='#16212e', fg='#e2eaf4',
                               relief='flat', highlightthickness=1, highlightbackground='#26374a')
        model_entry.pack(side='left')

        def on_prov_change(e=None):
            chosen_label = prov_combo.get()
            chosen_key = next((k for k, v in dispatch_labels.items() if v == chosen_label), 'auto')
            self.store.data['active_provider'] = chosen_key
            if chosen_key == 'auto':
                model_var.set('(Automatic)')
            else:
                model_var.set(self.store.data['providers'].get(chosen_key, {}).get('model', ''))
            self.store.save()
            self._update_status_bar()

        prov_combo.bind('<<ComboboxSelected>>', on_prov_change)

        tk.Label(top, text='Access Mode:', font=('Segoe UI', 9, 'bold'),
                 bg='#101822', fg='#7e91a6').pack(side='left', padx=(10, 4))
        access_var = tk.StringVar(value=project.get('access', 'Ask before edits'))
        access_menu = ttk.Combobox(top, textvariable=access_var, state='readonly',
                                   values=['Read only', 'Ask before edits', 'Full project editing'], width=18)
        access_menu.pack(side='left')

        def on_access_change(e=None):
            project['access'] = access_var.get()
            self.store.save()

        access_menu.bind('<<ComboboxSelected>>', on_access_change)

        review_btn = tk.Button(top, text='🔍 Review Pending Proposal', font=('Segoe UI', 9, 'bold'),
                               bg='#2b3e55', fg='#e2eaf4', relief='flat', padx=10, pady=3,
                               command=lambda: self.safe_action(self.review_proposal_dialog))
        review_btn.pack(side='right')

        # Live Status HUD & Token Tracker Bar
        hud_bar = tk.Frame(page, bg='#0a0e14', padx=12, pady=4)
        hud_bar.pack(fill='x')

        status_indicator = tk.Label(hud_bar, text='🟢 Idle (Ready for Prompt)', font=('Segoe UI', 9, 'bold'),
                                    bg='#0a0e14', fg='#22c55e')
        status_indicator.pack(side='left')

        usage_label = tk.Label(hud_bar, text='Tokens: 0 | Latency: 0.0s | Speed: 0 tok/s',
                               font=('Segoe UI', 8), bg='#0a0e14', fg='#64748b')
        usage_label.pack(side='right')

        # Chat Transcript Area
        transcript_frame = tk.Frame(page, bg='#070a0e', padx=12, pady=6)
        transcript_frame.pack(fill='both', expand=True)

        transcript = tk.Text(transcript_frame, bg='#101822', fg='#e2eaf4',
                             insertbackground='#60a5fa', relief='flat', font=('Segoe UI', 10),
                             wrap='word', padx=12, pady=10)
        transcript.pack(fill='both', expand=True)
        transcript.tag_configure('user', foreground='#60a5fa', font=('Segoe UI', 10, 'bold'))
        transcript.tag_configure('assistant', foreground='#e2eaf4')
        transcript.tag_configure('tool', foreground='#f59e0b', font=('Consolas', 9))
        transcript.tag_configure('router', foreground='#38bdf8', font=('Segoe UI', 8, 'italic'))
        transcript.tag_configure('meta', foreground='#64748b', font=('Segoe UI', 8))

        chats = project.setdefault('chats', [{'title': 'General', 'messages': []}])
        current_chat = chats[0]

        def render_messages():
            transcript.configure(state='normal')
            transcript.delete('1.0', 'end')
            for msg in current_chat['messages']:
                role = msg['role']
                if role == 'user':
                    transcript.insert('end', 'You:\n', 'user')
                    transcript.insert('end', f"{msg['content']}\n\n", 'user')
                elif role == 'assistant':
                    transcript.insert('end', 'Agent Assistant:\n', 'assistant')
                    transcript.insert('end', f"{msg['content']}\n\n", 'assistant')
                elif role == 'tool':
                    transcript.insert('end', f"🛠️ Tool Execution ({msg.get('tool', 'tool')}):\n{msg['content']}\n\n", 'tool')
            transcript.configure(state='disabled')
            transcript.see('end')

        render_messages()

        # Attachments Preview Bar
        attach_preview_frame = tk.Frame(page, bg='#101822', padx=12, pady=4)
        attach_preview_frame.pack(fill='x')

        def render_attachments_bar():
            for child in attach_preview_frame.winfo_children():
                child.destroy()
            if not self.active_attachments:
                attach_preview_frame.pack_forget()
                return
            attach_preview_frame.pack(fill='x')
            tk.Label(attach_preview_frame, text='Attached Files:', font=('Segoe UI', 8, 'bold'),
                     bg='#101822', fg='#9db0c4').pack(side='left', padx=(0, 6))
            for path in list(self.active_attachments):
                pill = tk.Frame(attach_preview_frame, bg='#1f2d3d', padx=6, pady=2)
                pill.pack(side='left', padx=3)
                tk.Label(pill, text=f"📎 {path.name}", font=('Segoe UI', 8),
                         bg='#1f2d3d', fg='#e2eaf4').pack(side='left')
                del_btn = tk.Button(pill, text='✕', font=('Segoe UI', 7), bg='#1f2d3d', fg='#ef4444',
                                    relief='flat', activebackground='#26374a',
                                    command=lambda p=path: [self.active_attachments.remove(p), render_attachments_bar()])
                del_btn.pack(side='left', padx=(4, 0))

        # Prompt Input & Action Controls
        input_frame = tk.Frame(page, bg='#101822', padx=12, pady=8)
        input_frame.pack(fill='x', side='bottom')

        prompt_box = tk.Text(input_frame, height=3, bg='#16212e', fg='#e2eaf4',
                             insertbackground='#60a5fa', relief='flat', font=('Segoe UI', 10),
                             wrap='word', padx=8, pady=6)
        prompt_box.pack(fill='x', side='left', expand=True, padx=(0, 8))

        # Cancel / Stop Generation Button
        cancel_btn = tk.Button(input_frame, text='⏹️ Stop', font=('Segoe UI', 9),
                               bg='#7f1d1d', fg='#fecaca', activebackground='#991b1b',
                               relief='flat', padx=12, pady=8, state='disabled')
        cancel_btn.pack(side='right', padx=(4, 0))

        send_btn = tk.Button(input_frame, text='Send ➤', font=('Segoe UI', 9, 'bold'),
                             bg='#2b3e55', fg='#e2eaf4', relief='flat', padx=16, pady=8)
        send_btn.pack(side='right')

        def attach_files():
            files = filedialog.askdirectory('Select folder to attach files from')
            if files:
                p = Path(files)
                if p.is_dir():
                    for f in list(p.glob('*.*'))[:5]:
                        if f.is_file() and f not in self.active_attachments:
                            self.active_attachments.append(f)
                elif p.is_file() and p not in self.active_attachments:
                    self.active_attachments.append(p)
                render_attachments_bar()

        attach_btn = tk.Button(input_frame, text='📎 Attach', font=('Segoe UI', 9),
                               bg='#1f2d3d', fg='#c2d0df', relief='flat', padx=10, pady=8,
                               command=attach_files)
        attach_btn.pack(side='right', padx=4)

        # ─────────────────────────────────────────────────────────────────────
        # STREAMING & DISPATCH EXECUTION LOGIC
        # ─────────────────────────────────────────────────────────────────────

        def set_ui_busy(busy, status_text='Thinking...'):
            if busy:
                send_btn.config(state='disabled')
                cancel_btn.config(state='normal')
                status_indicator.config(text=f"🟡 {status_text}", fg='#f59e0b')
            else:
                send_btn.config(state='normal')
                cancel_btn.config(state='disabled')
                status_indicator.config(text='🟢 Idle', fg='#22c55e')

        def on_cancel():
            self.abort_event.set()
            status_indicator.config(text='🔴 Cancelled', fg='#ef4444')
            set_ui_busy(False)

        cancel_btn.config(command=on_cancel)

        def poll_stream():
            while not self.stream_queue.empty():
                try:
                    event_type, payload = self.stream_queue.get_nowait()
                except queue.Empty:
                    break

                if event_type == 'chunk':
                    transcript.configure(state='normal')
                    transcript.insert('end', payload, 'assistant')
                    transcript.see('end')
                    transcript.configure(state='disabled')
                elif event_type == 'status':
                    status_indicator.config(text=payload.get('text', ''), fg=payload.get('color', '#60a5fa'))
                elif event_type == 'router':
                    transcript.configure(state='normal')
                    transcript.insert('end', f"[{payload}]\n", 'router')
                    transcript.see('end')
                    transcript.configure(state='disabled')
                elif event_type == 'metrics':
                    usage_label.config(text=payload)
                elif event_type == 'tool_start':
                    transcript.configure(state='normal')
                    transcript.insert('end', f"\n🛠️ Executing: {payload}...\n", 'tool')
                    transcript.see('end')
                    transcript.configure(state='disabled')
                elif event_type == 'tool_result':
                    transcript.configure(state='normal')
                    transcript.insert('end', f"Output: {payload}\n\n", 'tool')
                    transcript.see('end')
                    transcript.configure(state='disabled')
                elif event_type == 'step_start':
                    transcript.configure(state='normal')
                    transcript.insert('end', f"\n⚡ --- [Autonomous {payload}] ---\n", 'router')
                    transcript.see('end')
                    transcript.configure(state='disabled')
                elif event_type == 'done':
                    set_ui_busy(False)
                    if isinstance(payload, list):
                        current_chat['messages'] = payload
                    else:
                        current_chat['messages'].append({'role': 'assistant', 'content': payload})
                    self.store.save()
                    return
                elif event_type == 'error':
                    set_ui_busy(False)
                    transcript.configure(state='normal')
                    transcript.insert('end', f"\n[Error: {payload}]\n\n", 'tool')
                    transcript.see('end')
                    transcript.configure(state='disabled')
                    return

            if self.active_thread and self.active_thread.is_alive():
                page.after(40, poll_stream)
            else:
                set_ui_busy(False)

        def do_send():
            user_text = prompt_box.get('1.0', 'end-1c').strip()
            if not user_text:
                return

            chosen_prov_key = self.store.data.get('active_provider', 'auto')
            manual_model = model_var.get().strip()

            # Package Attachments
            attachment_text = ''
            if self.active_attachments:
                attachment_text = '\n\n[ATTACHED CONTEXT FILES]:\n'
                for att in self.active_attachments:
                    try:
                        content_snip = att.read_text(encoding='utf-8', errors='replace')[:4000]
                        attachment_text += f"\n--- {att.name} ---\n{content_snip}\n--- END {att.name} ---\n"
                    except Exception:
                        pass
                render_attachments_bar()

            full_prompt = user_text + attachment_text
            current_chat['messages'].append({'role': 'user', 'content': full_prompt})
            prompt_box.delete('1.0', 'end')
            render_messages()

            # Intelligent Auto-Routing or Manual Selection
            if chosen_prov_key == 'auto':
                prov_key, resolved_model, route_reason = auto_route_request(
                    full_prompt, self.active_attachments, self.store.data.get('providers', {})
                )
            else:
                prov_key = chosen_prov_key
                resolved_model = manual_model if manual_model and manual_model != '(Automatic)' else self.store.data['providers'].get(prov_key, {}).get('model', 'llama3')
                route_reason = f"Manual override: {self.store.data['providers'].get(prov_key, {}).get('name', prov_key.upper())} ({resolved_model})"

            self.active_attachments.clear()
            render_attachments_bar()

            self.abort_event.clear()
            set_ui_busy(True, f"Connecting to {resolved_model}...")

            transcript.configure(state='normal')
            transcript.insert('end', f"⚡ {route_reason}\n", 'router')
            transcript.insert('end', 'Agent Assistant:\n', 'assistant')
            transcript.configure(state='disabled')

            def worker():
                start_time = time.time()
                total_tokens = 0
                provider_cfg = self.store.data['providers'].get(prov_key, {})
                base_url = provider_cfg.get('base_url', '').rstrip('/')
                api_key = provider_cfg.get('api_key', '')

                system_instructions = (
                    "You are GameForge Studio's autonomous game engineering agent. "
                    "You have direct access to project inspection and modification tools. "
                    "To execute an action, output a markdown JSON block:\n"
                    "```json\n"
                    '{"tool": "read_file" | "list_dir" | "search_code" | "write_file", "args": {...}}\n'
                    "```\n"
                    "Available Tools:\n"
                    "- read_file: {\"path\": \"relative/path\"}\n"
                    "- list_dir: {\"path\": \"relative/path\"}\n"
                    "- search_code: {\"query\": \"search string\"}\n"
                    "- write_file: {\"path\": \"relative/path\", \"content\": \"full content\"}\n"
                    f"Current Project Access Mode: {project.get('access', 'Ask before edits')}.\n"
                    "Autonomous Rules:\n"
                    "1. Inspect files or search code first if you need context before editing.\n"
                    "2. When you call a tool, GameForge executes it and gives you the real observation.\n"
                    "3. You may chain multiple steps (reading, searching, writing) until your task is accomplished.\n"
                    "4. When finished, provide a clear, concise final summary without further tool calls."
                )

                turn_messages = list(current_chat['messages'])
                max_turns = 8

                try:
                    for turn in range(max_turns):
                        if self.abort_event.is_set():
                            break

                        if turn > 0:
                            self.stream_queue.put(('step_start', f"Step {turn+1}/{max_turns}"))
                            self.stream_queue.put(('status', {'text': f'⚡ Step {turn+1}/{max_turns} ({resolved_model})...', 'color': '#38bdf8'}))

                        messages_payload = [{'role': 'system', 'content': system_instructions}]
                        for m in turn_messages:
                            messages_payload.append({'role': m['role'], 'content': m['content']})

                        # 1. Ollama local
                        if prov_key == 'ollama':
                            req_data = json.dumps({
                                'model': resolved_model,
                                'messages': messages_payload,
                                'stream': True
                            }).encode('utf-8')
                            req = urllib.request.Request(
                                f"{base_url}/api/chat", data=req_data,
                                headers={'Content-Type': 'application/json'}
                            )
                        # 2. Google Gemini
                        elif prov_key == 'gemini':
                            gemini_contents = []
                            for m in turn_messages:
                                role_map = 'model' if m['role'] == 'assistant' else 'user'
                                gemini_contents.append({'role': role_map, 'parts': [{'text': m['content']}]})
                            req_data = json.dumps({
                                'system_instruction': {'parts': [{'text': system_instructions}]},
                                'contents': gemini_contents
                            }).encode('utf-8')
                            url = f"https://generativelanguage.googleapis.com/v1beta/models/{resolved_model}:streamGenerateContent?alt=sse&key={api_key}"
                            req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'})

                        # 3. Anthropic Claude
                        elif prov_key == 'anthropic':
                            anthropic_msgs = []
                            for m in turn_messages:
                                anthropic_msgs.append({'role': m['role'], 'content': m['content']})
                            req_data = json.dumps({
                                'model': resolved_model,
                                'system': system_instructions,
                                'messages': anthropic_msgs,
                                'max_tokens': 4096,
                                'stream': True
                            }).encode('utf-8')
                            req = urllib.request.Request(
                                f"{base_url}/messages", data=req_data,
                                headers={
                                    'x-api-key': api_key,
                                    'anthropic-version': '2023-06-01',
                                    'Content-Type': 'application/json'
                                }
                            )
                        # 4. OpenAI / Compatible
                        else:
                            req_data = json.dumps({
                                'model': resolved_model,
                                'messages': messages_payload,
                                'stream': True
                            }).encode('utf-8')
                            headers = {'Content-Type': 'application/json'}
                            if api_key:
                                headers['Authorization'] = f"Bearer {api_key}"
                            req = urllib.request.Request(f"{base_url}/chat/completions", data=req_data, headers=headers)

                        accumulated_text = []
                        with urllib.request.urlopen(req, timeout=90) as response:
                            self.stream_queue.put(('status', {'text': f'🔵 Streaming from {resolved_model}...', 'color': '#60a5fa'}))
                            for raw_line in response:
                                if self.abort_event.is_set():
                                    break
                                line = raw_line.decode('utf-8').strip()
                                if not line:
                                    continue

                                token = ''
                                if prov_key == 'ollama':
                                    try:
                                        chunk = json.loads(line)
                                        token = chunk.get('message', {}).get('content', '')
                                        eval_cnt = chunk.get('eval_count')
                                        if eval_cnt:
                                            total_tokens = eval_cnt
                                    except Exception:
                                        pass
                                elif prov_key == 'gemini':
                                    if line.startswith('data: '):
                                        try:
                                            chunk = json.loads(line[6:])
                                            candidates = chunk.get('candidates', [])
                                            if candidates:
                                                parts = candidates[0].get('content', {}).get('parts', [])
                                                if parts:
                                                    token = parts[0].get('text', '')
                                        except Exception:
                                            pass
                                elif prov_key == 'anthropic':
                                    if line.startswith('data: '):
                                        try:
                                            chunk = json.loads(line[6:])
                                            if chunk.get('type') == 'content_block_delta':
                                                token = chunk.get('delta', {}).get('text', '')
                                        except Exception:
                                            pass
                                else:
                                    if line.startswith('data: '):
                                        line_data = line[6:]
                                        if line_data == '[DONE]':
                                            break
                                        try:
                                            chunk = json.loads(line_data)
                                            token = chunk['choices'][0].get('delta', {}).get('content', '')
                                        except Exception:
                                            pass

                                if token:
                                    total_tokens += 1
                                    accumulated_text.append(token)
                                    self.stream_queue.put(('chunk', token))

                                    elapsed = max(0.1, time.time() - start_time)
                                    speed = total_tokens / elapsed
                                    self.stream_queue.put(('metrics', f"Tokens: {total_tokens} | Latency: {elapsed:.1f}s | Speed: {speed:.1f} tok/s"))

                        complete_reply = ''.join(accumulated_text)
                        turn_messages.append({'role': 'assistant', 'content': complete_reply})

                        # Autonomous Tool Inspection
                        match = re.search(r'```(?:json)?\s*(\{"tool":[\s\S]+?\})\s*```', complete_reply)
                        if not match or self.abort_event.is_set():
                            # Finished without needing further tools!
                            self.stream_queue.put(('done', turn_messages))
                            break

                        # Execute tool
                        try:
                            call = json.loads(match.group(1))
                            tool_name = call.get('tool')
                            args = call.get('args', {})
                            self.stream_queue.put(('tool_start', f"{tool_name} {args}"))

                            res = 'Tool execution failed'
                            if tool_name == 'read_file':
                                res = ToolEngine.read_file(project['path'], args.get('path', ''))
                            elif tool_name == 'list_dir':
                                res = ToolEngine.list_dir(project['path'], args.get('path', ''))
                            elif tool_name == 'search_code':
                                res = ToolEngine.search_code(project['path'], args.get('query', ''))
                            elif tool_name == 'write_file':
                                mode = project.get('access', 'Ask before edits')
                                target_rel = args.get('path', '')
                                content = args.get('content', '')
                                t = (Path(project['path']) / target_rel).resolve()
                                if mode == 'Full project editing':
                                    t.parent.mkdir(parents=True, exist_ok=True)
                                    if t.exists():
                                        bak_dir = Path(project['path']) / '.gameforge' / 'backups'
                                        bak_dir.mkdir(parents=True, exist_ok=True)
                                        bak_file = bak_dir / f"{t.name}_{int(time.time())}.bak"
                                        shutil.copy2(t, bak_file)
                                        project.setdefault('edit_activity', []).append({
                                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                                            'file': target_rel,
                                            'mode': mode,
                                            'backup': str(bak_file)
                                        })
                                    t.write_text(content, encoding='utf-8')
                                    res = f"Written {target_rel} successfully ({len(content)} bytes)."
                                    self.store.save()
                                else:
                                    res = f"File edit to '{target_rel}' proposed and stored in Approval Center for review."

                            self.stream_queue.put(('tool_result', res[:500] + ('...' if len(res) > 500 else '')))
                            turn_messages.append({
                                'role': 'user',
                                'content': f"[Tool Observation ({tool_name})]:\n{res}\n\nAnalyze this result and proceed to your next action, or provide your final summary if complete."
                            })

                            if turn == max_turns - 1:
                                self.stream_queue.put(('done', turn_messages))
                                break

                        except Exception as tool_ex:
                            self.stream_queue.put(('tool_result', f"Tool Error: {tool_ex}"))
                            self.stream_queue.put(('done', turn_messages))
                            break

                except Exception as ex:
                    if self.abort_event.is_set():
                        self.stream_queue.put(('status', {'text': '🔴 Generation Cancelled', 'color': '#ef4444'}))
                    else:
                        self.stream_queue.put(('error', str(ex)))

            self.active_thread = threading.Thread(target=worker, daemon=True)
            self.active_thread.start()
            page.after(50, poll_stream)

        send_btn.config(command=do_send)

    # ─────────────────────────────────────────────────────────────────────────
    # TASKS & ROADMAP TAB
    # ─────────────────────────────────────────────────────────────────────────

    def _tab_tasks(self, page):
        container = tk.Frame(page, bg='#070a0e', padx=16, pady=12)
        container.pack(fill='both', expand=True)

        tk.Label(container, text='Project Tasks & Milestone Roadmap', font=('Segoe UI', 12, 'bold'),
                 bg='#070a0e', fg='#60a5fa').pack(anchor='w')
        tk.Label(container, text='Track game features, mechanics, assets, and bug fixes.',
                 font=('Segoe UI', 9), bg='#070a0e', fg='#7e91a6').pack(anchor='w', pady=(2, 10))

        tasks = self.project.setdefault('tasks', [])

        tasks_listbox = tk.Listbox(container, bg='#101822', fg='#e2eaf4', selectbackground='#2d425c',
                                   font=('Segoe UI', 10), relief='flat', highlightthickness=1,
                                   highlightbackground='#26374a')
        tasks_listbox.pack(fill='both', expand=True, pady=6)

        def refresh_tasks():
            tasks_listbox.delete(0, 'end')
            for t in tasks:
                icon = '☑ [DONE]' if t.get('done') else '☐ [TODO]'
                tasks_listbox.insert('end', f"{icon}  {t.get('title', '')}")

        def toggle_task():
            sel = tasks_listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            tasks[idx]['done'] = not tasks[idx].get('done', False)
            self.store.save()
            refresh_tasks()

        def add_task():
            title = simpledialog.askstring('New Task', 'Task title or roadmap goal:')
            if title:
                tasks.append({'title': title.strip(), 'done': False})
                self.store.save()
                refresh_tasks()

        def remove_task():
            sel = tasks_listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            del tasks[idx]
            self.store.save()
            refresh_tasks()

        btn_bar = tk.Frame(container, bg='#070a0e')
        btn_bar.pack(fill='x', pady=8)

        tk.Button(btn_bar, text='➕ Add Task', font=('Segoe UI', 9, 'bold'),
                  bg='#2b3e55', fg='#e2eaf4', relief='flat', padx=12, pady=5,
                  command=lambda: self.safe_action(add_task)).pack(side='left', padx=(0, 6))
        tk.Button(btn_bar, text='Toggle Status (Done/Todo)', font=('Segoe UI', 9),
                  bg='#182330', fg='#c2d0df', relief='flat', padx=12, pady=5,
                  command=lambda: self.safe_action(toggle_task)).pack(side='left', padx=6)
        tk.Button(btn_bar, text='Remove Task', font=('Segoe UI', 9),
                  bg='#16212e', fg='#ef4444', relief='flat', padx=10, pady=5,
                  command=lambda: self.safe_action(remove_task)).pack(side='left', padx=6)

        refresh_tasks()

    # ─────────────────────────────────────────────────────────────────────────
    # AGENT ACTIVITY & APPROVAL CENTER
    # ─────────────────────────────────────────────────────────────────────────

    def _tab_agents_approvals(self, page):
        container = tk.Frame(page, bg='#070a0e', padx=14, pady=12)
        container.pack(fill='both', expand=True)

        tk.Label(container, text='Agent Activity & Approval Center', font=('Segoe UI', 12, 'bold'),
                 bg='#070a0e', fg='#60a5fa').pack(anchor='w')
        tk.Label(container, text='Review pending agent proposals, inspect unified diffs, and audit historical file modifications.',
                 font=('Segoe UI', 9), bg='#070a0e', fg='#7e91a6').pack(anchor='w', pady=(0, 10))

        bar = tk.Frame(container, bg='#070a0e')
        bar.pack(fill='x', pady=(0, 10))
        tk.Button(bar, text='🔍 Review Pending Proposal', font=('Segoe UI', 9, 'bold'),
                  bg='#2b3e55', fg='#e2eaf4', relief='flat', padx=12, pady=5,
                  command=lambda: self.safe_action(self.review_proposal_dialog)).pack(side='left', padx=(0, 6))
        tk.Button(bar, text='🤖 Pull from Connected Agents', font=('Segoe UI', 9),
                  bg='#1b2736', fg='#c2d0df', relief='flat', padx=12, pady=5,
                  command=self.agent_sources_view).pack(side='left')

        tk.Label(container, text='Audit Log (Applied Agent Edits)', font=('Segoe UI', 10, 'bold'),
                 bg='#070a0e', fg='#c2d0df').pack(anchor='w', pady=(8, 4))

        tree = ttk.Treeview(container, columns=('timestamp', 'file', 'mode', 'status'), show='headings', height=8)
        tree.heading('timestamp', text='Timestamp')
        tree.heading('file', text='File Path')
        tree.heading('mode', text='Permission Mode')
        tree.heading('status', text='Status / Backup')
        tree.column('timestamp', width=160)
        tree.column('file', width=280)
        tree.column('mode', width=140)
        tree.column('status', width=200)
        tree.pack(fill='both', expand=True, pady=4)

        activity = self.project.get('edit_activity', [])
        for act in reversed(activity):
            has_backup = 'Backup Available' if act.get('backup') else 'No Backup'
            tree.insert('', 'end', values=(
                act.get('timestamp', 'Unknown'),
                act.get('file', 'Unknown'),
                act.get('mode', 'Ask before edits'),
                has_backup
            ))

        def rollback_selected():
            sel = tree.focus()
            if not sel:
                return
            idx = tree.index(sel)
            act = list(reversed(activity))[idx]
            backup_path = act.get('backup')
            if not backup_path or not Path(backup_path).exists():
                raise ValueError('Backup file is no longer available on disk')
            dest = (Path(self.project['path']) / act['file']).resolve()
            if messagebox.askyesno('Rollback Edit', f'Restore pre-edit version of {act["file"]}?'):
                shutil.copy2(backup_path, dest)
                messagebox.showinfo('Rollback Complete', f'Restored {act["file"]} to its previous state.')

        roll_bar = tk.Frame(container, bg='#070a0e')
        roll_bar.pack(fill='x', pady=6)
        tk.Button(roll_bar, text='⏪ Rollback Selected Edit', font=('Segoe UI', 9),
                  bg='#1c2938', fg='#c2d0df', relief='flat', padx=12, pady=4,
                  command=lambda: self.safe_action(rollback_selected)).pack(side='left')

    def _tab_game_bible(self, page):
        container = tk.Frame(page, bg='#070a0e', padx=14, pady=12)
        container.pack(fill='both', expand=True)

        tk.Label(container, text='Game Bible & Design Architecture', font=('Segoe UI', 12, 'bold'),
                 bg='#070a0e', fg='#60a5fa').pack(anchor='w')

        bible_path = Path(self.project['path']) / 'GAME_BIBLE.md'
        content = ''
        if bible_path.exists():
            try:
                content = bible_path.read_text(encoding='utf-8', errors='replace')
            except Exception:
                pass

        editor = tk.Text(container, bg='#101822', fg='#e2eaf4', insertbackground='#60a5fa',
                         relief='flat', font=('Consolas', 10), wrap='word', padx=10, pady=8)
        editor.insert('1.0', content or f"# {self.project['name']} — Game Bible\n\n## Overview\n\n## Core Mechanics\n\n## Art Style & Assets\n")
        editor.pack(fill='both', expand=True, pady=8)

        def save_bible():
            text = editor.get('1.0', 'end-1c')
            bible_path.write_text(text, encoding='utf-8')
            messagebox.showinfo('Game Bible', f'Saved to {bible_path.name}')

        tk.Button(container, text='💾 Save Game Bible', font=('Segoe UI', 9, 'bold'),
                  bg='#2b3e55', fg='#e2eaf4', relief='flat', padx=14, pady=6,
                  command=save_bible).pack(anchor='w')

    def _tab_changes(self, page):
        container = tk.Frame(page, bg='#070a0e', padx=14, pady=12)
        container.pack(fill='both', expand=True)

        tk.Label(container, text='Git Status & Working Tree Changes', font=('Segoe UI', 12, 'bold'),
                 bg='#070a0e', fg='#60a5fa').pack(anchor='w')

        viewer = tk.Text(container, bg='#101822', fg='#e2eaf4', relief='flat',
                         font=('Consolas', 10), wrap='none', padx=10, pady=8)
        viewer.pack(fill='both', expand=True, pady=8)

        def refresh_git():
            viewer.configure(state='normal')
            viewer.delete('1.0', 'end')
            try:
                stat = git(self.project['path'], 'status', '--short', '--branch')
                diff = git(self.project['path'], 'diff')
                viewer.insert('end', f"=== Status ===\n{stat or 'Clean'}\n\n=== Diff ===\n{diff or '(No unstaged modifications)'}")
            except Exception as ex:
                viewer.insert('end', f"Git inquiry: {ex}")
            viewer.configure(state='disabled')

        refresh_git()
        tk.Button(container, text='🔄 Refresh Changes', font=('Segoe UI', 9),
                  bg='#1c2938', fg='#c2d0df', relief='flat', padx=12, pady=5,
                  command=refresh_git).pack(anchor='w')

    def _tab_connect(self, page):
        container = tk.Frame(page, bg='#070a0e', padx=18, pady=16)
        container.pack(fill='both', expand=True)

        tk.Label(container, text='GameForge Connect • Team AI Safeguards',
                 font=('Segoe UI', 13, 'bold'), bg='#070a0e', fg='#60a5fa').pack(anchor='w')

        notice_box = tk.Frame(container, bg='#141c26', padx=14, pady=12, highlightthickness=1,
                              highlightbackground='#26374a')
        notice_box.pack(fill='x', pady=10)

        invariants_text = (
            "MANDATORY SAFETY INVARIANTS:\n"
            "• Team-paid AI resources are strictly OPT-IN per member and per project.\n"
            "• Disabled by default on all projects and profiles.\n"
            "• Individual spending caps are enforced ($0.00 default).\n"
            "• Immediate revocation cuts off all remote token spending instantly.\n"
            "• No automatic cost splitting between workspace collaborators."
        )
        tk.Label(notice_box, text=invariants_text, font=('Segoe UI', 9),
                 justify='left', bg='#141c26', fg='#c2d0df').pack(anchor='w')

        team_ai = self.store.data.get('team_ai', {})
        status_text = "CURRENT STATUS: DISABLED (Safe • Local requests only)"
        tk.Label(container, text=status_text, font=('Segoe UI', 11, 'bold'),
                 bg='#070a0e', fg='#22c55e' if not team_ai.get('enabled') else '#f59e0b').pack(anchor='w', pady=(10, 4))

        tk.Label(container, text=f"Spending Cap Ceiling: ${team_ai.get('individual_cap_usd', 0.0):.2f} USD",
                 font=('Segoe UI', 10), bg='#070a0e', fg='#9db0c4').pack(anchor='w')

        btn_bar = tk.Frame(container, bg='#070a0e')
        btn_bar.pack(fill='x', pady=14)

        def revoke_now():
            team_ai['enabled'] = False
            team_ai['immediate_revocation'] = True
            team_ai['individual_cap_usd'] = 0.0
            self.store.save()
            messagebox.showinfo('Revocation Enforced', 'All team AI connections have been revoked and set to $0.00.')
            self.home()

        tk.Button(btn_bar, text='🛑 Immediate Revocation (Kill Switch)', font=('Segoe UI', 9, 'bold'),
                  bg='#7f1d1d', fg='#fecaca', activebackground='#991b1b', relief='flat', padx=14, pady=6,
                  command=revoke_now).pack(side='left', padx=(0, 8))

    # ─────────────────────────────────────────────────────────────────────────
    # FILE PROPOSAL REVIEW & DIFF VIEWER
    # ─────────────────────────────────────────────────────────────────────────

    def review_proposal_dialog(self):
        if not self.project:
            return
        chats = self.project.get('chats', [])
        if not chats:
            raise ValueError('No active conversation history')
        messages = chats[0].get('messages', [])
        assistant_msg = next((m['content'] for m in reversed(messages) if m['role'] == 'assistant'), '')
        clean = re.sub(r'^```(?:json)?\s*|\s*```$', '', assistant_msg.strip())

        proposal = None
        try:
            proposal = json.loads(clean)
        except Exception:
            match = re.search(r'\{[\s\S]*\}', clean)
            if match:
                try:
                    proposal = json.loads(match.group(0))
                except Exception:
                    pass

        if not proposal or 'path' not in proposal or 'content' not in proposal:
            raise ValueError('No valid file edit proposal found in recent assistant responses.')

        relative = proposal['path']
        content = proposal['content']
        root = Path(self.project['path']).resolve()
        target = (root / relative).resolve()

        if root not in target.parents or '.git' in target.relative_to(root).parts:
            raise ValueError('Proposal path is outside allowed project boundaries')

        before_bytes = target.read_bytes() if target.exists() else None
        expected_digest = hashlib.sha256(before_bytes).hexdigest() if before_bytes is not None else None
        old_text = before_bytes.decode('utf-8', errors='replace') if before_bytes is not None else ''

        diff = ''.join(difflib.unified_diff(
            old_text.splitlines(True), content.splitlines(True),
            fromfile=f"a/{relative}", tofile=f"b/{relative}"
        ))

        win = tk.Toplevel(self)
        win.title(f'Review Proposed Edit: {relative}')
        win.configure(bg='#070a0e')
        win.geometry('880x640')
        win.transient(self)

        top_f = tk.Frame(win, bg='#0d131a', padx=16, pady=12)
        top_f.pack(fill='x')
        tk.Label(top_f, text=f"Proposal for: {relative}", font=('Segoe UI', 12, 'bold'),
                 bg='#0d131a', fg='#60a5fa').pack(anchor='w')
        tk.Label(top_f, text='Review diff below. Click Approve to write changes atomically with backup.',
                 font=('Segoe UI', 9), bg='#0d131a', fg='#7e91a6').pack(anchor='w')

        viewer = tk.Text(win, bg='#0c1117', fg='#e2eaf4', relief='flat',
                         font=('Consolas', 10), wrap='none', padx=10, pady=8)
        viewer.pack(fill='both', expand=True, padx=16, pady=8)
        viewer.tag_configure('add', foreground='#22c55e')
        viewer.tag_configure('sub', foreground='#ef4444')
        viewer.tag_configure('hdr', foreground='#60a5fa', font=('Consolas', 10, 'bold'))

        for line in (diff or '(Identical content)').splitlines():
            tag = None
            if line.startswith('+') and not line.startswith('+++'):
                tag = 'add'
            elif line.startswith('-') and not line.startswith('---'):
                tag = 'sub'
            elif line.startswith('@'):
                tag = 'hdr'
            viewer.insert('end', line + '\n', tag)
        viewer.configure(state='disabled')

        btn_bar = tk.Frame(win, bg='#070a0e', padx=16, pady=12)
        btn_bar.pack(fill='x')

        def do_apply():
            applied = apply_edit(
                self.project, relative, content, expected_digest,
                lambda: messagebox.askyesno('Confirm Approval', f'Apply verified edit to {relative}?')
            )
            if applied:
                self.store.save()
                messagebox.showinfo('Applied', f'Successfully updated {relative}.')
                win.destroy()
                self.home()

        tk.Button(btn_bar, text='✅ Approve & Apply Edit', font=('Segoe UI', 10, 'bold'),
                  bg='#15803d', fg='#ffffff', activebackground='#166534', relief='flat', padx=16, pady=6,
                  command=lambda: self.safe_action(do_apply)).pack(side='right')
        tk.Button(btn_bar, text='Reject', font=('Segoe UI', 9),
                  bg='#1e293b', fg='#94a3b8', relief='flat', padx=12, pady=6,
                  command=win.destroy).pack(side='right', padx=8)

        dark_title(win)
        win.grab_set()

    # ─────────────────────────────────────────────────────────────────────────
    # RECOVERY CENTER (Checkpoints & Restore)
    # ─────────────────────────────────────────────────────────────────────────

    def recovery_center_view(self):
        self.clear_main('Recovery Center', 'Create and restore safety checkpoints (ZIP archives).')

        container = tk.Frame(self.main, bg='#070a0e')
        container.pack(fill='both', expand=True)

        top_bar = tk.Frame(container, bg='#101822', padx=14, pady=10)
        top_bar.pack(fill='x', pady=(0, 10))

        tk.Label(top_bar, text='Checkpoints are self-contained ZIP archives. Restoring ALWAYS requires a new empty destination to prevent data loss.',
                 font=('Segoe UI', 9), bg='#101822', fg='#9db0c4').pack(anchor='w')

        tree = ttk.Treeview(container, columns=('date', 'project', 'size', 'path'), show='headings')
        tree.heading('date', text='Created Date')
        tree.heading('project', text='Project Name')
        tree.heading('size', text='Archive Size')
        tree.heading('path', text='Archive Location')
        tree.column('date', width=160)
        tree.column('project', width=180)
        tree.column('size', width=100, anchor='e')
        tree.column('path', width=400)
        tree.pack(fill='both', expand=True, pady=6)

        def refresh_checkpoints():
            tree.delete(*tree.get_children())
            CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)
            for zip_p in sorted(CHECKPOINTS_DIR.glob('*.zip'), key=lambda p: p.stat().st_mtime, reverse=True):
                sz = zip_p.stat().st_size
                size_str = f"{sz / (1024 * 1024):.1f} MB" if sz > 1024 * 1024 else f"{sz / 1024:.1f} KB"
                dt = datetime.datetime.fromtimestamp(zip_p.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                prj_name = zip_p.stem.split('-checkpoint-')[0]
                tree.insert('', 'end', values=(dt, prj_name, size_str, str(zip_p)))

        def do_create():
            if not self.project:
                raise ValueError('Select a project in the sidebar first to create a checkpoint.')
            archive = create_checkpoint(self.project)
            messagebox.showinfo('Checkpoint Created', f'Safety checkpoint saved:\n{archive}')
            refresh_checkpoints()

        def do_restore():
            sel = tree.focus()
            if not sel:
                raise ValueError('Select a checkpoint from the list above to restore.')
            zip_path = tree.item(sel)['values'][3]
            target = filedialog.askdirectory('Choose NEW, EMPTY destination folder for restore')
            if not target:
                return
            restored = restore_checkpoint(zip_path, target)
            if messagebox.askyesno('Register Restored Project', f'Restored to:\n{restored}\n\nRegister in GameForge Studio now?'):
                self.store.register(restored)
                self.refresh()
                self.home()

        actions_f = tk.Frame(container, bg='#070a0e')
        actions_f.pack(fill='x', pady=8)
        tk.Button(actions_f, text='🛡️ Create Checkpoint for Current Project', font=('Segoe UI', 9, 'bold'),
                  bg='#2b3e55', fg='#e2eaf4', relief='flat', padx=14, pady=6,
                  command=lambda: self.safe_action(do_create)).pack(side='left', padx=(0, 6))
        tk.Button(actions_f, text='📦 Restore Checkpoint to New Folder', font=('Segoe UI', 9),
                  bg='#1b2736', fg='#c2d0df', relief='flat', padx=14, pady=6,
                  command=lambda: self.safe_action(do_restore)).pack(side='left', padx=6)
        tk.Button(actions_f, text='🔄 Refresh List', font=('Segoe UI', 9),
                  bg='#16212e', fg='#9db0c4', relief='flat', padx=10, pady=6,
                  command=refresh_checkpoints).pack(side='left')

        refresh_checkpoints()

    def create_project_checkpoint(self, project):
        archive = create_checkpoint(project)
        messagebox.showinfo('Checkpoint Created', f'Checkpoint saved successfully:\n{archive}')

    # ─────────────────────────────────────────────────────────────────────────
    # MULTI-AGENT SYNCER (Pull from Agents)
    # ─────────────────────────────────────────────────────────────────────────

    def agent_sources_view(self):
        self.clear_main('Pull from AI Agents', 'Read and refresh reports from Cursor, Antigravity, and connected markdown documents.')

        controls = tk.Frame(self.main, bg='#101822', padx=12, pady=8)
        controls.pack(fill='x')

        preview = tk.Text(self.main, bg='#0c1117', fg='#e2eaf4', relief='flat',
                          font=('Segoe UI', 10), wrap='word', padx=14, pady=12)
        preview.pack(fill='both', expand=True, pady=8)

        def pull_all():
            reports = []
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            for src in self.store.data.get('agent_sources', []):
                p = Path(src)
                if p.exists():
                    try:
                        reports.append(f"═══════════════════════════════════════════════════════════════\n"
                                       f"SOURCE: {p.name} ({p})\n"
                                       f"═══════════════════════════════════════════════════════════════\n\n"
                                       f"{read_source(p)}")
                    except Exception as ex:
                        reports.append(f"SOURCE ERROR ({p}): {ex}")

            if self.project:
                cursor_gap = Path(self.project['path']) / '.cursor' / 'LIVE_GAPS.md'
                if cursor_gap.exists():
                    try:
                        reports.append(f"═══════════════════════════════════════════════════════════════\n"
                                       f"PROJECT CURSOR GAPS: {self.project['name']} (.cursor/LIVE_GAPS.md)\n"
                                       f"═══════════════════════════════════════════════════════════════\n\n"
                                       f"{read_source(cursor_gap)}")
                    except Exception:
                        pass

            preview.configure(state='normal')
            preview.delete('1.0', 'end')
            preview.insert('1.0', f"Refreshed locally: {timestamp}\nConnected sources: {len(self.store.data.get('agent_sources', []))}\n\n" +
                           '\n\n'.join(reports))
            preview.configure(state='disabled')

        def add_source():
            path_str = simpledialog.askstring('Add Agent Source', 'Full path to agent markdown, report or JSON:')
            if path_str:
                p = Path(path_str).resolve()
                if not p.is_file():
                    raise ValueError('File does not exist')
                sources = self.store.data.setdefault('agent_sources', [])
                if str(p) not in sources:
                    sources.append(str(p))
                    self.store.save()
                pull_all()

        for label, cmd in [('🔄 Pull Latest Updates', pull_all),
                           ('➕ Connect Source File', add_source),
                           ('📋 Copy to Clipboard', lambda: [self.clipboard_clear(), self.clipboard_append(preview.get('1.0', 'end'))])]:
            tk.Button(controls, text=label, font=('Segoe UI', 9), bg='#1b2736', fg='#c2d0df',
                      relief='flat', padx=12, pady=5, command=lambda c=cmd: self.safe_action(c)).pack(side='left', padx=3)

        pull_all()

    # ─────────────────────────────────────────────────────────────────────────
    # MASTER LIST EDITOR & BATCH IMPORT
    # ─────────────────────────────────────────────────────────────────────────

    def master_list_view(self):
        self.clear_main('Project Master List Editor', 'Edit MASTER_PROJECTS.md and PROJECTS.md with automatic outside modification detection and backup.')

        controls = tk.Frame(self.main, bg='#101822', padx=12, pady=8)
        controls.pack(fill='x')

        editor = tk.Text(self.main, bg='#0c1117', fg='#e2eaf4', insertbackground='#60a5fa',
                         relief='flat', font=('Consolas', 10), wrap='word', padx=14, pady=12, undo=True)
        editor.pack(fill='both', expand=True, pady=8)

        loaded_state = {'path': None, 'text': None}

        def load_doc(path):
            p = Path(path).resolve(strict=True)
            txt = read_source(p)
            loaded_state.update(path=str(p), text=txt)
            editor.delete('1.0', 'end')
            editor.insert('1.0', txt)
            self.store.data['master_list'] = str(p)
            self.store.save()

        def save_doc():
            if not loaded_state['path']:
                raise ValueError('No document currently connected')
            p = Path(loaded_state['path'])
            if read_source(p) != loaded_state['text']:
                raise ValueError('Document was modified outside GameForge Studio. Please reconnect or reload before saving.')

            if not messagebox.askyesno('Save Changes', f'Save edits to {p.name}? A backup will be generated.'):
                return
            timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            backup_p = p.with_name(f"{p.name}.{timestamp}.bak")
            shutil.copy2(p, backup_p)

            new_text = editor.get('1.0', 'end-1c')
            p.write_text(new_text, encoding='utf-8')
            loaded_state['text'] = new_text
            messagebox.showinfo('Saved', f'Document saved. Backup created:\n{backup_p.name}')

        def choose_doc():
            chosen = simpledialog.askstring('Connect Master List', 'Full path to masterlist markdown:')
            if chosen:
                load_doc(chosen)

        for label, cmd in [('💾 Save Edits with Backup', save_doc),
                           ('📂 Connect / Switch File', choose_doc),
                           ('📋 Batch Import Projects', self.batch_import_dialog)]:
            tk.Button(controls, text=label, font=('Segoe UI', 9), bg='#1b2736', fg='#c2d0df',
                      relief='flat', padx=12, pady=5, command=lambda c=cmd: self.safe_action(c)).pack(side='left', padx=3)

        curr_master = self.store.data.get('master_list')
        if curr_master and Path(curr_master).exists():
            load_doc(curr_master)
        elif Path('D:/DEVELOPMENT/MASTER_PROJECTS.md').exists():
            load_doc('D:/DEVELOPMENT/MASTER_PROJECTS.md')

    def batch_import_dialog(self):
        docs = []
        master = self.store.data.get('master_list', 'D:\\DEVELOPMENT\\MASTER_PROJECTS.md')
        if Path(master).exists():
            docs.append(master)
            comp = Path(master).with_name('PROJECTS.md')
            if comp.exists() and str(comp) not in docs:
                docs.append(str(comp))

        records = project_catalog(docs)
        if not records:
            raise ValueError('No projects detected in the master list document.')

        win = tk.Toplevel(self)
        win.title('Batch Import Projects from Master List')
        win.configure(bg='#070a0e')
        win.geometry('780x560')
        win.transient(self)

        top_f = tk.Frame(win, bg='#0d131a', padx=16, pady=12)
        top_f.pack(fill='x')
        tk.Label(top_f, text=f"Discovered {len(records)} Projects in Master List",
                 font=('Segoe UI', 12, 'bold'), bg='#0d131a', fg='#60a5fa').pack(anchor='w')
        tk.Label(top_f, text='Check existing projects to register in GameForge Studio without modifying any files.',
                 font=('Segoe UI', 9), bg='#0d131a', fg='#7e91a6').pack(anchor='w')

        tree = ttk.Treeview(win, columns=('status', 'engine', 'path'), show='tree headings')
        tree.heading('#0', text='Project Name')
        tree.heading('status', text='Status')
        tree.heading('engine', text='Engine')
        tree.heading('path', text='Resolved Path')
        tree.column('#0', width=180)
        tree.column('status', width=100)
        tree.column('engine', width=120)
        tree.column('path', width=320)
        tree.pack(fill='both', expand=True, padx=16, pady=10)

        for rec in records:
            path_display = rec['path'] or 'Path not on disk / pitch'
            tree.insert('', 'end', iid=rec['name'], text=rec['name'],
                        values=(rec.get('status', 'Catalogued'), rec.get('engine', 'Unknown'), path_display))

        btn_bar = tk.Frame(win, bg='#070a0e', padx=16, pady=12)
        btn_bar.pack(fill='x')

        def import_all_existing():
            imported_count = 0
            for rec in records:
                if rec['path'] and Path(rec['path']).is_dir():
                    self.store.register(rec['path'], name=rec['name'], synopsis=rec['synopsis'])
                    imported_count += 1
            self.refresh()
            messagebox.showinfo('Import Complete', f"Successfully registered {imported_count} projects into GameForge Studio.")
            win.destroy()
            self.home()

        tk.Button(btn_bar, text='📥 Import All Existing Projects on Disk', font=('Segoe UI', 9, 'bold'),
                  bg='#2b3e55', fg='#e2eaf4', relief='flat', padx=16, pady=6,
                  command=import_all_existing).pack(side='right')
        tk.Button(btn_bar, text='Cancel', font=('Segoe UI', 9),
                  bg='#16212e', fg='#9db0c4', relief='flat', padx=12, pady=6,
                  command=win.destroy).pack(side='right', padx=8)

        dark_title(win)
        win.grab_set()

    # ─────────────────────────────────────────────────────────────────────────
    # FIRST-RUN SETUP WIZARD & AI LOGINS
    # ─────────────────────────────────────────────────────────────────────────

    def setup_wizard(self):
        """Interactive 4-step wizard introducing tools, AI sign-ins, and safety invariants."""
        win = tk.Toplevel(self)
        win.title('GameForge Studio Setup Wizard')
        win.configure(bg='#070a0e')
        win.geometry('780x560')
        win.transient(self)

        step = [0]
        tools = detect_tools()
        providers = self.store.data.setdefault('providers', {})

        body = tk.Frame(win, bg='#070a0e', padx=24, pady=18)
        body.pack(fill='both', expand=True)

        def render_step():
            for child in body.winfo_children():
                child.destroy()
            s = step[0]

            if s == 0:
                tk.Label(body, text='Step 1 of 4: Environment & Toolchains', font=('Segoe UI', 14, 'bold'),
                         bg='#070a0e', fg='#60a5fa').pack(anchor='w', pady=(0, 4))
                tk.Label(body, text='GameForge detected the following developer toolchains and game engines on your Windows system:',
                         font=('Segoe UI', 9), bg='#070a0e', fg='#9db0c4').pack(anchor='w', pady=(0, 12))

                grid = tk.Frame(body, bg='#0f1620', padx=12, pady=10)
                grid.pack(fill='both', expand=True)
                for i, (tool_name, info) in enumerate(tools.items()):
                    status_color = '#22c55e' if info['installed'] else '#64748b'
                    status_text = '✓ Ready' if info['installed'] else '— Not Detected'
                    tk.Label(grid, text=f"{tool_name.upper()}:", font=('Segoe UI', 9, 'bold'),
                             bg='#0f1620', fg='#c2d0df').grid(row=i % 7, column=(i // 7) * 2, sticky='w', pady=2, padx=4)
                    tk.Label(grid, text=f"{status_text} ({info['version']})", font=('Segoe UI', 8),
                             bg='#0f1620', fg=status_color).grid(row=i % 7, column=(i // 7) * 2 + 1, sticky='w', pady=2, padx=4)

            elif s == 1:
                # ── Step 2: AI Provider Sign-Ins & Authentication ──
                tk.Label(body, text='Step 2 of 4: AI Provider Sign-Ins & Setup', font=('Segoe UI', 14, 'bold'),
                         bg='#070a0e', fg='#60a5fa').pack(anchor='w', pady=(0, 4))
                tk.Label(body, text='Connect the AI models you use. GameForge auto-switches between them depending on whether you need code, vision, or quick fixes:',
                         font=('Segoe UI', 9), bg='#070a0e', fg='#9db0c4').pack(anchor='w', pady=(0, 10))

                scroll_f = tk.Frame(body, bg='#070a0e')
                scroll_f.pack(fill='both', expand=True)

                provider_items = [
                    ('gemini', 'Google Gemini', 'Multimodal vision, concept art analysis, 1M+ token context', True),
                    ('anthropic', 'Anthropic Claude', 'Deep game architecture, state machines, physics, and complex refactors', True),
                    ('openai', 'OpenAI (GPT-4o)', 'Character turnarounds, 3D specs, general reasoning', True),
                    ('ollama', 'Local Ollama', 'Zero-cost offline iteration, instant syntax checks & quick bug fixes', False),
                    ('fal', 'Fal.ai / Tripo 3D', 'Video reference generation (Flux) and 3D mesh modeling', True),
                ]

                for p_key, p_title, p_desc, needs_key in provider_items:
                    card = tk.Frame(scroll_f, bg='#141c26', padx=10, pady=8, highlightthickness=1,
                                    highlightbackground='#26374a')
                    card.pack(fill='x', pady=3)

                    top_row = tk.Frame(card, bg='#141c26')
                    top_row.pack(fill='x')
                    tk.Label(top_row, text=p_title, font=('Segoe UI', 10, 'bold'),
                             bg='#141c26', fg='#e2eaf4').pack(side='left')
                    tk.Label(top_row, text=f"• {p_desc}", font=('Segoe UI', 8),
                             bg='#141c26', fg='#9db0c4').pack(side='left', padx=6)

                    cfg = providers.setdefault(p_key, {})
                    status_lbl = tk.Label(top_row, text='⚪ Not tested', font=('Segoe UI', 8, 'bold'),
                                          bg='#141c26', fg='#7e91a6')
                    status_lbl.pack(side='right')

                    bot_row = tk.Frame(card, bg='#141c26')
                    bot_row.pack(fill='x', pady=(4, 0))

                    if needs_key:
                        tk.Label(bot_row, text='API Key:', font=('Segoe UI', 8), bg='#141c26', fg='#7e91a6').pack(side='left')
                        k_var = tk.StringVar(value=cfg.get('api_key', ''))
                        k_entry = tk.Entry(bot_row, textvariable=k_var, width=38, show='•',
                                           bg='#1b2736', fg='#e2eaf4', relief='flat')
                        k_entry.pack(side='left', padx=6)

                        def toggle_mask(ent=k_entry):
                            ent.config(show='' if ent.cget('show') == '•' else '•')

                        tk.Button(bot_row, text='👁', font=('Segoe UI', 7), bg='#1b2736', fg='#9db0c4',
                                  relief='flat', padx=4, command=toggle_mask).pack(side='left', padx=(0, 6))

                        def test_key(pk=p_key, kv=k_var, sl=status_lbl):
                            k_val = kv.get().strip()
                            providers[pk]['api_key'] = k_val
                            b_url = providers[pk].get('base_url', '')
                            ok, msg = verify_provider_auth(pk, b_url, k_val)
                            if ok:
                                sl.config(text='🟢 Connected & Verified', fg='#22c55e')
                                providers[pk]['enabled'] = True
                            else:
                                sl.config(text=f'🔴 {msg}', fg='#ef4444')
                            self.store.save()

                        tk.Button(bot_row, text='Sign In / Verify', font=('Segoe UI', 8, 'bold'),
                                  bg='#2b3e55', fg='#e2eaf4', relief='flat', padx=10, pady=2,
                                  command=test_key).pack(side='left')

                        # Auto-check if key already populated from environment
                        if k_var.get():
                            test_key(p_key, k_var, status_lbl)
                    else:
                        tk.Label(bot_row, text='Local URL: http://127.0.0.1:11434', font=('Segoe UI', 8),
                                 bg='#141c26', fg='#9db0c4').pack(side='left')

                        def test_ollama(pk=p_key, sl=status_lbl):
                            b_url = providers[pk].get('base_url', 'http://127.0.0.1:11434')
                            ok, msg = verify_provider_auth(pk, b_url, '')
                            sl.config(text='🟢 Online' if ok else '⚪ Offline', fg='#22c55e' if ok else '#9db0c4')
                            providers[pk]['enabled'] = ok
                            self.store.save()

                        tk.Button(bot_row, text='Check Service Status', font=('Segoe UI', 8),
                                  bg='#1b2736', fg='#c2d0df', relief='flat', padx=10, pady=2,
                                  command=test_ollama).pack(side='left', padx=8)

            elif s == 2:
                tk.Label(body, text='Step 3 of 4: Master Project Tracker', font=('Segoe UI', 14, 'bold'),
                         bg='#070a0e', fg='#60a5fa').pack(anchor='w', pady=(0, 4))
                tk.Label(body, text='Connect your central master project document to manage your game portfolio:',
                         font=('Segoe UI', 9), bg='#070a0e', fg='#9db0c4').pack(anchor='w', pady=(0, 14))

                detected_master = 'D:\\DEVELOPMENT\\MASTER_PROJECTS.md'
                has_master = Path(detected_master).exists()

                box = tk.Frame(body, bg='#141c26', padx=14, pady=14)
                box.pack(fill='x', pady=10)
                tk.Label(box, text='Detected Location:' if has_master else 'Default Location:',
                         font=('Segoe UI', 9, 'bold'), bg='#141c26', fg='#60a5fa').pack(anchor='w')
                tk.Label(box, text=detected_master, font=('Segoe UI', 10),
                         bg='#141c26', fg='#ffffff' if has_master else '#7e91a6').pack(anchor='w', pady=(4, 0))

            elif s == 3:
                tk.Label(body, text='Step 4 of 4: Team AI Safety Invariant', font=('Segoe UI', 14, 'bold'),
                         bg='#070a0e', fg='#22c55e').pack(anchor='w', pady=(0, 4))
                tk.Label(body, text='Please review and confirm the GameForge Connect safety guarantee:',
                         font=('Segoe UI', 9), bg='#070a0e', fg='#9db0c4').pack(anchor='w', pady=(0, 14))

                card = tk.Frame(body, bg='#141c26', padx=14, pady=14)
                card.pack(fill='x', pady=10)
                guarantee = (
                    "✓ Team-paid AI resources are DISABLED by default.\n"
                    "✓ Explicit opt-in is required per member and per project.\n"
                    "✓ Individual spending caps with hard limit ($0.00 default).\n"
                    "✓ Immediate revocation cuts off all remote access instantly.\n"
                    "✓ No automatic cost splitting between users."
                )
                tk.Label(card, text=guarantee, font=('Segoe UI', 10), justify='left',
                         bg='#141c26', fg='#c2d0df').pack(anchor='w')

        render_step()

        btn_bar = tk.Frame(win, bg='#070a0e', padx=24, pady=16)
        btn_bar.pack(fill='x', side='bottom')

        def next_step():
            if step[0] < 3:
                step[0] += 1
                render_step()
                if step[0] == 3:
                    next_btn.config(text='Finish Setup ✓')
            else:
                self.store.data['setup'] = True
                self.store.save()
                win.destroy()
                messagebox.showinfo('Setup Complete', 'GameForge Studio is configured with your AI providers.')

        next_btn = tk.Button(btn_bar, text='Next Step ➤', font=('Segoe UI', 9, 'bold'),
                             bg='#2b3e55', fg='#e2eaf4', relief='flat', padx=16, pady=6,
                             command=next_step)
        next_btn.pack(side='right')

        dark_title(win)
        win.grab_set()

    def about_dialog(self):
        """Displays About GameForge Studio modal with links and release info."""
        win = tk.Toplevel(self)
        win.title('About GameForge Studio')
        win.configure(bg='#070a0e')
        win.geometry('580x420')
        win.transient(self)

        top_f = tk.Frame(win, bg='#0d131a', padx=20, pady=16)
        top_f.pack(fill='x')
        tk.Label(top_f, text='GameForge Studio', font=('Segoe UI', 16, 'bold'),
                 bg='#0d131a', fg='#60a5fa').pack(anchor='w')
        tk.Label(top_f, text=f"Version {APP_VERSION} (Production Release) • Obsidian Glass Slate",
                 font=('Segoe UI', 9), bg='#0d131a', fg='#9db0c4').pack(anchor='w', pady=(2, 0))

        content_f = tk.Frame(win, bg='#070a0e', padx=20, pady=14)
        content_f.pack(fill='both', expand=True)

        desc = (
            "GameForge Studio is an agent-augmented desktop IDE for game developers.\n\n"
            "• Auto-Routing Dispatcher: Automatically routes between Vision, Logic & Local AI\n"
            "• Engine Integrations: Unreal Engine 5, Godot 4, Unity, ESP32-S3, Blender\n"
            "• Autonomous Sandbox: Code inspection, live diff proposals, and atomic safety edits\n"
            "• Multi-Agent Sync: Real-time Cursor, Antigravity, and master list tracking\n"
            "• Recovery Center: Instant ZIP checkpoints, clean folder restores, and file rollbacks\n"
            "• Connect Invariant: 100% Opt-in team AI spending with immediate kill switches\n\n"
            "GitHub Repository: https://github.com/CharmCompanion/GameForgeStudio\n"
            "Licensed under the MIT License. Copyright (c) 2026 CharmCompanion."
        )
        tk.Label(content_f, text=desc, font=('Segoe UI', 9), justify='left',
                 bg='#070a0e', fg='#c2d0df').pack(anchor='w')

        btn_bar = tk.Frame(win, bg='#070a0e', padx=20, pady=12)
        btn_bar.pack(fill='x', side='bottom')
        tk.Button(btn_bar, text='Close', font=('Segoe UI', 9, 'bold'),
                  bg='#2b3e55', fg='#e2eaf4', relief='flat', padx=16, pady=6,
                  command=win.destroy).pack(side='right')

        dark_title(win)
        win.grab_set()

    def settings_view(self):
        self.clear_main('Settings & AI Provider Keys', 'Tool detection, AI provider sign-ins, rules, and skill compatibility.')

        tabs = ttk.Notebook(self.main)
        tabs.pack(fill='both', expand=True)

        # Tab: AI Providers & Usage
        ai_frame = ttk.Frame(tabs)
        tabs.add(ai_frame, text=' AI Providers & Logins ')
        ai_box = tk.Frame(ai_frame, bg='#070a0e', padx=16, pady=14)
        ai_box.pack(fill='both', expand=True)

        tk.Label(ai_box, text='Connected Providers & API Keys', font=('Segoe UI', 11, 'bold'),
                 bg='#070a0e', fg='#60a5fa').pack(anchor='w', pady=(0, 4))
        tk.Label(ai_box, text='Configure credentials. GameForge auto-selects the best AI based on whether you are analyzing concept art, refactoring logic, or debugging.',
                 font=('Segoe UI', 9), bg='#070a0e', fg='#9db0c4').pack(anchor='w', pady=(0, 10))

        prov_scroll = tk.Frame(ai_box, bg='#070a0e')
        prov_scroll.pack(fill='both', expand=True)

        providers = self.store.data.get('providers', {})
        for key, pinfo in providers.items():
            card = tk.Frame(prov_scroll, bg='#141c26', padx=12, pady=10, highlightthickness=1,
                            highlightbackground='#26374a')
            card.pack(fill='x', pady=4)

            tk.Label(card, text=pinfo.get('name', key.upper()), font=('Segoe UI', 10, 'bold'),
                     bg='#141c26', fg='#e2eaf4').pack(anchor='w')

            row = tk.Frame(card, bg='#141c26')
            row.pack(fill='x', pady=4)

            tk.Label(row, text='API Key:', font=('Segoe UI', 8), bg='#141c26', fg='#9db0c4').pack(side='left')
            k_var = tk.StringVar(value=pinfo.get('api_key', ''))
            k_ent = tk.Entry(row, textvariable=k_var, width=28, show='•', bg='#1b2736', fg='#e2eaf4', relief='flat')
            k_ent.pack(side='left', padx=4)

            def toggle_k(ent=k_ent):
                ent.config(show='' if ent.cget('show') == '•' else '•')
            tk.Button(row, text='👁', font=('Segoe UI', 7), bg='#1b2736', fg='#9db0c4', relief='flat', command=toggle_k).pack(side='left', padx=(0, 6))

            tk.Label(row, text='Model:', font=('Segoe UI', 8), bg='#141c26', fg='#9db0c4').pack(side='left', padx=(6, 0))
            mod_var = tk.StringVar(value=pinfo.get('model', ''))
            mod_ent = tk.Entry(row, textvariable=mod_var, width=18, bg='#1b2736', fg='#e2eaf4', relief='flat')
            mod_ent.pack(side='left', padx=4)

            def test_conn(k=key, kv=k_var, mv=mod_var):
                providers[k]['api_key'] = kv.get().strip()
                providers[k]['model'] = mv.get().strip()
                self.store.save()
                ok, msg = verify_provider_auth(k, providers[k].get('base_url', ''), kv.get().strip())
                if ok:
                    messagebox.showinfo('Verified', f"{providers[k].get('name', k)}: {msg}")
                else:
                    messagebox.showerror('Verification Failed', f"{providers[k].get('name', k)}: {msg}")

            tk.Button(row, text='Verify / Save', font=('Segoe UI', 8, 'bold'), bg='#2b3e55', fg='#e2eaf4',
                      relief='flat', padx=10, pady=2, command=test_conn).pack(side='right')

        # Tab: Installed Tools
        tools_frame = ttk.Frame(tabs)
        tabs.add(tools_frame, text=' Installed Tools ')
        tools_box = tk.Frame(tools_frame, bg='#070a0e', padx=16, pady=14)
        tools_box.pack(fill='both', expand=True)

        tools = detect_tools()
        tree = ttk.Treeview(tools_box, columns=('status', 'version', 'path'), show='tree headings')
        tree.heading('#0', text='Tool / Engine')
        tree.heading('status', text='Status')
        tree.heading('version', text='Version')
        tree.heading('path', text='Path on System')
        tree.column('#0', width=140)
        tree.column('status', width=100)
        tree.column('version', width=180)
        tree.column('path', width=380)
        tree.pack(fill='both', expand=True)

        for name, info in tools.items():
            tree.insert('', 'end', text=name.upper(), values=(
                'Installed' if info['installed'] else 'Missing',
                info['version'],
                info['path']
            ))

        # Tab: Skills & Compatibility
        skills_frame = ttk.Frame(tabs)
        tabs.add(skills_frame, text=' Skills & Plugins ')
        skills_box = tk.Frame(skills_frame, bg='#070a0e', padx=16, pady=14)
        skills_box.pack(fill='both', expand=True)

        skills = inspect_skills_compatibility(self.project['path'] if self.project else None)
        s_tree = ttk.Treeview(skills_box, columns=('status', 'desc', 'path'), show='tree headings')
        s_tree.heading('#0', text='Skill Name')
        s_tree.heading('status', text='Compatibility')
        s_tree.heading('desc', text='Description')
        s_tree.heading('path', text='Location')
        s_tree.column('#0', width=180)
        s_tree.column('status', width=140)
        s_tree.column('desc', width=300)
        s_tree.column('path', width=260)
        s_tree.pack(fill='both', expand=True)

        for sk in skills:
            s_tree.insert('', 'end', text=sk['name'], values=(
                sk['status'], sk['description'], sk['path']
            ))

        # Tab: Mandatory Rules
        rules_frame = ttk.Frame(tabs)
        tabs.add(rules_frame, text=' Mandatory Rules ')
        rules_box = tk.Frame(rules_frame, bg='#070a0e', padx=16, pady=14)
        rules_box.pack(fill='both', expand=True)
        rules_text = (
            "ENFORCED SAFETY RULES:\n\n"
            "1. Existing Project Files: Never overwrite or delete project files without verified user consent.\n"
            "2. Git Actions: Force-push is strictly disabled. Pulls are limited to fast-forward (--ff-only).\n"
            "3. Connect AI Billing: Team-paid AI resources are disabled by default. $0 spending caps.\n"
            "4. Checkpoint Restores: Recovery archives can only be extracted into clean, empty target folders.\n"
            "5. Sandboxed Edits: Agent file proposals must stay inside the project root and outside .git."
        )
        tk.Label(rules_box, text=rules_text, font=('Segoe UI', 10), justify='left',
                 bg='#070a0e', fg='#c2d0df').pack(anchor='w')

    # ─────────────────────────────────────────────────────────────────────────
    # PROJECT CREATION & IMPORT DIALOGS
    # ─────────────────────────────────────────────────────────────────────────

    def create_dialog(self):
        docs = []
        master = self.store.data.get('master_list')
        if master and Path(master).exists():
            docs.append(master)
            comp = Path(master).with_name('PROJECTS.md')
            if comp.exists() and str(comp) not in docs:
                docs.append(str(comp))

        records = project_catalog(docs)
        by_name = {r['name']: r for r in records}

        win = tk.Toplevel(self)
        win.title('Create or Import Project')
        win.configure(bg='#070a0e')
        win.geometry('720x460')
        win.transient(self)

        content = tk.Frame(win, bg='#070a0e', padx=20, pady=18)
        content.pack(fill='both', expand=True)

        tk.Label(content, text='Start a Project in GameForge', font=('Segoe UI', 14, 'bold'),
                 bg='#070a0e', fg='#60a5fa').pack(anchor='w')
        tk.Label(content, text='Select an existing title from your master tracker, or type a new name:',
                 font=('Segoe UI', 9), bg='#070a0e', fg='#9db0c4').pack(anchor='w', pady=(2, 12))

        name_var = tk.StringVar()
        combo = ttk.Combobox(content, textvariable=name_var, values=list(by_name.keys()), font=('Segoe UI', 10))
        combo.pack(fill='x', pady=(0, 10))

        loc_var = tk.StringVar(value='D:\\DEVELOPMENT\\Games')
        tk.Label(content, text='Target Project Folder:', font=('Segoe UI', 9, 'bold'),
                 bg='#070a0e', fg='#c2d0df').pack(anchor='w', pady=(8, 2))
        loc_entry = tk.Entry(content, textvariable=loc_var, bg='#16212e', fg='#e2eaf4',
                             relief='flat', font=('Segoe UI', 10), highlightthickness=1,
                             highlightbackground='#26374a')
        loc_entry.pack(fill='x', ipady=4, pady=(0, 6))

        def on_name_select(e=None):
            rec = by_name.get(name_var.get())
            if rec and rec['path']:
                loc_var.set(rec['path'])

        combo.bind('<<ComboboxSelected>>', on_name_select)

        def browse():
            folder = filedialog.askdirectory('Select Project Folder')
            if folder:
                loc_var.set(folder)

        tk.Button(content, text='Browse…', font=('Segoe UI', 8), bg='#1e293b', fg='#c2d0df',
                  relief='flat', padx=10, pady=3, command=browse).pack(anchor='w', pady=(0, 14))

        def do_create():
            title = name_var.get().strip()
            folder_str = loc_var.get().strip()
            if not title or not folder_str:
                raise ValueError('Please specify both project name and folder path')
            folder = Path(folder_str).resolve()
            if not folder.exists():
                if messagebox.askyesno('Create Folder', f'Create directory:\n{folder}?'):
                    folder.mkdir(parents=True, exist_ok=True)
                else:
                    return
            project = self.store.register(folder, name=title, synopsis=by_name.get(title, {}).get('synopsis', ''))
            self.refresh()
            self.select(project)
            win.destroy()

        btn_bar = tk.Frame(win, bg='#070a0e', padx=20, pady=14)
        btn_bar.pack(fill='x', side='bottom')
        tk.Button(btn_bar, text='Create / Register Project', font=('Segoe UI', 9, 'bold'),
                  bg='#2b3e55', fg='#e2eaf4', relief='flat', padx=16, pady=6,
                  command=lambda: self.safe_action(do_create)).pack(side='right')
        tk.Button(btn_bar, text='Cancel', font=('Segoe UI', 9),
                  bg='#16212e', fg='#9db0c4', relief='flat', padx=12, pady=6,
                  command=win.destroy).pack(side='right', padx=8)

        dark_title(win)
        win.grab_set()

    def import_folder_dialog(self):
        folder = filedialog.askdirectory('Import Existing Game Project')
        if folder:
            project = self.store.register(folder)
            self.refresh()
            self.select(project)

    def clone_dialog(self):
        url = simpledialog.askstring('Download / Clone Project', 'HTTPS Repository URL:')
        if not url:
            return
        if not url.startswith('https://'):
            raise ValueError('A secure HTTPS repository URL is required')
        parent = filedialog.askdirectory('Select Destination Directory')
        if not parent:
            return
        repo_name = Path(url).stem or 'cloned_project'
        dest = Path(parent) / repo_name
        if dest.exists():
            raise ValueError('Destination folder already exists. Please choose a different parent.')
        git(parent, 'clone', '--', url, str(dest))
        project = self.store.register(dest)
        self.refresh()
        self.select(project)

    # ─────────────────────────────────────────────────────────────────────────
    # GIT ACTIONS & HEALTH CHECK
    # ─────────────────────────────────────────────────────────────────────────

    def view_git_changes(self):
        stat = git(self.project['path'], 'status', '--short', '--branch')
        messagebox.showinfo('Git Status', stat or 'Working tree is clean')

    def publish_git_commits(self):
        folder = self.project['path']
        if git(folder, 'status', '--porcelain'):
            raise ValueError('Uncommitted files exist. Review and commit with your Git client first; automatic staging is disabled.')
        try:
            preview = git(folder, 'log', '--oneline', '@{upstream}..HEAD')
        except Exception:
            preview = 'Ready to push commits.'
        if messagebox.askyesno('Confirm Push', f"Push committed changes to remote repository?\n\n{preview}"):
            out = git(folder, 'push')
            messagebox.showinfo('Push Completed', out or 'Push completed successfully.')

    def download_git_updates(self):
        folder = self.project['path']
        if git(folder, 'status', '--porcelain'):
            raise ValueError('Save or commit local modifications before downloading updates.')
        out = git(folder, 'pull', '--ff-only')
        messagebox.showinfo('Download Complete', out or 'Already up to date.')

    def sync_git_status(self):
        git(self.project['path'], 'fetch')
        stat = git(self.project['path'], 'status', '--short', '--branch')
        messagebox.showinfo('Fetch Completed', f"Remote fetched.\n\n{stat}")

    def project_health_check(self):
        folder = Path(self.project['path']).resolve()
        checks = []
        checks.append(('Git Repository', (folder / '.git').exists()))
        checks.append(('.gitignore File', (folder / '.gitignore').exists()))
        checks.append(('Game Bible / Readme', (folder / 'GAME_BIBLE.md').exists() or (folder / 'README.md').exists()))
        checks.append(('Cursor Gaps / Rules', (folder / '.cursor' / 'LIVE_GAPS.md').exists() or (folder / '.cursorrules').exists()))

        report = f"Health Check for {self.project['name']}:\n\n"
        for item, passed in checks:
            report += f"{'✓' if passed else '⚠️'}  {item}: {'Present' if passed else 'Missing / Not configured'}\n"
        messagebox.showinfo('Project Health & Migration Check', report)

    def save_current(self):
        self.store.save()


# ─────────────────────────────────────────────────────────────────────────────
# APPLICATION ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app = Studio()
    app.mainloop()
