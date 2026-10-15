"""
FastAPI Server for Airport FWD Data Analyzer & FAA Pavement Evaluator
Exposes REST endpoints for FWD parsing, basin analysis, cumulative difference,
backcalculation, joint LTE, FAARFIELD design & life, and ICAO ACR-PCR.
Serves static frontend at root.
"""

import os
from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional

from engine.aircraft_db import AIRCRAFT_DB, get_aircraft_by_name, get_all_manufacturers
from engine.fwd_parser import parse_fwd_file, parse_csv_fwd, FWDRecord
from engine.basin_analyzer import analyze_deflection_basin
from engine.cum_diff import compute_cumulative_difference, delineate_sections
from engine.leaf_solver import PavementLayer, compute_surface_deflections
from engine.backcalc import backcalculate_station, batch_backcalculate, correct_asphalt_modulus_temperature
from engine.lte_analyzer import analyze_joint_lte, detect_slab_void
from engine.faarfield_engine import (
    TrafficAircraft, calculate_flexible_cdf, calculate_rigid_cdf,
    design_flexible_thickness, design_rigid_thickness, compute_icao_acr_pcr
)
from engine.report_generator import generate_csv_fwd_export, generate_csv_cdf_export, generate_html_report

app = FastAPI(
    title="Airport FWD Data Analyzer & FAA Pavement Evaluator",
    description="Professional FAA AC 150/5320-6G & BAKFAA 3.4 / FAARFIELD 2.1 Software Suite",
    version="3.5.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import sys
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WEB_DIR = os.path.join(BASE_DIR, "web")
SAMPLES_DIR = os.path.join(BASE_DIR, "sample_data")

# --- API ENDPOINTS ---

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "3.5.0", "engine": "FAARFIELD 2.1 & BAKFAA 3.4.4"}

@app.get("/api/aircraft")
def get_aircraft(manufacturer: Optional[str] = None):
    """Returns FAA aircraft library with optional manufacturer filter."""
    if manufacturer:
        mfg_clean = manufacturer.strip().lower()
        filtered = [ac for ac in AIRCRAFT_DB if ac.get("manufacturer", "").lower() == mfg_clean]
        return {"total": len(filtered), "aircraft": filtered}
    return {"total": len(AIRCRAFT_DB), "aircraft": AIRCRAFT_DB}

@app.get("/api/manufacturers")
def get_manufacturers():
    """Returns sorted unique aircraft manufacturers."""
    return {"manufacturers": get_all_manufacturers()}

@app.post("/api/fwd/parse")
def parse_fwd_data(payload: Dict[str, Any] = Body(...)):
    """Parses raw FWD file text (CSV, Dynatest, etc.) and returns structured drop data with basin indices."""
    content = payload.get("content", "")
    filename = payload.get("filename", "data.csv")
    target_load_kn = float(payload.get("targetLoadKn", 180.0))

    if not content.strip():
        raise HTTPException(status_code=400, detail="Empty content provided")

    records = parse_fwd_file(content, filename)
    if not records:
        raise HTTPException(status_code=422, detail="Failed to parse FWD deflection data from file")

    parsed_stations = []
    for rec in records:
        item = rec.to_dict()
        norm_defl = rec.normalized_deflections(target_load_kn)
        item["normalizedDeflectionsUm"] = norm_defl
        indices = analyze_deflection_basin(
            deflections_um=norm_defl,
            sensor_offsets_mm=rec.sensor_offsets_mm,
            load_kn=target_load_kn,
            plate_radius_mm=rec.plate_radius_mm
        )
        item["indices"] = indices
        parsed_stations.append(item)

    return {
        "count": len(parsed_stations),
        "targetLoadKn": target_load_kn,
        "stations": parsed_stations
    }

