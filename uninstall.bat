@echo off
setlocal enabledelayedexpansion

net session >nul 2>&1
if errorlevel 1 (
  powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)

title spjss clean
echo.
echo ==== spjss clean ====
echo.

echo [1/8] stopping processes
taskkill /f /im spjss.exe       >nul 2>&1
taskkill /f /im spjss-setup.exe >nul 2>&1
taskkill /f /im unins000.exe    >nul 2>&1
timeout /t 1 /nobreak >nul

set "APPDIR=%LOCALAPPDATA%\Programs\spjss"
set "UNINST=%APPDIR%\unins000.exe"
if exist "%UNINST%" (
  echo [2/8] running uninstaller
  "%UNINST%" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
  timeout /t 3 /nobreak >nul
) else (
  echo [2/8] no uninstaller found
)

echo [3/8] removing folders
for %%P in (
  "%LOCALAPPDATA%\Programs\spjss"
  "%ProgramFiles%\spjss"
  "%ProgramFiles(x86)%\spjss"
  "%APPDATA%\spjss"
  "%LOCALAPPDATA%\spjss"
  "%ProgramData%\spjss"
) do if exist "%%~P" (
  rd /s /q "%%~P" 2>nul
  if exist "%%~P" (
    takeown /f "%%~P" /r /d y >nul 2>&1
    icacls "%%~P" /grant *S-1-5-32-544:F /t /c >nul 2>&1
    rd /s /q "%%~P" 2>nul
  )
)

echo [4/8] removing shortcuts
rd /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\spjss" 2>nul
rd /s /q "%ProgramData%\Microsoft\Windows\Start Menu\Programs\spjss" 2>nul
del /f /q "%USERPROFILE%\Desktop\spjss.lnk" 2>nul
del /f /q "%PUBLIC%\Desktop\spjss.lnk" 2>nul

echo [5/8] removing registry
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\{8F2C3A4D-1B5E-4F6A-9D8C-7E0A1B2C3D4E}_is1" /f >nul 2>&1
reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\{8F2C3A4D-1B5E-4F6A-9D8C-7E0A1B2C3D4E}_is1" /f >nul 2>&1
reg delete "HKLM\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\{8F2C3A4D-1B5E-4F6A-9D8C-7E0A1B2C3D4E}_is1" /f >nul 2>&1
reg delete "HKCU\Software\spjss" /f >nul 2>&1
reg delete "HKLM\Software\spjss" /f >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v spjss /f >nul 2>&1

echo [6/8] removing credentials
for /f "tokens=1,* delims=:" %%A in ('cmdkey /list ^| findstr /i "Target:.*spjss"') do (
  set "T=%%B"
  set "T=!T:~1!"
  cmdkey /delete:"!T!" >nul 2>&1
  for /f "tokens=2 delims==" %%U in ("!T!") do cmdkey /delete:"%%U" >nul 2>&1
)

echo [7/8] removing temp files
del /f /q "%TEMP%\spjss-setup-*.exe" 2>nul
for /d %%D in ("%TEMP%\_MEI*") do if exist "%%D\spjss.exe" rd /s /q "%%D" 2>nul

echo [8/8] refreshing shell cache
ie4uinit.exe -show >nul 2>&1

echo.
echo ==== verification ====
set LEFT=0
for %%P in (
  "%LOCALAPPDATA%\Programs\spjss"
  "%ProgramFiles%\spjss"
  "%ProgramFiles(x86)%\spjss"
  "%APPDATA%\spjss"
  "%LOCALAPPDATA%\spjss"
  "%ProgramData%\spjss"
) do if exist "%%~P" (
  echo   left: %%~P
  set /a LEFT+=1
)
reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall" 2>nul | findstr /i spjss >nul && (
  echo   left: HKLM uninstall key
  set /a LEFT+=1
)
tasklist 2>nul | findstr /i spjss.exe >nul && (
  echo   left: spjss.exe still running
  set /a LEFT+=1
)
if !LEFT! equ 0 (echo   ok, clean) else (echo   !LEFT! item^(s^) remain)
echo.
pause
