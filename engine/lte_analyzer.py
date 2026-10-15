"""
Joint Load Transfer Efficiency (LTE) and Void Detection Module
Analyzes rigid airport pavement joint testing data (FAA AC 150/5320-6G & BAKFAA 3.4).
Computes:
- Deflection Load Transfer Efficiency (LTE%)
- Corrected LTE* (accounting for slab bending)
- Joint Condition Rating (Good >= 85%, Fair 70-85%, Poor < 70%)
- Void Detection through load-deflection intercept analysis
"""

from typing import List, Dict, Any, Optional

def analyze_joint_lte(d_loaded_um: float,
                      d_unloaded_um: float,
                      joint_id: str = "J1",
                      station: float = 0.0,
                      load_kn: float = 180.0,
                      slab_thickness_mm: Optional[float] = None) -> Dict[str, Any]:
    """
    Computes Joint Load Transfer Efficiency from loaded and unloaded slab deflections.
    """
    if d_loaded_um <= 0:
        lte_percent = 0.0
        lte_corrected = 0.0
    else:
        lte_percent = (d_unloaded_um / d_loaded_um) * 100.0
        # Corrected LTE (accounting for slab geometry / bending)
        sum_defl = d_loaded_um + d_unloaded_um
        lte_corrected = (2.0 * d_unloaded_um / sum_defl * 100.0) if sum_defl > 0 else 0.0

    lte_percent = min(100.0, max(0.0, lte_percent))
    lte_corrected = min(100.0, max(0.0, lte_corrected))

    # FAA AC 150/5320-6G Condition Rating
    if lte_percent >= 85.0:
        rating = "Good"
        action = "Adequate load transfer. No remedial action needed."
        color = "#10B981"  # Emerald
    elif lte_percent >= 70.0:
        rating = "Fair"
        action = "Moderate load transfer. Monitor for faulting or spalling."
        color = "#F59E0B"  # Amber
    else:
        rating = "Poor"
        action = "Substandard load transfer. High risk of slab cracking. Consider dowel retrofit."
        color = "#EF4444"  # Red

    return {
        "jointId": joint_id,
        "station": station,
        "loadKn": load_kn,
        "dLoadedUm": round(d_loaded_um, 1),
        "dUnloadedUm": round(d_unloaded_um, 1),
        "differentialDeflectionUm": round(abs(d_loaded_um - d_unloaded_um), 1),
        "ltePercent": round(lte_percent, 1),
        "lteCorrectedPercent": round(lte_corrected, 1),
        "rating": rating,
        "recommendedAction": action,
        "ratingColor": color
    }


def detect_slab_void(load_levels_kn: List[float],
                     loaded_deflections_um: List[float],
                     void_threshold_um: float = 50.0) -> Dict[str, Any]:
    """
    Detects voids underneath rigid pavement slab edges using multi-load drop linearity.
    A positive deflection intercept > 50 um (2 mils) indicates loss of subbase support.
    """
    n = len(load_levels_kn)
    if n < 2 or len(loaded_deflections_um) != n:
        return {"voidDetected": False, "interceptUm": 0.0, "rSquared": 0.0}

    sum_x = sum(load_levels_kn)
    sum_y = sum(loaded_deflections_um)
    sum_xx = sum(x * x for x in load_levels_kn)
    sum_yy = sum(y * y for y in loaded_deflections_um)
    sum_xy = sum(x * y for x, y in zip(load_levels_kn, loaded_deflections_um))

    denom = (n * sum_xx - sum_x * sum_x)
    if abs(denom) < 1e-6:
        return {"voidDetected": False, "interceptUm": 0.0, "rSquared": 0.0}

    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n

    # R^2 correlation
    ss_tot = sum((y - (sum_y / n)) ** 2 for y in loaded_deflections_um)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(load_levels_kn, loaded_deflections_um))
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 1.0

    void_detected = bool(intercept >= void_threshold_um)

    return {
        "voidDetected": void_detected,
        "interceptUm": round(intercept, 1),
        "slopeUmPerKn": round(slope, 3),
        "rSquared": round(r2, 4),
        "assessment": "Severe voiding under slab edge" if intercept > 100.0 else
                     "Probable void / loss of support" if void_detected else "Full contact with subbase"
    }
