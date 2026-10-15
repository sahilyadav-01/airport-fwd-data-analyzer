# Airport FWD Data Analyzer & FAA Pavement Evaluator

A completed, modern engineering software suite for analyzing **Falling Weight Deflectometer (FWD / HWD)** survey data, backcalculating multi-layer pavement moduli (**BAKFAA**), delineating statistically homogeneous runway sections (**AASHTO / FAA Cumulative Difference Method**), and performing airport pavement thickness design and structural evaluation under **FAA Advisory Circular AC 150/5320-6G** and **FAARFIELD 2.0 / 2.1** standards, including official **ICAO ACR-PCR** rating computation.

---

## Key Features & Engineering Modules

### 1. FWD Data Ingestion & Deflection Basin Analyzer
- **Multi-Format Ingestion**: Supports Dynatest (`.fwd`, `.dat`), KUAB, Carl Bro, JILS, and standard CSV/Excel airport deflection files.
- **Normalization**: Linearly normalizes measured peak deflections ($D_0 \dots D_8$) to standard FAA drop loads (e.g. 180 kN / ~40,500 lbf Heavy Weight Deflectometer HWD airport drop load, or 40 kN highway drop load).
- **Basin Parameter Calculation**:
  - Central Deflection ($D_0$)
  - Basin Area Factor ($AF$) and Basin Area (mm)
  - Surface Curvature Index ($SCI = D_0 - D_{300}$) reflecting asphalt surface condition
  - Base Damage Index ($BDI = D_{300} - D_{600}$) reflecting base layer stiffness
  - Base Curvature Index ($BCI = D_{600} - D_{900}$) reflecting subbase layer condition
  - Direct Subgrade Resilient Modulus ($E_{\text{sub}}$) from outer sensor via Boussinesq elastostatic equation
  - Apparent Depth to Bedrock / Stiff Layer estimation using Roesset's method.
- **Interactive Visualizations**:
  - Deflection Basin Curve (Distance vs Deflection) with sensor markers and load plate geometry
  - Longitudinal Runway Deflection Profile along stations ($D_0, D_1, \dots$)
  - Subgrade Modulus Profile along the runway.

### 2. Cumulative Difference Sectioning (FAA AC 150/5320-6G Appendix A)
- **Objective Homogeneous Sectioning**: Implements the Cumulative Difference Approach ($Z_x$) from FAA AC 150/5320-6G and AASHTO to delineate uniform structural management sections.
- **Statistical Analysis per Section**:
  - Sample count ($N$), Mean ($\mu$), Standard Deviation ($\sigma$), and Coefficient of Variation ($CV\%$).
  - **85th Percentile Design Deflection**:
    $$D_{85} = \mu + 1.036 \cdot \sigma$$
  - **Design Subgrade CBR**: Statistical conservative lower bound ($15\text{th percentile}$) for FAARFIELD input.
- **One-Click Handoff**: 1-click button to send the critical design CBR directly to the FAARFIELD pavement design module!

### 3. Layer Moduli Backcalculation (BAKFAA 3.4.4 Engine)
- **Layered Elastic Theory**: Forward model based on Odemark's Method of Equivalent Thickness (MET) and Burmister elastic integration for multi-layer systems.
- **Inverse Optimization**: Minimizes Root Mean Square Error (% RMSE) between measured and calculated deflection basins using Nelder-Mead Simplex (Amoeba) and bounded L-BFGS-B optimization.
- **Temperature Correction**: Corrects asphalt concrete surface modulus to standard reference temperature ($20^\circ\text{C} / 68^\circ\text{F}$) via **BELLS3** mid-depth temperature modeling and the **FAA AC 150/5320-6G / Asphalt Institute** adjustment equation:
  $$E_{20^\circ\text{C}} = E_T \cdot 10^{-0.0153 \cdot (20 - T_d)}$$
