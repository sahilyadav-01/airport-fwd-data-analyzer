"""
FAA Aircraft Library Module
Loads and provides access to standard FAA aircraft definitions extracted from FAARFIELD 2.0 / 2.1.
"""

import json
import os
import sys
from typing import Dict, List, Optional

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    _CURRENT_DIR = os.path.join(sys._MEIPASS, "engine")
else:
    _CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

_DB_PATH = os.path.join(_CURRENT_DIR, "aircraft_db.json")

# Fallback default list if file not found
_DEFAULT_AIRCRAFT = [
    {
        "name": "B737-800",
        "manufacturer": "Boeing",
        "grossWeightLbs": 174200.0,
        "grossWeightKg": 79015.0,
        "mgPercent": 0.95,
        "pcnMgPercent": 0.475,
        "numWheels": 2,
        "gearType": "Dual",
        "tirePressurePsi": 205.0,
        "tirePressureMpa": 1.413
    },
    {
        "name": "A320-200 std",
        "manufacturer": "Airbus",
        "grossWeightLbs": 162925.0,
        "grossWeightKg": 73900.0,
        "mgPercent": 0.95,
        "pcnMgPercent": 0.475,
        "numWheels": 2,
        "gearType": "Dual",
        "tirePressurePsi": 200.0,
        "tirePressureMpa": 1.379
    },
    {
        "name": "B777-300ER",
        "manufacturer": "Boeing",
        "grossWeightLbs": 775000.0,
        "grossWeightKg": 351534.0,
        "mgPercent": 0.95,
        "pcnMgPercent": 0.475,
        "numWheels": 6,
        "gearType": "Triple Dual Tandem",
        "tirePressurePsi": 220.0,
        "tirePressureMpa": 1.517
    },
    {
        "name": "B787-8",
        "manufacturer": "Boeing",
        "grossWeightLbs": 502500.0,
        "grossWeightKg": 227930.0,
        "mgPercent": 0.95,
        "pcnMgPercent": 0.475,
        "numWheels": 4,
        "gearType": "Dual Tandem",
        "tirePressurePsi": 220.0,
        "tirePressureMpa": 1.517
    },
    {
        "name": "A350-900",
        "manufacturer": "Airbus",
        "grossWeightLbs": 601650.0,
        "grossWeightKg": 272900.0,
        "mgPercent": 0.95,
        "pcnMgPercent": 0.475,
        "numWheels": 4,
        "gearType": "Dual Tandem",
        "tirePressurePsi": 220.0,
        "tirePressureMpa": 1.517
    },
    {
        "name": "A380-800 WV000",
        "manufacturer": "Airbus",
        "grossWeightLbs": 1239000.0,
        "grossWeightKg": 562000.0,
        "mgPercent": 0.3804,
        "pcnMgPercent": 0.19,
        "numWheels": 4,
        "gearType": "Wing/Body",
        "tirePressurePsi": 218.0,
        "tirePressureMpa": 1.503
    },
    {
        "name": "B747-400",
        "manufacturer": "Boeing",
        "grossWeightLbs": 875000.0,
        "grossWeightKg": 396893.0,
        "mgPercent": 0.95,
        "pcnMgPercent": 0.475,
        "numWheels": 4,
        "gearType": "Wing/Body",
        "tirePressurePsi": 205.0,
        "tirePressureMpa": 1.413
    },
    {
        "name": "C-17 Globemaster",
        "manufacturer": "Military",
        "grossWeightLbs": 585000.0,
        "grossWeightKg": 265352.0,
        "mgPercent": 0.95,
        "pcnMgPercent": 0.475,
        "numWheels": 6,
        "gearType": "Multi-wheel",
        "tirePressurePsi": 142.0,
        "tirePressureMpa": 0.979
    }
]

def load_aircraft_database() -> List[Dict]:
    """Load the full FAA aircraft database."""
    if os.path.exists(_DB_PATH):
        try:
            with open(_DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data:
                    return data
        except Exception:
            pass
    return _DEFAULT_AIRCRAFT

AIRCRAFT_DB = load_aircraft_database()

def get_aircraft_by_name(name: str) -> Optional[Dict]:
    """Search for an aircraft by exact or partial name."""
    name_clean = name.strip().lower()
    for ac in AIRCRAFT_DB:
        if ac["name"].lower() == name_clean:
            return ac
    for ac in AIRCRAFT_DB:
        if name_clean in ac["name"].lower():
            return ac
    return None

def get_all_manufacturers() -> List[str]:
    """Return sorted unique manufacturers."""
    mfgs = sorted({ac.get("manufacturer", "Other") for ac in AIRCRAFT_DB})
    return mfgs
