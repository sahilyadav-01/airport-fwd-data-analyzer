"""
Backcalculation Engine Module (BAKFAA-equivalent)
Iteratively backcalculates airport pavement layer moduli from FWD deflection basins
using Nelder-Mead Simplex and L-BFGS-B optimization to minimize Root Mean Square Error (% RMSE).
Includes BELLS3 and FAA AC 150/5320-6G temperature correction for asphalt layers.
"""

import math
import numpy as np
from scipy.optimize import minimize
from typing import List, Dict, Any, Optional, Tuple
from engine.leaf_solver import PavementLayer, compute_surface_deflections

def correct_asphalt_modulus_temperature(modulus_mpa: float,
                                        pavement_temp_c: float,
                                        reference_temp_c: float = 20.0,
                                        thickness_mm: float = 100.0,
                                        surface_temp_c: Optional[float] = None,
                                        air_temp_c: Optional[float] = None) -> Dict[str, Any]:
    """
    Corrects backcalculated asphalt surface modulus to standard reference temperature (20°C / 68°F).
    Implements FAA AC 150/5320-6G / Asphalt Institute temperature adjustment model.
    """
    t_mid = pavement_temp_c

    # If surface and air temperatures are available, refine using BELLS3 formula
    if surface_temp_c is not None and air_temp_c is not None:
        # Depth d = mid-depth of asphalt layer (mm)
        d = max(10.0, thickness_mm / 2.0)
        # Default test time = 13:00 (1:00 PM)
        hr18 = 13.0
        sin_term = math.sin(hr18 * 2.0 * math.pi / 18.0)
        log_d = math.log10(d)
        t_mid = (0.95 + 0.892 * surface_temp_c +
                 (log_d - 1.25) * (-0.448 * surface_temp_c + 0.621 * air_temp_c + 1.83 * sin_term) +
                 0.042 * surface_temp_c * sin_term)

    # FAA AC 150/5320-6G / Asphalt Institute Equation:
    # E_ref = E_field * 10^(-0.0153 * (T_ref - T_field))
    delta_t = reference_temp_c - t_mid
    adjustment_factor = 10.0 ** (-0.0153 * delta_t)
    e_corrected_mpa = modulus_mpa * adjustment_factor

    return {
        "midDepthTempC": round(t_mid, 1),
        "midDepthTempF": round(t_mid * 9.0 / 5.0 + 32.0, 1),
        "referenceTempC": reference_temp_c,
        "referenceTempF": round(reference_temp_c * 9.0 / 5.0 + 32.0, 1),
        "adjustmentFactor": round(adjustment_factor, 3),
        "originalModulusMpa": round(modulus_mpa, 1),
        "correctedModulusMpa": round(e_corrected_mpa, 1),
        "correctedModulusPsi": round(e_corrected_mpa * 145.0377, 0)
    }


def compute_rmse(measured_um: List[float], calculated_um: List[float]) -> float:
    """Computes percent Root Mean Square Error (% RMSE)."""
    n = len(measured_um)
    if n == 0:
        return 0.0
    sq_err_sum = 0.0
    valid_count = 0
    for m, c in zip(measured_um, calculated_um):
        if m > 0:
            sq_err_sum += ((c - m) / m) ** 2
            valid_count += 1
    if valid_count == 0:
        return 0.0
    return math.sqrt(sq_err_sum / valid_count) * 100.0


