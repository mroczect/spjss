@echo off
setlocal

echo === sync deps ===
uv sync --extra dev || goto :err

echo === clean ===
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo === pyinstaller ===
uv run pyinstaller spjss.spec --clean --noconfirm || goto :err

echo === inno setup ===
if not exist installer_out mkdir installer_out
iscc installer.iss || goto :err

echo.
echo DONE: installer_out\spjss-setup-0.2.2.exe
goto :eof

:err
echo.
echo BUILD FAILED
exit /b 1
