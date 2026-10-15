# airport-fwd-data-analyzer

![Airport FWD Data Analyzer logo](assets/airport-fwd-data-analyzer-logo.png)

**Airport FWD Data Analyzer** combines two supplied airport pavement-engineering engines behind one branded Windows launcher:

- **Backcalculation** — imports FWD/HWD data and backcalculates pavement layer properties.
- **Pavement Design** — performs airport pavement thickness and overlay design.

## System requirements

- Windows 10 or newer
- .NET Framework 4.8
- At least 4 GB RAM (more is recommended for larger analyses)

## Install and run

### Recommended launcher

Run `airport-fwd-data-analyzer.exe` from the package root. The branded launcher opens Backcalculation, Pavement Design, and the supplied manuals.

### Backcalculation

1. Open `Airport_FWD_Backcalculation`.
2. Run `AirportFWD.Backcalculation.exe`.
3. Keep the EXE, DLLs, `Data`, and `Defaults` folders together. Do not move only the EXE.

The Backcalculation application is portable; it does not require an installer. Its supplied help file is in the same folder. The full user manual and presentation are in `Manuals`.

### Pavement Design

1. Open `Airport_FWD_Pavement_Design`.
2. Run `AirportFWD.PavementDesign.exe`.
3. Keep the EXE, DLLs, `Defaults`, and `Resources` folders together.

This is a portable Release build from the supplied pavement-design source. The engine version remains 2.1.2 for compatibility and traceability.

## Typical workflow

1. Use Backcalculation to import and review FWD/HWD measurements.
2. Backcalculate layer moduli and review the fit/error indicators.
3. Export or record the evaluated pavement structure and material properties.
4. Use the evaluated structure, traffic mix, and design criteria in Pavement Design for pavement or overlay design.

Engineering judgment and the applicable FAA advisory circular remain controlling. Review units, layer definitions, aircraft traffic, design life, and reliability inputs before relying on results.

## Build and verification status

- Both Backcalculation and Pavement Design were rebuilt from the supplied source in **Release** configuration against .NET Framework 4.8.
- Their engineering engine versions remain **3.4.4.0** and **2.1.2.0**, respectively.
- Both builds completed with no errors. The legacy source still emits compiler warnings about obsolete compatibility APIs and possibly uninitialized variables; calculation code was not silently rewritten.
- Unused legacy COM references were removed only where their types were not used and they blocked modern build tools. The supplied source ZIP files were not modified.
- Neither supplied application is digitally signed. Windows may show a SmartScreen or publisher warning.
- The binaries were statically checked and hashed. They were not launched during packaging.

See `SHA256SUMS.txt` for integrity hashes and `Manuals` for the supplied documentation.

## Branding and copyright

The Airport FWD Data Analyzer name, logo, launcher, branding modifications, and original packaging documentation are **Copyright © 2026 Sahil Yadav**.

The underlying third-party engines, source code, manuals, trademarks, and existing notices retain their original ownership. See `NOTICE.md`.

Project repository: <https://github.com/sahilyadav-01/airport-fwd-data-analyzer>

## Support

Email: [skonetechsupport@gmail.com](mailto:skonetechsupport@gmail.com)
