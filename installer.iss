; spjss installer script for Inno Setup 6
; build: iscc installer.iss

#define AppName "spjss"
#define AppVersion "0.3.0"
#define AppPublisher "mroczect"
#define AppURL "https://github.com/mroczect/librjss"
#define AppExeName "spjss.exe"

[Setup]
AppId={{8F2C3A4D-1B5E-4F6A-9D8C-7E0A1B2C3D4E}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
AppUpdatesURL={#AppURL}/releases
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} installer
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}

DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
UninstallDisplayName={#AppName} {#AppVersion}

; ── icon ─────────────────────────────────────────────────────────────
SetupIconFile=assets\spjss.ico                 ; icon di file installer
UninstallDisplayIcon={app}\{#AppExeName}       ; icon di Add/Remove Programs

OutputDir=installer_out
OutputBaseFilename=spjss-setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; ── update-related flags ─────────────────────────────────────────────
SetupMutex=spjss_setup_mutex
CloseApplications=yes
CloseApplicationsFilter=*.exe
RestartApplications=yes

AllowNoIcons=yes
LicenseFile=src\spjss\data\license.txt

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; \
  Description: "{cm:LaunchProgram,{#AppName}}"; \
  Flags: nowait postinstall skipifsilent runasoriginaluser

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\spjss"; Check: ShouldRemoveUserData

[Code]
function ShouldRemoveUserData(): Boolean;
begin
  Result :=
    UninstallSilent or
    (MsgBox(
      'Remove your spjss settings and presets?' + #13#10 +
      'Location: %APPDATA%\spjss' + #13#10#13#10 +
      'Choose No to keep them for a future reinstall.',
      mbConfirmation, MB_YESNO) = IDYES);
end;
