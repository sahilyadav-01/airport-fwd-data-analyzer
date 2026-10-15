"""
Airport FWD Data Analyzer & FAA Pavement Design Engine
"""

from engine.aircraft_db import AIRCRAFT_DB, get_aircraft_by_name, get_all_manufacturers
from engine.fwd_parser import parse_fwd_file, parse_csv_fwd, parse_dynatest_fwd, FWDRecord
from engine.basin_analyzer import analyze_deflection_basin
from engine.cum_diff import compute_cumulative_difference, delineate_sections
from engine.leaf_solver import PavementLayer, compute_surface_deflections
from engine.backcalc import backcalculate_station, batch_backcalculate, correct_asphalt_modulus_temperature
from engine.lte_analyzer import analyze_joint_lte, detect_slab_void
from engine.faarfield_engine import (
    TrafficAircraft, calculate_flexible_cdf, calculate_rigid_cdf,
    design_flexible_thickness, design_rigid_thickness, compute_icao_acr_pcr
)