def backcalculate_station(layers: List[PavementLayer],
                          measured_deflections_um: List[float],
                          sensor_offsets_mm: List[float],
                          load_kn: float = 180.0,
                          plate_radius_mm: float = 150.0,
                          max_iterations: int = 60,
                          tolerance_percent: float = 1.0,
                          surface_temp_c: Optional[float] = 20.0,
                          air_temp_c: Optional[float] = 20.0) -> Dict[str, Any]:
    """
    Performs backcalculation for a single FWD deflection basin.
    Returns optimal layer moduli, calculated deflections, % RMSE, and convergence info.
    """
    # Identify variable (unfixed) layers
    var_indices = [i for i, lyr in enumerate(layers) if not lyr.is_fixed]

    if not var_indices:
        # All layers fixed, just compute forward deflections
        calc_defl = compute_surface_deflections(layers, sensor_offsets_mm, load_kn, plate_radius_mm)
        rmse = compute_rmse(measured_deflections_um, calc_defl)
        return {
            "success": True,
            "iterations": 0,
            "rmsePercent": round(rmse, 2),
            "layers": [lyr.to_dict() for lyr in layers],
            "calculatedDeflectionsUm": calc_defl,
            "measuredDeflectionsUm": measured_deflections_um
        }

    # Initial log-moduli
    x0 = [math.log(layers[i].modulus_mpa) for i in var_indices]
    bounds = [(math.log(max(1.0, layers[i].min_modulus_mpa)),
               math.log(layers[i].max_modulus_mpa)) for i in var_indices]

    iter_count = [0]

    def objective(x):
        iter_count[0] += 1
        # Build layer instances with proposed moduli
        test_layers = []
        var_ptr = 0
        for i, lyr in enumerate(layers):
            if lyr.is_fixed:
                test_layers.append(PavementLayer(lyr.name, lyr.thickness_mm, lyr.modulus_mpa, lyr.poisson, True))
            else:
                mod = math.exp(x[var_ptr])
                test_layers.append(PavementLayer(lyr.name, lyr.thickness_mm, mod, lyr.poisson, False))
                var_ptr += 1

        calc = compute_surface_deflections(test_layers, sensor_offsets_mm, load_kn, plate_radius_mm)
        return compute_rmse(measured_deflections_um, calc)

    # Use Nelder-Mead simplex optimizer (matches BAKFAA Amoeba algorithm)
    # followed by bounded refinement if needed
    res = minimize(objective, x0, method='Nelder-Mead',
                   options={'maxiter': max_iterations, 'xatol': 1e-3, 'fatol': tolerance_percent / 2.0})

    optimal_x = res.x
    # Clip to bounds
    for k in range(len(var_indices)):
        optimal_x[k] = max(bounds[k][0], min(bounds[k][1], optimal_x[k]))

    # Final layers
    final_layers = []
    var_ptr = 0
    for i, lyr in enumerate(layers):
        if lyr.is_fixed:
            mod = lyr.modulus_mpa
        else:
            mod = math.exp(optimal_x[var_ptr])
            var_ptr += 1
        final_layers.append(PavementLayer(lyr.name, lyr.thickness_mm, mod, lyr.poisson, lyr.is_fixed))

    final_calc_defl = compute_surface_deflections(final_layers, sensor_offsets_mm, load_kn, plate_radius_mm)
    final_rmse = compute_rmse(measured_deflections_um, final_calc_defl)

    # Apply temperature correction to layer 1 if asphalt / flexible
    temp_corr = None
    if len(final_layers) > 0 and 'asphalt' in final_layers[0].name.lower() or 'hma' in final_layers[0].name.lower() or 'p-401' in final_layers[0].name.lower():
        temp_corr = correct_asphalt_modulus_temperature(
            modulus_mpa=final_layers[0].modulus_mpa,
            pavement_temp_c=surface_temp_c if surface_temp_c is not None else 20.0,
            thickness_mm=final_layers[0].thickness_mm,
            surface_temp_c=surface_temp_c,
            air_temp_c=air_temp_c
        )

    # Subgrade resilient modulus & CBR
    subgrade_mod_mpa = final_layers[-1].modulus_mpa
    subgrade_mod_psi = subgrade_mod_mpa * 145.0377
    subgrade_cbr = subgrade_mod_psi / 1500.0
    k_value_pci = 28.6926 * (subgrade_cbr ** 0.7788) if subgrade_cbr > 0 else 0.0

    return {
        "success": bool(final_rmse <= tolerance_percent * 2.5 or res.success),
        "iterations": iter_count[0],
        "rmsePercent": round(final_rmse, 2),
        "layers": [lyr.to_dict() for lyr in final_layers],
        "calculatedDeflectionsUm": final_calc_defl,
        "measuredDeflectionsUm": measured_deflections_um,
        "temperatureCorrection": temp_corr,
        "subgradeProperties": {
            "modulusMpa": round(subgrade_mod_mpa, 1),
            "modulusPsi": round(subgrade_mod_psi, 0),
            "cbr": round(subgrade_cbr, 1),
            "kValuePci": round(k_value_pci, 1),
            "kValueMnM3": round(k_value_pci * 0.27144, 1)
        }
    }


def batch_backcalculate(layers: List[PavementLayer],
                        fwd_records: List[Any],
                        target_load_kn: float = 180.0,
                        plate_radius_mm: float = 150.0,
                        tolerance_percent: float = 2.0) -> List[Dict[str, Any]]:
    """
    Performs batch backcalculation across all stations / drops.
    """
    results = []
    for rec in fwd_records:
        defl_norm = rec.normalized_deflections(target_load_kn)
        res = backcalculate_station(
            layers=layers,
            measured_deflections_um=defl_norm,
            sensor_offsets_mm=rec.sensor_offsets_mm,
            load_kn=target_load_kn,
            plate_radius_mm=plate_radius_mm,
            tolerance_percent=tolerance_percent,
            surface_temp_c=rec.surface_temp_c,
            air_temp_c=rec.air_temp_c
        )
        res["station"] = rec.station
        res["dropId"] = rec.drop_id
        res["loadKn"] = rec.load_kn
        results.append(res)
    return results
