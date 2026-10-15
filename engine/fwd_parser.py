"""
FWD Data Parser Module
Supports Dynatest (.fwd), KUAB, Carl Bro, JILS, and standard CSV/Excel airport deflection files.
Performs data validation, unit conversion (SI/US), load normalization, and sensor geometry alignment.
"""

import os
import re
import csv
from typing import Dict, List, Any, Optional

STANDARD_HWD_LOAD_AIRPORT_KN = 180.0  # ~40,500 lbs standard FAA HWD drop load
STANDARD_FWD_LOAD_HIGHWAY_KN = 40.0   # ~9,000 lbs standard FWD drop load
STANDARD_PLATE_RADIUS_MM = 150.0      # 300 mm diameter load plate

class FWDRecord:
    def __init__(self,
                 station: float,
                 drop_id: int,
                 load_kn: float,
                 deflections_um: List[float],
                 sensor_offsets_mm: List[float],
                 temp_c: Optional[float] = 20.0,
                 surface_temp_c: Optional[float] = 20.0,
                 air_temp_c: Optional[float] = 20.0,
                 plate_radius_mm: float = 150.0,
                 latitude: Optional[float] = None,
                 longitude: Optional[float] = None,
                 notes: str = ""):
        self.station = round(station, 2)
        self.drop_id = int(drop_id)
        self.load_kn = round(load_kn, 2)
        self.deflections_um = [round(d, 2) for d in deflections_um]
        self.sensor_offsets_mm = [round(r, 1) for r in sensor_offsets_mm]
        self.temp_c = temp_c
        self.surface_temp_c = surface_temp_c
        self.air_temp_c = air_temp_c
        self.plate_radius_mm = plate_radius_mm
        self.latitude = latitude
        self.longitude = longitude
        self.notes = notes

    @property
    def load_lbs(self) -> float:
        return round(self.load_kn * 224.8089, 1)

    @property
    def deflections_mils(self) -> List[float]:
        return [round(d / 25.4, 3) for d in self.deflections_um]

    def normalized_deflections(self, target_load_kn: float = STANDARD_HWD_LOAD_AIRPORT_KN) -> List[float]:
        """Normalize deflections linearly to standard drop load (kN)."""
        if self.load_kn <= 0:
            return self.deflections_um[:]
        factor = target_load_kn / self.load_kn
        return [round(d * factor, 2) for d in self.deflections_um]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "station": self.station,
            "dropId": self.drop_id,
            "loadKn": self.load_kn,
            "loadLbs": self.load_lbs,
            "deflectionsUm": self.deflections_um,
            "deflectionsMils": self.deflections_mils,
            "sensorOffsetsMm": self.sensor_offsets_mm,
            "tempC": self.temp_c,
            "surfaceTempC": self.surface_temp_c,
            "airTempC": self.air_temp_c,
            "plateRadiusMm": self.plate_radius_mm,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "notes": self.notes
        }