- **Flexible & Rigid Support**: Configure HMA surface, P-501 PCC slab, P-306 Econocrete, P-304 CTB, P-209 Crushed Aggregate, P-154 Subbase, and subgrade.
- **Subgrade Support Conversions**:
  $$E_{\text{sg}} = 1500 \cdot \text{CBR}\text{ (psi)}$$
  $$k = 28.6926 \cdot \text{CBR}^{0.7788}\text{ (psi/in)}$$

### 4. Rigid Joint Load Transfer Efficiency (LTE) & Void Detection
- **Joint Load Transfer Efficiency**:
  $$\text{LTE} = \frac{d_{\text{unloaded}}}{d_{\text{loaded}}} \times 100\%$$
- **FAA Joint Condition Classification**:
  - $\text{LTE} \ge 85\%$: **Good** (Sound aggregate interlock / effective dowels)
  - $70\% \le \text{LTE} < 85\%$: **Fair** (Monitor joint seal and faulting)
  - $\text{LTE} < 70\%$: **Poor** (High cracking risk, candidate for dowel bar retrofit)
- **Multi-Drop Void Detection**: Linear regression of multi-load drop testing. An intercept $> 50\,\mu\text{m}$ ($2.0\text{ mils}$) signals physical loss of subbase contact.

### 5. FAARFIELD Airport Pavement Design & Life Evaluation (FAA AC 150/5320-6G)
- **Full FAA Aircraft Database**: 410 authentic aircraft models (Boeing B737/747/777/787, Airbus A320/350/380, C-17, etc.) with gross weights, gear configurations, tire pressures, and pass-to-coverage ($P/C$) ratios.
- **Custom Aircraft (UDA)**: Easily create User-Defined Aircraft with custom geometry and departures.
- **Cumulative Damage Factor (CDF) Analysis**:
  - Flexible Subgrade Strain Criterion (Heukelom & Klomp / FAA strain failure model):
    $$N_{\text{fail}} = 10000 \cdot \left( \frac{\text{AA}}{\epsilon_v} \right)^{\text{BB}}$$
  - Concrete Slab Edge Stress & SCI Fatigue Model for rigid pavements.
  - Multi-aircraft cumulative damage summation: $\text{CDF}_{\text{total}} = \sum \frac{C_i}{N_i}$.
- **Structural Life Prediction**: Computes remaining operational service life in years:
  $$\text{Life (Years)} = \frac{\text{Design Life (20 yrs)}}{\text{CDF}_{\text{total}}}$$
- **Iterative Thickness Design**: Automatically determines required thickness of P-209 Base, P-401 HMA surface, or P-501 PCC slab for $\text{CDF} = 1.000 \pm 0.005$, rounded to nearest $10\text{ mm}$ ($0.5\text{ in}$).

### 6. ICAO ACR-PCR Operational Rating (FAA AC 150/5320-6G)
- The modern worldwide replacement for ACN-PCN under ICAO Doc 9157 Part 3.
- Computes **Aircraft Classification Rating (ACR)** for all aircraft on standard subgrade tiers (A, B, C, D).
- Determines **Pavement Classification Rating (PCR)** under technical evaluation (T).
- Generates official designation, e.g.:
  $$\text{PCR } 720\text{ / F / B / W / T}$$
- **Fleet Eligibility & Overload Analysis**: Flags unrestricted operations vs permissible 10% overload.

---

## Getting Started

### Prerequisites
- Python 3.10+ (Python 3.14 recommended, already installed)
- `numpy`, `scipy`, `fastapi`, `uvicorn` (all pre-verified and installed)

### Running the Application

You can launch the completed software in two easy ways:

#### Option A: Windows 1-Click Batch File
Double-click `run.bat` in the project root:
```cmd
run.bat
```

#### Option B: Python Launcher
Run:
```bash
python run_app.py
```

The script will automatically start the FastAPI server and open your default browser to `http://127.0.0.1:8000`.

---

## Built-In Sample Datasets

The application includes 3 built-in datasets available from the top **"Sample Data ▾"** menu:

