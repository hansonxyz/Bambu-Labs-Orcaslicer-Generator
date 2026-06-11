; Inno Setup script for the OrcaSlicer Profile Generator (Windows installer).
;
; Wraps the PyInstaller one-file build (dist\OrcaConfGen.exe) into a per-user
; setup executable - no administrator rights required. Installing per-user puts
; the app under %LOCALAPPDATA%\Programs so the generator can write config.json
; and backups\ next to its own executable.
;
; Build:  iscc installer.iss   (after: pyinstaller --noconfirm OrcaConfGen.spec)
; Output: Output\OrcaConfGen-Setup-<version>.exe
;
; Pass /DMyAppVersion=x.y.z to stamp a version; defaults to 1.0.0.

#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif

#define MyAppName "OrcaSlicer Profile Generator"
#define MyAppExeName "OrcaConfGen.exe"
#define MyAppPublisher "Brian Hanson"
#define MyAppURL "https://github.com/hansonxyz/Bambu-Labs-Orcaslicer-Generator"

[Setup]
AppId={{B7B3E4B2-5C9A-4D3E-9A1F-0C0F0A0R0C0G}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\OrcaConfGen
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=Output
OutputBaseFilename=OrcaConfGen-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\OrcaConfGen.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
