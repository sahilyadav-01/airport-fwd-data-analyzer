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

## Backcalculation application

- Source: `ATRD_BAKFAA-3.4.4-Source-code.zip`
- Configuration: Release / Any CPU
- Target: .NET Framework 4.8
- Result: successful build, 0 errors
- Branded product: Airport FWD Data Analyzer - Backcalculation
- Output: `Airport_FWD_Backcalculation/AirportFWD.Backcalculation.exe`
- Company/copyright metadata: Sahil Yadav / Copyright © 2026 Sahil Yadav
- Support contact displayed in the application: skonetechsupport@gmail.com
- Product version: 3.4.4.0

Portable build inputs restored from their official NuGet packages:

- Microsoft.NETFramework.ReferenceAssemblies.net48 1.0.3 (build-only)
- System.Windows.Interactivity.WPF 2.0.20525
- Microsoft.Xaml.Behaviors.Wpf 1.1.3
- MicrosoftOfficeCore 15.0.0 (build-only; no runtime Office dependency was emitted)
- SharpDX / SharpDX.D3DCompiler 2.5.0 (runtime support for Telerik Direct2D charts)
- WPFToolkit 3.5.50211.1

The source archive's four unused COM references (ADODB, Office Core, Excel, and VBIDE) were removed from the workspace build copy to avoid requiring Office and AxImp/TlbImp tools. A text search confirmed that their types are not used by the current source. The original source archive remains unchanged.

## Pavement Design application

- Source: `20260615_FAARFIELD_SourceCode.zip`
- Configuration: Release / Any CPU
- Target: .NET Framework 4.8
- Result: successful build, 0 errors
- Branded product: Airport FWD Data Analyzer - Pavement Design
- Output: `Airport_FWD_Pavement_Design/AirportFWD.PavementDesign.exe`
- Company/copyright metadata: Sahil Yadav / Copyright © 2026 Sahil Yadav
- Support contact displayed in the application: skonetechsupport@gmail.com
- Engineering engine version: 2.1.2.0
- The unused Microsoft Scripting Runtime COM reference and four unused declarations were removed from the workspace build copy because all operational calls were already commented out and the reference required unavailable legacy AxImp tooling.

## Important verification boundary

The package was inspected, rebuilt, dependency-checked, and hashed. Both rebuilt applications and the branded launcher passed build and static metadata validation. No executable was launched, so final GUI smoke tests remain to be performed on a Windows test machine.
