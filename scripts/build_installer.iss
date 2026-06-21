[Setup]
AppName=Hutrol Agentic Harness
AppVersion=0.1.0
DefaultDirName={pf}\HutrolHarness
DefaultGroupName=Hutrol Harness
OutputDir=dist
OutputBaseFilename=HutrolSetup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
ChangesEnvironment=yes

[Files]
; This assumes PyInstaller has already built the binary in dist\hutrol.exe
Source: "..\dist\hutrol.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\skills\*"; DestDir: "{app}\skills"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
Name: "envPath"; Description: "Add Hutrol to system PATH environment variable"; GroupDescription: "Additional configuration:"; Flags: unchecked

[Registry]
; Add the app directory to the user's PATH so they can use the `hutrol` CLI anywhere
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; Tasks: envPath; Check: NeedsAddPath(ExpandConstant('{app}'))

[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OrigPath)
  then begin
    Result := True;
    exit;
  end;
  // look for the path with leading and trailing semicolon
  // Pos() returns 0 if not found
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;
