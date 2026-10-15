"""
Layered Elastic Analysis Solver (LEAF-equivalent)
Computes theoretical surface deflections, strains, and stresses for multi-layer airport pavement systems
under circular FWD/HWD loading using Method of Equivalent Thickness (MET) and Burmister elastic theory.
"""

import math
from typing import List, Dict, Any, Optional

class PavementLayer:
    def __init__(self,
                 name: str,
                 thickness_mm: float,
                 modulus_mpa: float,
                 poisson: float = 0.35,
                 is_fixed: bool = False,
                 min_modulus_mpa: float = 20.0,
                 max_modulus_mpa: float = 50000.0):
        self.name = name
        self.thickness_mm = max(0.0, float(thickness_mm))
        self.modulus_mpa = max(1.0, float(modulus_mpa))
        self.poisson = float(poisson)
        self.is_fixed = bool(is_fixed)
        self.min_modulus_mpa = float(min_modulus_mpa)
        self.max_modulus_mpa = float(max_modulus_mpa)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "thicknessMm": round(self.thickness_mm, 1),
            "thicknessIn": round(self.thickness_mm / 25.4, 2),
            "modulusMpa": round(self.modulus_mpa, 1),
            "modulusPsi": round(self.modulus_mpa * 145.0377, 0),
            "poisson": self.poisson,
            "isFixed": self.is_fixed,
            "minModulusMpa": self.min_modulus_mpa,
            "maxModulusMpa": self.max_modulus_mpa
        }


def compute_surface_deflections(layers: List[PavementLayer],
                                sensor_offsets_mm: List[float],
                                load_kn: float = 180.0,
                                plate_radius_mm: float = 150.0) -> List[float]:
    """
    Computes theoretical surface deflections (in microns) at the given sensor offsets.
    Implements Odemark's Method of Equivalent Thickness (MET) combined with Boussinesq integration.
    """
    n_layers = len(layers)
    if n_layers == 0:
        return [0.0] * len(sensor_offsets_mm)

    subgrade = layers[-1]
    e_sub = max(1.0, subgrade.modulus_mpa)
    nu_sub = subgrade.poisson

    # Contact pressure q (MPa)
    # P in N, area in mm^2 -> MPa = N/mm^2
    p_n = load_kn * 1000.0
    area_mm2 = math.pi * (plate_radius_mm ** 2)
    q_mpa = p_n / area_mm2

    # Calculate equivalent depths (z_e) at layer interfaces
    z_e = [0.0]
    for i in range(n_layers - 1):
        lyr = layers[i]
        # Correction factor: 0.85 for first layer, 1.0 for others
        f_factor = 0.85 if i == 0 else 1.0
        e_ratio = (lyr.modulus_mpa * (1.0 - nu_sub**2)) / (e_sub * (1.0 - lyr.poisson**2))
        h_eq = f_factor * lyr.thickness_mm * (max(0.01, e_ratio) ** (1.0 / 3.0))
        z_e.append(z_e[-1] + h_eq)

    deflections_um = []

    for r_mm in sensor_offsets_mm:
        r = float(r_mm)
        w_total_mm = 0.0

        if r == 0.0:
            # Deflection directly under circular load
            for i in range(n_layers - 1):
                lyr = layers[i]
                z_top = z_e[i]
                z_bot = z_e[i + 1]
                t_top = math.sqrt(1.0 + (z_top / plate_radius_mm)**2) - (z_top / plate_radius_mm)
                t_bot = math.sqrt(1.0 + (z_bot / plate_radius_mm)**2) - (z_bot / plate_radius_mm)
                delta_w = (2.0 * (1.0 - lyr.poisson**2) * q_mpa * plate_radius_mm / lyr.modulus_mpa) * (t_top - t_bot)
                w_total_mm += max(0.0, delta_w)

            # Subgrade deflection
            z_sub = z_e[-1]
            t_sub = math.sqrt(1.0 + (z_sub / plate_radius_mm)**2) - (z_sub / plate_radius_mm)
            w_sub = (2.0 * (1.0 - nu_sub**2) * q_mpa * plate_radius_mm / e_sub) * t_sub
            w_total_mm += max(0.0, w_sub)
        else:
            # At radial offset r > 0
            for i in range(n_layers - 1):
                lyr = layers[i]
                z_top = z_e[i]
                z_bot = z_e[i + 1]

                # Point load / distributed approximation at depth
                r2 = r**2
                term_top = (2.0 * (1.0 - lyr.poisson) / math.sqrt(r2 + z_top**2)) + (z_top**2 / (r2 + z_top**2)**1.5)
                term_bot = (2.0 * (1.0 - lyr.poisson) / math.sqrt(r2 + z_bot**2)) + (z_bot**2 / (r2 + z_bot**2)**1.5)

                delta_w = ((1.0 + lyr.poisson) * p_n / (2.0 * math.pi * lyr.modulus_mpa)) * (term_top - term_bot)
                w_total_mm += max(0.0, delta_w)

            # Subgrade component
            z_sub = z_e[-1]
            r2 = r**2
            term_sub = (2.0 * (1.0 - nu_sub) / math.sqrt(r2 + z_sub**2)) + (z_sub**2 / (r2 + z_sub**2)**1.5)
            w_sub = ((1.0 + nu_sub) * p_n / (2.0 * math.pi * e_sub)) * term_sub
            w_total_mm += max(0.0, w_sub)

        # Convert mm to microns (1 mm = 1000 um)
        defl_um = max(0.0, w_total_mm * 1000.0)
        deflections_um.append(round(defl_um, 2))

    return deflections_um