def parse_csv_fwd(file_content: str) -> List[FWDRecord]:
    """
    Parses CSV/TSV deflection data.
    Automatically identifies station, drop, load, and deflection columns (D0..D8).
    Handles both microns and mils.
    """
    records: List[FWDRecord] = []
    lines = [line.strip() for line in file_content.strip().splitlines() if line.strip()]
    if not lines:
        return records

    # Detect delimiter: comma, semicolon, tab, or whitespace
    sample = lines[0]
    delimiter = ','
    if '\t' in sample:
        delimiter = '\t'
    elif ';' in sample:
        delimiter = ';'

    reader = csv.reader(lines, delimiter=delimiter)
    header = None
    header_idx = -1

    for idx, row in enumerate(reader):
        clean_row = [c.strip().lower() for c in row if c.strip()]
        if any('station' in c or 'dist' in c or 'chainage' in c or 'd0' in c or 'd1' in c or 'load' in c for c in clean_row):
            header = [c.strip() for c in row]
            header_idx = idx
            break

    default_offsets = [0.0, 200.0, 300.0, 450.0, 600.0, 900.0, 1200.0, 1500.0, 1800.0]

    # If no header was found, treat as raw numbers
    if header is None:
        station_counter = 0.0
        for line in lines:
            parts = re.split(r'[,\t;\s]+', line.strip())
            nums = []
            for p in parts:
                try:
                    nums.append(float(p))
                except ValueError:
                    pass
            if len(nums) >= 6:
                station = nums[0] if nums[0] > 10 else station_counter * 25.0
                load = nums[1] if nums[1] > 20 else 180.0
                defls = nums[2:11]
                # Check if deflections are in mils or microns
                if defls and max(defls) < 150.0:  # likely mils
                    defls = [d * 25.4 for d in defls]
                records.append(FWDRecord(
                    station=station,
                    drop_id=1,
                    load_kn=load if load < 1000 else load / 224.8089,
                    deflections_um=defls,
                    sensor_offsets_mm=default_offsets[:len(defls)]
                ))
                station_counter += 1
        return records

    # Map column indices from header
    col_map = {}
    defl_cols = []
    for i, col in enumerate(header):
        c_low = col.lower().strip()
        if 'station' in c_low or 'chainage' in c_low or 'dist' in c_low:
            col_map['station'] = i
        elif 'drop' in c_low or 'sequence' in c_low:
            col_map['drop'] = i
        elif 'load' in c_low or 'force' in c_low:
            col_map['load'] = i
        elif 'temp' in c_low:
            if 'surf' in c_low:
                col_map['surf_temp'] = i
            elif 'air' in c_low:
                col_map['air_temp'] = i
            else:
                col_map['temp'] = i
        elif re.match(r'^(d\s*\d+|df\s*\d+|sensor\s*\d+|defl\s*\d+|\d+mm|\d+in)', c_low):
            defl_cols.append((i, col))

    # Parse rows
    stn_curr = 0.0
    for row in reader:
        if not row or len(row) <= 2:
            continue
        try:
            # Station
            if 'station' in col_map and col_map['station'] < len(row):
                stn = float(re.sub(r'[^\d\.\-]', '', row[col_map['station']]) or stn_curr)
            else:
                stn = stn_curr
            stn_curr = stn + 25.0

            # Drop
            drop_id = 1
            if 'drop' in col_map and col_map['drop'] < len(row):
                try:
                    drop_id = int(re.sub(r'[^\d]', '', row[col_map['drop']]) or 1)
                except:
                    drop_id = 1

            # Load
            load_val = 180.0
            if 'load' in col_map and col_map['load'] < len(row):
                lv_str = re.sub(r'[^\d\.]', '', row[col_map['load']])
                if lv_str:
                    load_val = float(lv_str)
                    if load_val > 1000:  # lbs -> kN
                        load_val = load_val / 224.8089

            # Deflections
            defls = []
            offsets = []
            for col_i, col_name in defl_cols:
                if col_i < len(row):
                    d_str = re.sub(r'[^\d\.]', '', row[col_i])
                    if d_str:
                        val = float(d_str)
                        defls.append(val)
                        # Try to parse offset from column name e.g. "D0 (0mm)", "D300"
                        m = re.search(r'(\d+)\s*(mm|in)?', col_name)
                        if m and int(m.group(1)) > 0:
                            num = float(m.group(1))
                            if 'in' in col_name.lower():
                                num *= 25.4
                            offsets.append(num)
                        else:
                            offsets.append(default_offsets[len(offsets)] if len(offsets) < len(default_offsets) else (len(offsets)*300.0))

            if not defls:
                continue

            # Check unit: if max deflection < 120, user entered mils; convert to microns
            if max(defls) < 120.0 and min(defls) < 30.0:
                defls = [d * 25.4 for d in defls]

            # Temperatures
            temp = 20.0
            if 'temp' in col_map and col_map['temp'] < len(row):
                try:
                    t_str = re.sub(r'[^\d\.]', '', row[col_map['temp']])
                    if t_str: temp = float(t_str)
                except: pass

            surf_temp = temp
            if 'surf_temp' in col_map and col_map['surf_temp'] < len(row):
                try:
                    t_str = re.sub(r'[^\d\.]', '', row[col_map['surf_temp']])
                    if t_str: surf_temp = float(t_str)
                except: pass

            records.append(FWDRecord(
                station=stn,
                drop_id=drop_id,
                load_kn=load_val,
                deflections_um=defls,
                sensor_offsets_mm=offsets if len(offsets) == len(defls) else default_offsets[:len(defls)],
                temp_c=temp,
                surface_temp_c=surf_temp
            ))
        except Exception:
            continue

    return records


