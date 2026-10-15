"""
Deflection Basin Analyzer Module
Computes standard pavement structural indices from FWD deflection basins:
- Central Deflection D0
- Normalized Deflections (to 180 kN standard airport HWD load or 40 kN FWD load)
- Basin Area Factor (AF) and Basin Area (mm or inches)
- Surface Curvature Index (SCI)
- Base Damage Index (BDI)
- Base Curvature Index (BCI)
- Subgrade Resilient Modulus (E_sg) from outer sensor (AASHTO / FAA AC 150/5320-6G)
- Subgrade CBR (CBR = E / 1500)
- Subgrade Modulus of Reaction k (k = 28.6926 * CBR^0.7788)
- Depth to Apparent Rigid Layer / Bedrock (Roesset's method)
"""

import math
from typing import Dict, List, Any, Optional

def analyze_deflection_basin(deflections_um: List[float],
                             sensor_offsets_mm: List[float],
                             load_kn: float = 180.0,
                             plate_radius_mm: float = 150.0,
                             subgrade_poisson: float = 0.35) -> Dict[str, Any]:
    """
    Analyzes a single FWD deflection basin and returns all structural indices.
    """
    if not deflections_um or len(deflections_um) < 2:
        return {}

    d0 = deflections_um[0]
    num_sensors = len(deflections_um)

    # 1. Deflection Basin Area Factor (AASHTO / FAA)
    # Area = sum(0.5 * (d_i + d_{i+1}) * (r_{i+1} - r_i)) / d0
    area_mm = 0.0
    if d0 > 0:
        for i in range(num_sensors - 1):
            dr = sensor_offsets_mm[i + 1] - sensor_offsets_mm[i]
            avg_d = 0.5 * (deflections_um[i] + deflections_um[i + 1])
            area_mm += avg_d * dr
        area_factor = area_mm / (d0 * sensor_offsets_mm[-1]) if sensor_offsets_mm[-1] > 0 else 0.0
    else:
        area_factor = 0.0

    # 2. Structural Indices: SCI, BDI, BCI
    # Map sensors closest to 300mm, 600mm, 900mm
    def get_defl_at_offset(target_offset: float) -> float:
        closest_idx = min(range(len(sensor_offsets_mm)), key=lambda i: abs(sensor_offsets_mm[i] - target_offset))
        return deflections_um[closest_idx]

    d_300 = get_defl_at_offset(300.0)
    d_600 = get_defl_at_offset(600.0)
    d_900 = get_defl_at_offset(900.0)
    d_1200 = get_defl_at_offset(1200.0)
    d_1500 = get_defl_at_offset(1500.0) if sensor_offsets_mm[-1] >= 1400.0 else deflections_um[-1]

    sci = round(d0 - d_300, 2)
    bdi = round(d_300 - d_600, 2)
    bci = round(d_600 - d_900, 2)

    # 3. Subgrade Resilient Modulus from Outer Sensor (AASHTO / FAA AC 150/5320-6G Eq. A-2)
    # E_sg = (1 - nu^2) * P / (pi * r * d_r)
    # P in N, r in mm, d_r in mm -> E in MPa
    p_newtons = load_kn * 1000.0
    outer_sensor_idx = len(deflections_um) - 1
    # Pick sensor with offset >= 900 mm (typically 1200 mm or 1500 mm for subgrade isolation)
    for idx in range(len(sensor_offsets_mm) - 1, -1, -1):
        if sensor_offsets_mm[idx] >= 900.0:
            outer_sensor_idx = idx
            break

    r_outer_mm = sensor_offsets_mm[outer_sensor_idx]
    d_outer_um = deflections_um[outer_sensor_idx]
    d_outer_mm = d_outer_um / 1000.0

    e_subgrade_mpa = 0.0
    if r_outer_mm > 0 and d_outer_mm > 0:
        # Boussinesq outer sensor equation:
        e_subgrade_mpa = ((1.0 - subgrade_poisson**2) * p_newtons) / (math.pi * r_outer_mm * d_outer_mm)

    e_subgrade_psi = e_subgrade_mpa * 145.0377

    # 4. FAA AC 150/5320-6G CBR & k-value
    # CBR = E_sg (psi) / 1500
    subgrade_cbr = e_subgrade_psi / 1500.0 if e_subgrade_psi > 0 else 0.0

    # k = 28.6926 * CBR^0.7788 (psi/in)
    k_value_pci = (28.6926 * (subgrade_cbr ** 0.7788)) if subgrade_cbr > 0 else 0.0
    k_value_mn_m3 = k_value_pci * 0.27144

    # 5. Apparent Depth to Bedrock / Rigid Layer (Roesset / AASHTO 1/r extrapolation)
    # Uses 1/r vs deflection linearity
    depth_bedrock_m = None
    if len(deflections_um) >= 4:
        # Take outer 3 sensors
        x_inv_r = [1.0 / (sensor_offsets_mm[i] / 1000.0) for i in range(len(sensor_offsets_mm) - 3, len(sensor_offsets_mm))]
        y_defl = [deflections_um[i] for i in range(len(deflections_um) - 3, len(deflections_um))]
        # Linear fit y = m*x + c. Where y=0 -> x_intercept = -c/m -> depth = 1 / x_intercept
        n = len(x_inv_r)
        sum_x = sum(x_inv_r)
        sum_y = sum(y_defl)
        sum_xx = sum(x * x for x in x_inv_r)
        sum_xy = sum(x * y for x, y in zip(x_inv_r, y_defl))
        denom = (n * sum_xx - sum_x * sum_x)
        if abs(denom) > 1e-6:
            slope = (n * sum_xy - sum_x * sum_y) / denom
            intercept = (sum_y - slope * sum_x) / n
            if abs(slope) > 1e-4 and intercept != 0:
                x_0 = -intercept / slope
                if x_0 > 0:
                    d_est = 1.0 / x_0
                    if 0.5 <= d_est <= 25.0:
                        depth_bedrock_m = round(d_est, 2)

    return {
        "d0_um": round(d0, 1),
        "d0_mils": round(d0 / 25.4, 2),
        "area_factor": round(area_factor, 3),
        "area_mm": round(area_mm, 1),
        "sci_um": sci,
        "bdi_um": bdi,
        "bci_um": bci,
        "outer_sensor_r_mm": r_outer_mm,
        "outer_sensor_d_um": round(d_outer_um, 1),
        "e_subgrade_mpa": round(e_subgrade_mpa, 1),
        "e_subgrade_psi": round(e_subgrade_psi, 0),
        "subgrade_cbr": round(subgrade_cbr, 1),
        "k_value_pci": round(k_value_pci, 1),
        "k_value_mn_m3": round(k_value_mn_m3, 1),
        "depth_bedrock_m": depth_bedrock_m
    }