@app.post("/api/fwd/cumdiff")
def analyze_cumulative_difference(payload: Dict[str, Any] = Body(...)):
    """Calculates Cumulative Difference Z_x and delineates homogeneous runway sections."""
    stations = payload.get("stations", [])
    values = payload.get("values", [])
    param_name = payload.get("parameter", "D0_Normalized_um")

    if len(stations) < 3 or len(values) != len(stations):
        raise HTTPException(status_code=400, detail="Requires at least 3 stations with matching values")

    zx_values, boundaries = compute_cumulative_difference(stations, values)
    sections = delineate_sections(stations, values, param_name)

    return {
        "zxValues": zx_values,
        "boundaries": boundaries,
        "sections": sections
    }

@app.post("/api/backcalc/single")
def run_single_backcalc(payload: Dict[str, Any] = Body(...)):
    """Runs backcalculation for a single deflection basin."""
    layers_data = payload.get("layers", [])
    measured_um = payload.get("measuredDeflectionsUm", [])
    sensor_offsets_mm = payload.get("sensorOffsetsMm", [0, 200, 300, 450, 600, 900, 1200, 1500, 1800])
    load_kn = float(payload.get("loadKn", 180.0))
    plate_radius_mm = float(payload.get("plateRadiusMm", 150.0))
    tolerance_pct = float(payload.get("tolerancePercent", 1.5))
    surface_temp_c = payload.get("surfaceTempC", 20.0)
    air_temp_c = payload.get("airTempC", 20.0)

    layers = []
    for lyr in layers_data:
        layers.append(PavementLayer(
            name=lyr.get("name", "Layer"),
            thickness_mm=float(lyr.get("thicknessMm", 100.0)),
            modulus_mpa=float(lyr.get("modulusMpa", 1000.0)),
            poisson=float(lyr.get("poisson", 0.35)),
            is_fixed=bool(lyr.get("isFixed", False)),
            min_modulus_mpa=float(lyr.get("minModulusMpa", 20.0)),
            max_modulus_mpa=float(lyr.get("maxModulusMpa", 50000.0))
        ))

    result = backcalculate_station(
        layers=layers,
        measured_deflections_um=measured_um,
        sensor_offsets_mm=sensor_offsets_mm,
        load_kn=load_kn,
        plate_radius_mm=plate_radius_mm,
        tolerance_percent=tolerance_pct,
        surface_temp_c=surface_temp_c,
        air_temp_c=air_temp_c
    )
    return result

@app.post("/api/backcalc/batch")
def run_batch_backcalc(payload: Dict[str, Any] = Body(...)):
    """Runs batch backcalculation across an entire survey."""
    layers_data = payload.get("layers", [])
    stations_data = payload.get("stations", [])
    target_load_kn = float(payload.get("targetLoadKn", 180.0))
    plate_radius_mm = float(payload.get("plateRadiusMm", 150.0))
    tolerance_pct = float(payload.get("tolerancePercent", 2.0))

    layers = [
        PavementLayer(
            name=lyr.get("name", "Layer"),
            thickness_mm=float(lyr.get("thicknessMm", 100.0)),
            modulus_mpa=float(lyr.get("modulusMpa", 1000.0)),
            poisson=float(lyr.get("poisson", 0.35)),
            is_fixed=bool(lyr.get("isFixed", False)),
            min_modulus_mpa=float(lyr.get("minModulusMpa", 20.0)),
            max_modulus_mpa=float(lyr.get("maxModulusMpa", 50000.0))
        )
        for lyr in layers_data
    ]

    records = []
    for s in stations_data:
        records.append(FWDRecord(
            station=float(s.get("station", 0.0)),
            drop_id=int(s.get("dropId", 1)),
            load_kn=float(s.get("loadKn", target_load_kn)),
            deflections_um=s.get("deflectionsUm", []),
            sensor_offsets_mm=s.get("sensorOffsetsMm", [0, 200, 300, 450, 600, 900, 1200, 1500, 1800]),
            surface_temp_c=s.get("surfaceTempC", 20.0),
            air_temp_c=s.get("airTempC", 20.0),
            plate_radius_mm=plate_radius_mm
        ))

    results = batch_backcalculate(
        layers=layers,
        fwd_records=records,
        target_load_kn=target_load_kn,
        plate_radius_mm=plate_radius_mm,
        tolerance_percent=tolerance_pct
    )
    return {"count": len(results), "results": results}