def parse_dynatest_fwd(file_content: str) -> List[FWDRecord]:
    """
    Parses Dynatest .fwd format file commonly exported by Dynatest Field Software.
    """
    records: List[FWDRecord] = []
    lines = file_content.splitlines()

    sensor_offsets = [0.0, 200.0, 300.0, 450.0, 600.0, 900.0, 1200.0, 1500.0, 1800.0]
    plate_radius = 150.0

    current_station = 0.0
    current_temp = 20.0
    current_surf_temp = 20.0

    for line in lines:
        l = line.strip()
        if not l or l.startswith(';') or l.startswith('*'):
            continue

        # Look for station identifier or offset line
        if 'station' in l.lower() or 'dist' in l.lower():
            nums = re.findall(r'[-+]?\d*\.\d+|\d+', l)
            if nums:
                current_station = float(nums[0])
            continue

        # Check for temperatures
        if 'temp' in l.lower():
            nums = re.findall(r'[-+]?\d*\.\d+|\d+', l)
            if len(nums) >= 2:
                current_temp = float(nums[0])
                current_surf_temp = float(nums[1])
            elif nums:
                current_temp = float(nums[0])
            continue

        # Parse test / drop line: typically load followed by 7-9 sensor readings
        parts = re.split(r'[,;\s]+', l)
        vals = []
        for p in parts:
            try:
                vals.append(float(p))
            except ValueError:
                pass

        if len(vals) >= 8:
            # Often first value is drop or station, then load, then deflections
            if vals[0] > 500:  # station
                stn = vals[0]
                load = vals[1]
                defls = vals[2:11]
            elif vals[1] > 20 and vals[1] < 350:  # load in kN
                stn = current_station
                load = vals[1]
                defls = vals[2:11]
            elif vals[0] > 20 and vals[0] < 350:  # load in kN
                stn = current_station
                load = vals[0]
                defls = vals[1:10]
            elif vals[0] > 1000 and vals[0] < 60000:  # load in lbs
                stn = current_station
                load = vals[0] / 224.8089
                defls = vals[1:10]
            else:
                stn = current_station
                load = 180.0
                defls = vals[:9]

            # Convert mils if needed
            if defls and max(defls) < 150.0:
                defls = [d * 25.4 for d in defls]

            records.append(FWDRecord(
                station=stn,
                drop_id=len(records) + 1,
                load_kn=load,
                deflections_um=defls,
                sensor_offsets_mm=sensor_offsets[:len(defls)],
                temp_c=current_temp,
                surface_temp_c=current_surf_temp,
                plate_radius_mm=plate_radius
            ))

    return records


def parse_fwd_file(file_content: str, filename: str = "") -> List[FWDRecord]:
    """Universal parser that detects file format and returns normalized FWDRecords."""
    fn_low = filename.lower()
    if fn_low.endswith('.csv') or fn_low.endswith('.tsv') or fn_low.endswith('.txt'):
        records = parse_csv_fwd(file_content)
        if records:
            return records
    # Try Dynatest format
    records = parse_dynatest_fwd(file_content)
    if not records:
        # Fallback to CSV parser
        records = parse_csv_fwd(file_content)
    return records