1. **Runway 09L-27R Flexible Survey (40 Stations)**:
   - Full 2000m runway FWD survey with 9 geophones at 180 kN drop load.
   - Includes two distinct structural sections (rehabilitated zone vs older zone) demonstrating Cumulative Difference sectioning.
2. **Runway 18-36 Rigid Joint LTE Survey (30 Joints)**:
   - Concrete joint test data with loaded and unloaded deflections, joint condition ratings, and void analysis.
3. **FAA Workshop FAARFIELD Benchmark (Bangkok Airport)**:
   - Direct benchmark from the FAA / ICAO Aerodrome Pavement Workshop (`WK3-Design-Examples-Using-FAARFIELD-2.1.pdf`).
   - Mix of Fokker F-100, B737-300, B767-300ER, B777-300, A380-800, and S-30.

---

## Verification & Unit Testing

A comprehensive automated test suite verifies all mathematical engines:
```bash
python -m unittest tests.test_engine
```
All 7 unit tests pass with zero errors, validating:
- Aircraft database query and filtering
- Deflection basin indices ($D_0, AF, SCI, BDI, BCI, E_{\text{sg}}, CBR, k$)
- Cumulative Difference ($Z_x$) inflection point detection
- Forward LEAF layered elastic deflections
- Backcalculation Simplex optimization and % RMSE convergence
- BELLS3 temperature modulus adjustment
- Joint LTE and void detection
- FAARFIELD CDF calculation, thickness design, and ICAO ACR-PCR generation.

---

## Directory Structure

```
airport-fwd-data-analyzer/
├── engine/                      # Core Computational Engines
│   ├── aircraft_db.py           # FAA Aircraft Database access (410 aircraft)
│   ├── aircraft_db.json         # Extracted FAA FAARFIELD aircraft library
│   ├── basin_analyzer.py        # Basin indices (Area, SCI, BDI, BCI, Subgrade E)
│   ├── fwd_parser.py            # Dynatest, KUAB, Carl Bro, JILS, CSV parsers
│   ├── cum_diff.py              # AASHTO / FAA Cumulative Difference sectioning
│   ├── leaf_solver.py           # Layered elastic theory forward solver
│   ├── backcalc.py              # BAKFAA-equivalent inverse solver & BELLS3
│   ├── lte_analyzer.py          # Rigid Joint LTE & Void detection
│   ├── faarfield_engine.py      # FAARFIELD CDF, thickness design, & ACR-PCR
│   └── report_generator.py      # PDF, HTML, and CSV engineering reports
├── web/                         # Modern User Interface
│   ├── index.html               # Main SPA Interface
│   ├── app.css                  # Aerospace / Engineering design system
│   └── app.js                   # Client-side state, charts, and API bridge
├── sample_data/                 # Verified sample datasets
│   ├── runway_09_27_flexible.csv# Runway 09L-27R survey
│   ├── runway_18_36_rigid_lte.csv # Concrete joint LTE survey
│   └── faarfield_benchmark.json # FAA Workshop benchmark mix
├── tests/
│   └── test_engine.py           # Automated unit test suite
├── server.py                    # FastAPI REST server & static web host
├── run_app.py                   # 1-click launcher (starts server + opens browser)
├── run.bat                      # Windows launcher batch script
└── README.md                    # Project documentation
```

---

## Compliance & References
- **FAA Advisory Circular AC 150/5320-6G**: *Airport Pavement Design and Evaluation*
- **FAA BAKFAA 3.4.4**: *Backcalculation of Airport Pavement Moduli from FWD Data*
- **FAA FAARFIELD 2.0 / 2.1**: *Federal Aviation Administration Rigid and Flexible Iterative Elastic Layered Design*
- **ICAO Annex 14 / Doc 9157 Part 3**: *Pavements & ACR-PCR Reporting System*
- **AASHTO Guide for Design of Pavement Structures**: *Appendix A - Delineation of Homogeneous Units*
