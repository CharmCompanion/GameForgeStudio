@echo off
echo ==========================================================
echo  GameForge Studio - CharmCompanion Certificate Installer
echo ==========================================================
echo Installing publisher certificate to Windows Trusted Root and Trusted Publisher stores...
certutil -addstore -f "Root" "%~dp0CharmCompanion_GameForge.cer"
certutil -addstore -f "TrustedPublisher" "%~dp0CharmCompanion_GameForge.cer"
echo.
echo Certificate installation complete. GameForge Studio is now trusted on this PC.
pause