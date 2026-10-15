# airport-fwd-data-analyzer

![Airport FWD Data Analyzer logo](assets/airport-fwd-data-analyzer-logo.png)

**Airport FWD Data Analyzer** combines the two supplied FAA pavement-engineering tools:

- **BAKFAA 3.4.4 Portable** — imports FWD/HWD data and backcalculates pavement layer properties.
- **FAARFIELD** — performs FAA airport pavement thickness and overlay design.

## System requirements

- Windows 10 or newer
- .NET Framework 4.8
- Administrator permission for the FAARFIELD installer
- At least 4 GB RAM (more is recommended for larger analyses)

## Install and run

### Recommended launcher

Run `airport-fwd-data-analyzer.exe` from the package root. The branded launcher provides buttons for BAKFAA, the FAARFIELD installer, and the supplied manuals.

### BAKFAA 3.4.4

1. Open `BAKFAA_3.4.4_Portable`.
2. Run `BAKFAA.exe`.
3. Keep the EXE, DLLs, `Data`, and `Defaults` folders together. Do not move only the EXE.

BAKFAA is portable; it does not require an installer. Its help file is `BAKFAA.chm` in the same folder. The full user manual and presentation are in `Manuals`.

### FAARFIELD

1. Open `FAARFIELD`.
2. Run `FAARFIELD.Installer.msi`.
3. Follow the installer prompts and restart Windows if requested.

The supplied FAARFIELD documentation identifies the application as version 2.1.2 (15 June 2026). The installer project's internal package version is 2.2.0.0; the installer has been preserved exactly as supplied.

## Typical workflow

1. Use BAKFAA to import and review FWD/HWD measurements.
2. Backcalculate layer moduli and review the fit/error indicators.
3. Export or record the evaluated pavement structure and material properties.
4. Use the evaluated structure, traffic mix, and design criteria in FAARFIELD for pavement or overlay design.

Engineering judgment and the applicable FAA advisory circular remain controlling. Review units, layer definitions, aircraft traffic, design life, and reliability inputs before relying on results.

## Build and verification status

- BAKFAA was rebuilt from the supplied source in **Release** configuration against .NET Framework 4.8.
- The rebuilt executable reports product/file version **3.4.4.0**.
- The build completed with no errors. The legacy source still emits compiler warnings about obsolete compatibility APIs and possibly uninitialized variables; these were not silently rewritten.
- Four unused legacy COM references were removed from the workspace build copy because the supplied source does not use their types and they required Office/Windows SDK import tools. The original ZIP was not modified.
- FAARFIELD is the prebuilt MSI contained in the supplied source archive.
- Neither supplied application is digitally signed. Windows may show a SmartScreen or publisher warning.
- The binaries were statically checked and hashed. They were not installed or launched during packaging.

See `SHA256SUMS.txt` for integrity hashes and `Manuals` for the supplied documentation.

## Branding and copyright

The Airport FWD Data Analyzer name, launcher, logo, and original packaging documentation are **Copyright © 2026 Sahil Yadav**.

BAKFAA, FAARFIELD, their source code, manuals, trademarks, and existing notices retain their original ownership. See `NOTICE.md`.

Project repository: <https://github.com/sahilyadav-01/airport-fwd-data-analyzer>

## Support

Email: [skonetechsupport@gmail.com](mailto:skonetechsupport@gmail.com)
