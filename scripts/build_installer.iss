[Setup]
AppName=Human Agentic Harness
AppVersion=0.1.0
DefaultDirName={pf}\HumanHarness
DefaultGroupName=Human Harness
OutputDir=dist
OutputBaseFilename=HumanSetup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Files]
; This assumes PyInstaller has already built the binary in dist\human.exe
Source: "..\dist\human.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\skills\*"; DestDir: "{app}\skills"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Human Harness Shell"; Filename: "cmd.exe"; Parameters: "/K ""{app}\human.exe repl"""
Name: "{commondesktop}\Human Harness"; Filename: "{app}\human.exe"; Parameters: "repl"

[Registry]
; Add the app directory to the user's PATH so they can use the `human` CLI anywhere
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; Check: NeedsAddPath(ExpandConstant('{app}'))

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
