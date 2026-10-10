@echo off
setlocal

uv sync --extra dev || goto :err

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

uv run pyinstaller spjss.spec --clean --noconfirm || goto :err

if not exist installer_out mkdir installer_out
iscc installer.iss || goto :err

echo.
echo done: installer_out\spjss-setup-0.3.1.exe
exit /b 0

:err
echo.
echo build failed
exit /b 1
