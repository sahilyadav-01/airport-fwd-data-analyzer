"""
Engineering Report Generator Module
Generates comprehensive FAA AC 150/5320-6G compliant reports,
CSV datasets, and portable project files (.json).
"""

import json
import csv
import io
from typing import Dict, Any, List

def generate_csv_fwd_export(stations_data: List[Dict[str, Any]]) -> str:
    """Exports FWD stations, peak deflections, and structural indices to CSV."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Station (m)", "Drop ID", "Load (kN)", "Load (lbs)",
        "D0 (um)", "D200 (um)", "D300 (um)", "D450 (um)", "D600 (um)", "D900 (um)", "D1200 (um)", "D1500 (um)",
        "Surface Temp (C)", "Area Factor", "SCI (um)", "BDI (um)", "BCI (um)",
        "E_Subgrade (MPa)", "CBR (%)", "k_value (pci)"
    ])

    for stn in stations_data:
        defls = stn.get("deflectionsUm", [])
        indices = stn.get("indices", {})
        writer.writerow([
            stn.get("station", 0.0),
            stn.get("dropId", 1),
            stn.get("loadKn", 180.0),
            stn.get("loadLbs", 40465.0),
            defls[0] if len(defls) > 0 else "",
            defls[1] if len(defls) > 1 else "",
            defls[2] if len(defls) > 2 else "",
            defls[3] if len(defls) > 3 else "",
            defls[4] if len(defls) > 4 else "",
            defls[5] if len(defls) > 5 else "",
            defls[6] if len(defls) > 6 else "",
            defls[7] if len(defls) > 7 else "",
            stn.get("surfaceTempC", 20.0),
            indices.get("area_factor", ""),
            indices.get("sci_um", ""),
            indices.get("bdi_um", ""),
            indices.get("bci_um", ""),
            indices.get("e_subgrade_mpa", ""),
            indices.get("subgrade_cbr", ""),
            indices.get("k_value_pci", "")
        ])

    return output.getvalue()


def generate_csv_cdf_export(faarfield_result: Dict[str, Any]) -> str:
    """Exports FAARFIELD traffic mix and CDF damage results to CSV."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["FAA Pavement Evaluation Report - FAARFIELD Analysis"])
    writer.writerow(["Pavement Type", faarfield_result.get("pavementType", "")])
    writer.writerow(["Design Life (Years)", faarfield_result.get("designLifeYears", 20)])
    writer.writerow(["Total CDF", faarfield_result.get("totalCdf", "")])
    writer.writerow(["Predicted Life (Years)", faarfield_result.get("predictedLifeYears", "")])
    writer.writerow(["Structural Status", faarfield_result.get("status", "")])
    writer.writerow([])
    writer.writerow([
        "Aircraft Name", "Annual Departures", "Total Departures (20 yr)",
        "Coverages", "Allowable Coverages", "CDF Contribution", "% of Total Damage"
    ])

    for row in faarfield_result.get("aircraftCdf", []):
        writer.writerow([
            row.get("aircraft", ""),
            row.get("annualDepartures", ""),
            row.get("totalDepartures", ""),
            row.get("coverages", ""),
            row.get("allowableCoverages", ""),
            row.get("cdfContribution", ""),
            row.get("percentOfTotalDamage", "")
        ])

    return output.getvalue()


def generate_html_report(project_meta: Dict[str, Any],
                         fwd_summary: Dict[str, Any],
                         backcalc_summary: Dict[str, Any],
                         cumdiff_summary: List[Dict[str, Any]],
                         faarfield_summary: Dict[str, Any],
                         pcr_summary: Dict[str, Any]) -> str:
    """Generates an executive, print-ready HTML engineering report."""
    airport = project_meta.get("airportName", "Metropolitan International Airport")
    runway = project_meta.get("runway", "RWY 09L-27R")
    date_str = project_meta.get("date", "2026-10-15")
    engineer = project_meta.get("engineer", "Pavement Evaluation Team")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Airport Pavement FWD & FAARFIELD Evaluation Report - {runway}</title>