@app.post("/api/lte/analyze")
def run_lte_analysis(payload: Dict[str, Any] = Body(...)):
    """Computes Joint Load Transfer Efficiency and checks for voids."""
    joints_data = payload.get("joints", [])
    results = []
    for j in joints_data:
        res = analyze_joint_lte(
            d_loaded_um=float(j.get("dLoadedUm", 200.0)),
            d_unloaded_um=float(j.get("dUnloadedUm", 180.0)),
            joint_id=str(j.get("jointId", "J1")),
            station=float(j.get("station", 0.0)),
            load_kn=float(j.get("loadKn", 180.0))
        )
        results.append(res)

    void_data = payload.get("multiLoadVoidTest")
    void_res = None
    if void_data and "loadKn" in void_data and "deflUm" in void_data:
        void_res = detect_slab_void(
            load_levels_kn=[float(x) for x in void_data["loadKn"]],
            loaded_deflections_um=[float(y) for y in void_data["deflUm"]]
        )

    return {"count": len(results), "joints": results, "voidAnalysis": void_res}

@app.post("/api/faarfield/cdf")
def run_faarfield_cdf(payload: Dict[str, Any] = Body(...)):
    """Computes Cumulative Damage Factor (CDF) and structural service life."""
    pavement_type = payload.get("pavementType", "New Flexible")
    traffic_raw = payload.get("traffic", [])
    design_life = int(payload.get("designLifeYears", 20))

    traffic = []
    for t in traffic_raw:
        traffic.append(TrafficAircraft(
            name=t.get("name", "Aircraft"),
            gross_weight_kg=float(t.get("grossWeightKg", 70000.0)),
            annual_departures=int(t.get("annualDepartures", 1200)),
            annual_growth_percent=float(t.get("annualGrowthPercent", 0.0)),
            percent_on_main_gear=float(t.get("percentOnMainGear", 0.95)),
            gear_type=t.get("gearType", "Dual"),
            tire_pressure_mpa=float(t.get("tirePressureMpa", 1.40))
        ))

    if "rigid" in pavement_type.lower():
        struct = payload.get("rigidStructure", {})
        res = calculate_rigid_cdf(
            traffic_list=traffic,
            slab_thickness_mm=float(struct.get("slabThicknessMm", 380.0)),
            base_thickness_mm=float(struct.get("baseThicknessMm", 150.0)),
            concrete_flexural_strength_mpa=float(struct.get("flexuralStrengthMpa", 4.8)),
            subgrade_k_pci=float(struct.get("subgradeKPci", 150.0)),
            design_life_years=design_life
        )
    else:
        struct = payload.get("flexibleStructure", {})
        res = calculate_flexible_cdf(
            traffic_list=traffic,
            surface_thickness_mm=float(struct.get("surfaceThicknessMm", 100.0)),
            base_thickness_mm=float(struct.get("baseThicknessMm", 150.0)),
            subbase_thickness_mm=float(struct.get("subbaseThicknessMm", 200.0)),
            subgrade_cbr=float(struct.get("subgradeCbr", 6.0)),
            design_life_years=design_life
        )
    return res

@app.post("/api/faarfield/design")
def run_faarfield_thickness_design(payload: Dict[str, Any] = Body(...)):
    """Automatically designs required pavement layer thickness for CDF = 1.0."""
    pavement_type = payload.get("pavementType", "New Flexible")
    traffic_raw = payload.get("traffic", [])
    design_life = int(payload.get("designLifeYears", 20))

    traffic = [
        TrafficAircraft(
            name=t.get("name", "Aircraft"),
            gross_weight_kg=float(t.get("grossWeightKg", 70000.0)),
            annual_departures=int(t.get("annualDepartures", 1200)),
            annual_growth_percent=float(t.get("annualGrowthPercent", 0.0)),
            percent_on_main_gear=float(t.get("percentOnMainGear", 0.95)),
            gear_type=t.get("gearType", "Dual"),
            tire_pressure_mpa=float(t.get("tirePressureMpa", 1.40))
        )
        for t in traffic_raw
    ]

    if "rigid" in pavement_type.lower():
        struct = payload.get("rigidStructure", {})
        res = design_rigid_thickness(
            traffic_list=traffic,
            base_thickness_mm=float(struct.get("baseThicknessMm", 150.0)),
            concrete_flexural_strength_mpa=float(struct.get("flexuralStrengthMpa", 4.8)),
            subgrade_k_pci=float(struct.get("subgradeKPci", 150.0)),
            design_life_years=design_life
        )
    else:
        struct = payload.get("flexibleStructure", {})
        res = design_flexible_thickness(
            traffic_list=traffic,
            surface_thickness_mm=float(struct.get("surfaceThicknessMm", 100.0)),
            subbase_thickness_mm=float(struct.get("subbaseThicknessMm", 200.0)),
            subgrade_cbr=float(struct.get("subgradeCbr", 6.0)),
            design_life_years=design_life
        )
    return res

