# airport-fwd-data-analyzer build notes

Build date: 15 October 2026

## Branded launcher

- Name: Airport FWD Data Analyzer
- Executable: `airport-fwd-data-analyzer.exe`
- Product version: 1.0.0
- Company/copyright metadata: Sahil Yadav / Copyright © 2026 Sahil Yadav
- Support contact: skonetechsupport@gmail.com
- Original logo embedded as the Windows application icon and launcher artwork
- Target: .NET Framework 4.8, Release / Any CPU
- Result: successful build, 0 errors

## BAKFAA

- Source: `ATRD_BAKFAA-3.4.4-Source-code.zip`
- Configuration: Release / Any CPU
- Target: .NET Framework 4.8
- Result: successful build, 0 errors
- Output: `BAKFAA_3.4.4_Portable/BAKFAA.exe`
- Product version: 3.4.4.0

Portable build inputs restored from their official NuGet packages:

- Microsoft.NETFramework.ReferenceAssemblies.net48 1.0.3 (build-only)
- System.Windows.Interactivity.WPF 2.0.20525
- Microsoft.Xaml.Behaviors.Wpf 1.1.3
- MicrosoftOfficeCore 15.0.0 (build-only; no runtime Office dependency was emitted)
- SharpDX / SharpDX.D3DCompiler 2.5.0 (runtime support for Telerik Direct2D charts)
- WPFToolkit 3.5.50211.1

The source archive's four unused COM references (ADODB, Office Core, Excel, and VBIDE) were removed from the workspace build copy to avoid requiring Office and AxImp/TlbImp tools. A text search confirmed that their types are not used by the current source. The original source archive remains unchanged.

## FAARFIELD

- Source: `20260615_FAARFIELD_SourceCode.zip`
- Delivered artifact: the archive's existing Release MSI
- Application version stated by the supplied README and debug executable: 2.1.2.0
- Installer project package version: 2.2.0.0

## Important verification boundary

The package was inspected, rebuilt, dependency-checked, and hashed. A recursive static scan checked the rebuilt BAKFAA executable and 32 local assemblies with no unresolved assembly dependencies. The branded launcher also passed build and static metadata validation. No executable or installer was launched, so final GUI and installation smoke tests remain to be performed on a Windows test machine.
