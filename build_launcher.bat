@echo off
set CSC=%SystemRoot%\Microsoft.NET\Framework64\v4.0.30319\csc.exe
if not exist "%CSC%" set CSC=%SystemRoot%\Microsoft.NET\Framework\v4.0.30319\csc.exe

echo Compiling Airport FWD Data Analyzer launcher...
"%CSC%" /target:winexe /platform:anycpu /optimize+ ^
  /win32icon:assets\app.ico ^
  /resource:assets\airport-fwd-data-analyzer-logo.png,AirportFwdDataAnalyzer.logo.png ^
  /out:airport-fwd-data-analyzer.exe ^
  src\Launcher\Program.cs ^
  src\Launcher\LauncherForm.cs ^
  src\Launcher\Properties\AssemblyInfo.cs

if %ERRORLEVEL% EQU 0 (
  echo Build successful: airport-fwd-data-analyzer.exe
) else (
  echo Build failed with error %ERRORLEVEL%
)
