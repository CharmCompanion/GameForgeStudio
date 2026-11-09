$ErrorActionPreference = 'Stop'
$project = $PSScriptRoot
$environment = Join-Path $project '.build-env'
if (!(Test-Path "$environment/Scripts/python.exe")) {
    python -m venv $environment
    if ($LASTEXITCODE -ne 0) { throw 'Python environment creation failed' }
}
& "$environment/Scripts/python.exe" -m pip install 'pyinstaller==6.22.3'
if ($LASTEXITCODE -ne 0) { throw 'Packaging dependency installation failed' }
& "$environment/Scripts/python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed --name GameForgeStudio --distpath "$project/Release" --workpath "$project/.build" --specpath "$project/.build" "$project/app.py"
if ($LASTEXITCODE -ne 0) { throw 'Executable packaging failed' }
