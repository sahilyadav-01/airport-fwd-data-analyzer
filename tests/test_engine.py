"""
Unit and Benchmark Tests for Airport FWD Data Analyzer Engine
Validates:
1. Aircraft Database retrieval
2. Deflection basin indices (Area, SCI, BDI, BCI, subgrade modulus)
3. Cumulative difference section delineation
4. Forward LEAF deflection solver
5. Backcalculation and temperature correction
6. Rigid joint LTE and void detection
7. FAARFIELD flexible/rigid CDF calculation and thickness design
8. ICAO ACR-PCR calculation
"""

import unittest
from engine.aircraft_db import AIRCRAFT_DB, get_aircraft_by_name
from engine.basin_analyzer import analyze_deflection_basin
from engine.cum_diff import compute_cumulative_difference, delineate_sections
from engine.leaf_solver import PavementLayer, compute_surface_deflections
from engine.backcalc import backcalculate_station, correct_asphalt_modulus_temperature
from engine.lte_analyzer import analyze_joint_lte, detect_slab_void
from engine.faarfield_engine import (
    TrafficAircraft, calculate_flexible_cdf, calculate_rigid_cdf,
    design_flexible_thickness, compute_icao_acr_pcr
)

class TestAirportFWDEngine(unittest.TestCase):

    def test_aircraft_database(self):
        self.assertGreater(len(AIRCRAFT_DB), 50)
        b737 = get_aircraft_by_name("B737-800")
        self.assertIsNotNone(b737)
        self.assertGreater(b737["grossWeightKg"], 50000)

        a320 = get_aircraft_by_name("A320-200")
        self.assertIsNotNone(a320)

    def test_basin_analyzer(self):
        defls = [450.0, 380.0, 310.0, 240.0, 185.0, 120.0, 80.0, 55.0, 40.0]
        offsets = [0.0, 200.0, 300.0, 450.0, 600.0, 900.0, 1200.0, 1500.0, 1800.0]

        res = analyze_deflection_basin(defls, offsets, load_kn=180.0)
        self.assertAlmostEqual(res["d0_um"], 450.0)
        self.assertGreater(res["sci_um"], 0.0)
        self.assertGreater(res["e_subgrade_mpa"], 30.0)
        self.assertGreater(res["subgrade_cbr"], 3.0)
        self.assertGreater(res["k_value_pci"], 50.0)

    def test_cumulative_difference(self):
        stations = [0.0, 25.0, 50.0, 75.0, 100.0, 125.0, 150.0, 175.0, 200.0, 225.0]
        values = [250.0, 260.0, 255.0, 245.0, 250.0, 500.0, 520.0, 495.0, 510.0, 505.0]

        zx, boundaries = compute_cumulative_difference(stations, values)
        self.assertEqual(len(zx), len(stations))
        sections = delineate_sections(stations, values)
        self.assertGreaterEqual(len(sections), 1)

    def test_leaf_forward_and_backcalc(self):
        layers = [
            PavementLayer("HMA Surface", 100.0, 3000.0, 0.35, False, 1000.0, 10000.0),
            PavementLayer("P-209 Base", 200.0, 350.0, 0.35, False, 100.0, 1500.0),
            PavementLayer("Subgrade", 0.0, 75.0, 0.40, False, 20.0, 300.0)
        ]
        offsets = [0.0, 300.0, 600.0, 900.0, 1200.0, 1500.0]
        forward_defl = compute_surface_deflections(layers, offsets, load_kn=180.0)
        self.assertEqual(len(forward_defl), len(offsets))
        self.assertGreater(forward_defl[0], forward_defl[-1])

        seed_layers = [
            PavementLayer("HMA Surface", 100.0, 2500.0, 0.35, False, 1000.0, 10000.0),
            PavementLayer("P-209 Base", 200.0, 400.0, 0.35, False, 100.0, 1500.0),
            PavementLayer("Subgrade", 0.0, 60.0, 0.40, False, 20.0, 300.0)
        ]
        back_res = backcalculate_station(seed_layers, forward_defl, offsets, load_kn=180.0, max_iterations=40)
        self.assertLess(back_res["rmsePercent"], 5.0)

    def test_temperature_correction(self):
        res = correct_asphalt_modulus_temperature(modulus_mpa=3000.0, pavement_temp_c=32.0, reference_temp_c=20.0)
        self.assertGreater(res["correctedModulusMpa"], 3000.0)

    def test_joint_lte(self):
        lte_good = analyze_joint_lte(d_loaded_um=200.0, d_unloaded_um=180.0)
        self.assertEqual(lte_good["rating"], "Good")
        self.assertAlmostEqual(lte_good["ltePercent"], 90.0)

        lte_poor = analyze_joint_lte(d_loaded_um=300.0, d_unloaded_um=120.0)
        self.assertEqual(lte_poor["rating"], "Poor")
        self.assertAlmostEqual(lte_poor["ltePercent"], 40.0)

        # Multi-drop void detection: large positive intercept
        void_res = detect_slab_void(load_levels_kn=[50.0, 100.0, 150.0, 180.0],
                                    loaded_deflections_um=[140.0, 210.0, 280.0, 325.0])
        self.assertTrue(void_res["voidDetected"])

    def test_faarfield_cdf_and_thickness_design(self):
        traffic = [
            TrafficAircraft("B737-800", gross_weight_kg=79000.0, annual_departures=1200, gear_type="Dual"),
            TrafficAircraft("B777-300ER", gross_weight_kg=351000.0, annual_departures=800, gear_type="Triple Dual Tandem")
        ]

        # Flexible CDF
        flex_res = calculate_flexible_cdf(traffic, surface_thickness_mm=100.0, base_thickness_mm=250.0, subbase_thickness_mm=300.0, subgrade_cbr=6.0)
        self.assertIn("totalCdf", flex_res)
        self.assertIn("aircraftCdf", flex_res)
        self.assertGreater(len(flex_res["aircraftCdf"]), 0)

        # Thickness Design
        des_res = design_flexible_thickness(traffic, surface_thickness_mm=100.0, subbase_thickness_mm=200.0, subgrade_cbr=6.0)
        self.assertAlmostEqual(des_res["totalCdf"], 1.0, delta=0.5)
        self.assertGreater(des_res["designedThicknessMm"], 50.0)

        # ACR-PCR
        pcr_res = compute_icao_acr_pcr(traffic, pavement_type="Flexible", subgrade_cbr=6.0)
        self.assertIn("PCR", pcr_res["pcrCode"])
        self.assertEqual(pcr_res["pavementTypeCode"], "F")
        self.assertEqual(pcr_res["subgradeCategory"], "C")

if __name__ == "__main__":
    unittest.main()