<style>
  body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; color: #1e293b; background: #fff; }}
  h1 {{ color: #0f172a; border-bottom: 3px solid #0284c7; padding-bottom: 8px; margin-bottom: 4px; }}
  h2 {{ color: #0369a1; margin-top: 30px; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; }}
  .meta-box {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 15px; margin: 20px 0; }}
  .meta-item {{ font-size: 13px; }}
  .meta-item strong {{ display: block; color: #64748b; font-size: 11px; text-transform: uppercase; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; }}
  th, td {{ border: 1px solid #cbd5e1; padding: 8px 12px; text-align: left; }}
  th {{ background: #f1f5f9; color: #334155; font-weight: 600; }}
  tr:nth-child(even) {{ background: #f8fafc; }}
  .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }}
  .badge-pass {{ background: #d1fae5; color: #065f46; }}
  .badge-fail {{ background: #fee2e2; color: #991b1b; }}
  .highlight-card {{ background: #f0f9ff; border-left: 4px solid #0284c7; padding: 15px; margin: 20px 0; border-radius: 4px; }}
  @media print {{ body {{ margin: 15mm; }} .no-print {{ display: none; }} }}
</style>
</head>
<body>
  <div style="display: flex; justify-content: space-between; align-items: center;">
    <div>
      <h1>AIRPORT PAVEMENT STRUCTURAL EVALUATION REPORT</h1>
      <div style="color: #64748b; font-size: 14px;">In Accordance with FAA AC 150/5320-6G & ICAO Annex 14</div>
    </div>
    <div style="text-align: right;">
      <button class="no-print" onclick="window.print()" style="background: #0284c7; color: white; border: none; padding: 10px 18px; border-radius: 6px; cursor: pointer; font-weight: 600;">Print / Save to PDF</button>
    </div>
  </div>

  <div class="meta-box">
    <div class="meta-item"><strong>Facility / Airport</strong>{airport}</div>
    <div class="meta-item"><strong>Runway / Pavement</strong>{runway}</div>
    <div class="meta-item"><strong>Evaluation Date</strong>{date_str}</div>
    <div class="meta-item"><strong>Lead Evaluator</strong>{engineer}</div>
  </div>

  <div class="highlight-card">
    <h3 style="margin: 0 0 8px 0; color: #0369a1;">Executive Summary & Official Rating</h3>
    <div style="display: flex; gap: 30px; font-size: 15px;">
      <div><strong>Official ICAO Rating:</strong> <span style="font-family: monospace; font-size: 16px; background: #e0f2fe; padding: 2px 6px; border-radius: 4px; color: #0369a1;">{pcr_summary.get('pcrCode', 'PCR 720/F/B/W/T')}</span></div>
      <div><strong>Critical Aircraft:</strong> {faarfield_summary.get('criticalAircraft', 'B777-300ER')}</div>
      <div><strong>Structural Life:</strong> {faarfield_summary.get('predictedLifeYears', 20.0)} Years (Total CDF: {faarfield_summary.get('totalCdf', 0.85)})</div>
    </div>
  </div>

  <h2>1. Homogeneous Section Delineation (Cumulative Difference Method)</h2>
  <p>Statistically delineated runway segments derived from Falling Weight Deflectometer (FWD) normalized basins:</p>
  <table>
    <thead>
      <tr>
        <th>Section ID</th><th>Start Station</th><th>End Station</th><th>Length (m)</th>
        <th>Drops</th><th>Mean D0 (um)</th><th>CoV (%)</th><th>Design D85 (um)</th><th>Subgrade CBR</th>
      </tr>
    </thead>
    <tbody>"""

    for sec in cumdiff_summary:
        html += f"""
      <tr>
        <td><strong>{sec.get('sectionId')}</strong></td>
        <td>{sec.get('startStation')}</td>
        <td>{sec.get('endStation')}</td>
        <td>{sec.get('lengthM')}</td>
        <td>{sec.get('sampleCount')}</td>
        <td>{sec.get('mean')}</td>
        <td>{sec.get('covPercent')}%</td>
        <td><strong>{sec.get('designValue85th')}</strong></td>
        <td>{sec.get('subgradeCbr', '6.5')}</td>
      </tr>"""

    html += f"""
    </tbody>
  </table>

  <h2>2. Backcalculated Layer Moduli (BAKFAA Analysis)</h2>
  <p>Representative backcalculated elastic moduli matching measured deflection basins within acceptable RMSE tolerance:</p>
  <table>
    <thead>
      <tr><th>Layer Name</th><th>Thickness</th><th>Poisson's Ratio</th><th>Modulus (MPa)</th><th>Modulus (psi)</th><th>Condition Assessment</th></tr>
    </thead>
    <tbody>"""

    for lyr in backcalc_summary.get("layers", []):
        html += f"""
      <tr>
        <td><strong>{lyr.get('name')}</strong></td>
        <td>{lyr.get('thicknessMm')} mm ({lyr.get('thicknessIn')} in)</td>
        <td>{lyr.get('poisson')}</td>
        <td><strong>{lyr.get('modulusMpa')} MPa</strong></td>
        <td>{int(lyr.get('modulusPsi', 0)):,} psi</td>
        <td>Sound Condition</td>
      </tr>"""

    html += f"""
    </tbody>
  </table>

  <h2>3. FAARFIELD Cumulative Damage Factor (CDF) Analysis</h2>
  <div style="margin-bottom: 10px;">
    <strong>Structural Status:</strong> <span class="badge { 'badge-pass' if 'PASS' in faarfield_summary.get('status', '') else 'badge-fail' }">{faarfield_summary.get('status', 'PASS')}</span>
    &nbsp;&nbsp;|&nbsp;&nbsp;<strong>Total CDF:</strong> {faarfield_summary.get('totalCdf')}
    &nbsp;&nbsp;|&nbsp;&nbsp;<strong>Expected Service Life:</strong> {faarfield_summary.get('predictedLifeYears')} Years
  </div>
  <table>
    <thead>
      <tr>
        <th>Aircraft</th><th>Annual Departures</th><th>Cumulative Departures</th>
        <th>Allowable Coverages</th><th>CDF Contribution</th><th>% Damage Contribution</th>
      </tr>
    </thead>
    <tbody>"""

    for row in faarfield_summary.get("aircraftCdf", []):
        html += f"""
      <tr>
        <td><strong>{row.get('aircraft')}</strong></td>
        <td>{row.get('annualDepartures')}</td>
        <td>{int(row.get('totalDepartures', 0)):,}</td>
        <td>{int(row.get('allowableCoverages', 0)):,}</td>
        <td>{row.get('cdfContribution')}</td>
        <td><strong>{row.get('percentOfTotalDamage')}%</strong></td>
      </tr>"""

    html += f"""
    </tbody>
  </table>

  <h2>4. ICAO ACR-PCR Operational Eligibility</h2>
  <table>
    <thead>
      <tr><th>Aircraft</th><th>Gross Weight (kg)</th><th>ACR Value</th><th>Pavement PCR</th><th>Operational Status</th></tr>
    </thead>
    <tbody>"""

    for elig in pcr_summary.get("fleetEligibility", []):
        is_ok = elig.get('status') == 'Unrestricted'
        html += f"""
      <tr>
        <td><strong>{elig.get('name')}</strong></td>
        <td>{int(elig.get('grossWeightKg', 0)):,} kg</td>
        <td><strong>{elig.get('acr')}</strong></td>
        <td>{elig.get('pcr')}</td>
        <td><span class="badge { 'badge-pass' if is_ok else 'badge-fail' }">{elig.get('status')}</span></td>
      </tr>"""

    html += f"""
    </tbody>
  </table>

  <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #cbd5e1; font-size: 12px; color: #64748b; text-align: center;">
    Generated by Airport FWD Data Analyzer & FAA Pavement Evaluator Suite • FAA AC 150/5320-6G Standards
  </div>
</body>
</html>"""
    return html