@app.post("/api/faarfield/acr-pcr")
def run_acr_pcr_analysis(payload: Dict[str, Any] = Body(...)):
    """Calculates ICAO ACR and PCR values along with fleet operational eligibility."""
    pavement_type = payload.get("pavementType", "Flexible")
    subgrade_cbr = float(payload.get("subgradeCbr", 6.0))
    subgrade_k_pci = float(payload.get("subgradeKPci", 150.0))
    tire_pressure_cat = payload.get("tirePressureCategory", "W")
    traffic_raw = payload.get("traffic", [])

    traffic = [
        TrafficAircraft(
            name=t.get("name", "Aircraft"),
            gross_weight_kg=float(t.get("grossWeightKg", 70000.0)),
            annual_departures=int(t.get("annualDepartures", 1200)),
            annual_growth_percent=float(t.get("annualGrowthPercent", 0.0)),
            percent_on_main_gear=float(t.get("percentOnMainGear", 0.95)),
            gear_type=t.get("gearType", "Dual"),
            tire_pressure_mpa=float(t.get("tirePressureMpa", 1.40))
        )
        for t in traffic_raw
    ]

    res = compute_icao_acr_pcr(
        traffic_list=traffic,
        pavement_type=pavement_type,
        subgrade_cbr=subgrade_cbr,
        subgrade_k_pci=subgrade_k_pci,
        tire_pressure_category=tire_pressure_cat
    )
    return res

@app.post("/api/report/export-html")
def export_html_report(payload: Dict[str, Any] = Body(...)):
    """Generates print-ready HTML engineering report."""
    html_content = generate_html_report(
        project_meta=payload.get("project", {}),
        fwd_summary=payload.get("fwdSummary", {}),
        backcalc_summary=payload.get("backcalcSummary", {}),
        cumdiff_summary=payload.get("cumdiffSummary", []),
        faarfield_summary=payload.get("faarfieldSummary", {}),
        pcr_summary=payload.get("pcrSummary", {})
    )
    return HTMLResponse(content=html_content)

@app.post("/api/report/export-fwd-csv")
def export_fwd_csv(payload: Dict[str, Any] = Body(...)):
    """Exports FWD station data to CSV."""
    csv_str = generate_csv_fwd_export(payload.get("stations", []))
    return PlainTextResponse(content=csv_str, media_type="text/csv")

@app.get("/api/samples/{sample_name}")
def get_sample_data(sample_name: str):
    """Loads built-in sample files."""
    if sample_name == "flexible_fwd":
        path = os.path.join(SAMPLES_DIR, "runway_09_27_flexible.csv")
    elif sample_name == "rigid_lte":
        path = os.path.join(SAMPLES_DIR, "runway_18_36_rigid_lte.csv")
    elif sample_name == "benchmark":
        path = os.path.join(SAMPLES_DIR, "faarfield_benchmark.json")
    else:
        raise HTTPException(status_code=404, detail="Sample not found")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Sample file missing")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if path.endswith(".json"):
        import json
        return JSONResponse(content=json.loads(content))
    return PlainTextResponse(content=content)

# Serve web frontend
if os.path.exists(WEB_DIR):
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
