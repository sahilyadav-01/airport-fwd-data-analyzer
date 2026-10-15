"""
Cumulative Difference Method Module (AASHTO / FAA AC 150/5320-6G Appendix A)
Performs statistical delineation of homogeneous runway / taxiway pavement sections
based on FWD deflection basin indices, subgrade modulus, or load transfer efficiency.
"""

import math
from typing import List, Dict, Any, Tuple

def compute_cumulative_difference(stations: List[float], values: List[float]) -> Tuple[List[float], List[int]]:
    """
    Computes Cumulative Difference variable Z_x along the runway.
    Returns (zx_values, boundary_indices).
    """
    n = len(stations)
    if n < 3 or len(values) != n:
        return [0.0] * n, []

    # Calculate trapezoidal areas between adjacent stations
    dx = []
    avg_r = []
    delta_areas = []
    for i in range(n - 1):
        dist = stations[i + 1] - stations[i]
        # Safeguard against zero or negative dist
        if dist <= 0:
            dist = 1.0
        dx.append(dist)
        mean_val = 0.5 * (values[i] + values[i + 1])
        avg_r.append(mean_val)
        delta_areas.append(dist * mean_val)

    total_area = sum(delta_areas)
    total_length = stations[-1] - stations[0]
    if total_length <= 0:
        total_length = 1.0

    # Compute Z_x for each station
    zx = [0.0]
    accumulated_area = 0.0
    for i in range(n - 1):
        accumulated_area += delta_areas[i]
        fractional_length = (stations[i + 1] - stations[0]) / total_length
        val_zx = accumulated_area - fractional_length * total_area
        zx.append(round(val_zx, 3))

    # Detect inflection points (local peaks and valleys)
    # Filter with minimum section distance (at least 2 consecutive drops)
    boundaries = [0]
    # Smooth slight noise with simple 3-point slope change detection
    for i in range(2, n - 2):
        prev_slope = zx[i] - zx[i - 1]
        next_slope = zx[i + 1] - zx[i]
        # Sign change: peak or valley
        if (prev_slope * next_slope < 0):
            # Ensure not too close to last boundary (at least 3 stations apart)
            if (i - boundaries[-1]) >= 3:
                # Check magnitude threshold relative to max range
                z_range = max(zx) - min(zx)
                if z_range > 0 and abs(zx[i] - zx[boundaries[-1]]) > 0.05 * z_range:
                    boundaries.append(i)

    if boundaries[-1] != n - 1:
        boundaries.append(n - 1)

    return zx, boundaries


def delineate_sections(stations: List[float],
                       values: List[float],
                       parameter_name: str = "D0_Normalized_um") -> List[Dict[str, Any]]:
    """
    Delineates the runway into homogeneous sections and computes statistical measures.
    """
    n = len(stations)
    if n < 2:
        return []

    zx_values, boundaries = compute_cumulative_difference(stations, values)

    sections = []
    for s_idx in range(len(boundaries) - 1):
        start_i = boundaries[s_idx]
        end_i = boundaries[s_idx + 1]

        sec_stations = stations[start_i:end_i + 1]
        sec_values = values[start_i:end_i + 1]

        count = len(sec_values)
        if count == 0:
            continue

        mean_val = sum(sec_values) / count
        variance = sum((v - mean_val) ** 2 for v in sec_values) / (count - 1) if count > 1 else 0.0
        stdev = math.sqrt(variance)
        cv = (stdev / mean_val * 100.0) if mean_val > 0 else 0.0

        # FAA AC 150/5320-6G 85th percentile representative design deflection:
        # D_85 = mean + 1.036 * stdev
        design_val_85 = mean_val + 1.036 * stdev
        # For strength / CBR / modulus, 15th percentile is design lower bound:
        design_val_15 = max(0.0, mean_val - 1.036 * stdev)

        sections.append({
            "sectionId": f"Section {s_idx + 1}",
            "startIndex": start_i,
            "endIndex": end_i,
            "startStation": round(sec_stations[0], 2),
            "endStation": round(sec_stations[-1], 2),
            "lengthM": round(sec_stations[-1] - sec_stations[0], 2),
            "sampleCount": count,
            "mean": round(mean_val, 2),
            "stdev": round(stdev, 2),
            "covPercent": round(cv, 1),
            "designValue85th": round(design_val_85, 2),
            "designValue15th": round(design_val_15, 2),
            "parameter": parameter_name
        })

    return sections
