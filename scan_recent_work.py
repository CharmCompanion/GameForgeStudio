import os
import datetime
from pathlib import Path

root = Path(r"D:\DEVELOPMENT")
cutoff = datetime.datetime.now() - datetime.timedelta(days=90)
cutoff_ts = cutoff.timestamp()

results = []

def get_latest_mtime(p):
    latest = p.stat().st_mtime
    try:
        for root_d, dirs, files in os.walk(p):
            # prune heavy cache dirs
            dirs[:] = [d for d in dirs if d not in {'.git', 'Intermediate', 'Saved', 'DerivedDataCache', 'node_modules', '.vs', 'Binaries', 'Build'}]
            for f in files:
                try:
                    f_mtime = (Path(root_d) / f).stat().st_mtime
                    if f_mtime > latest:
                        latest = f_mtime
                except Exception:
                    pass
    except Exception:
        pass
    return latest

# Check all top level and immediate subfolders in Games, Unreal Projects, etc.
dirs_to_check = []
for p in root.iterdir():
    if p.is_dir():
        dirs_to_check.append(p)
        if p.name in ['Games', 'Unreal Projects', '_Active', 'Tools', 'Unity', 'UEFN', 'Ideas', 'Files']:
            try:
                for sub in p.iterdir():
                    if sub.is_dir():
                        dirs_to_check.append(sub)
            except Exception:
                pass

for d in dirs_to_check:
    mtime = get_latest_mtime(d)
    if mtime >= cutoff_ts:
        results.append((mtime, d))

results.sort(key=lambda x: x[0], reverse=True)

print("=" * 80)
print(f"PROJECTS TOUCHED IN THE LAST 90 DAYS (Since {cutoff.strftime('%Y-%m-%d')})")
print("=" * 80)
for mtime, p in results:
    dt = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
    print(f"{dt} | {p}")
print("=" * 80)
print(f"Total active/touched directories: {len(results)}")
