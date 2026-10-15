"""
PyInstaller Build Script for Airport FWD Data Analyzer
Generates a standalone Windows .exe file containing the complete application:
FastAPI server, Uvicorn, scientific libraries, static web app, and sample data.
"""

import os
import sys
import subprocess
import shutil

def build():
    print("=" * 70)
    print("  BUILDING STANDALONE WINDOWS EXECUTABLE (.EXE)")
    print("  Airport FWD Data Analyzer & FAA Pavement Evaluator")
    print("=" * 70)

    # Clean old build/dist if present
    for d in ["build", "dist"]:
        if os.path.exists(d):
            print(f"[*] Removing old {d} folder...")
            try:
                shutil.rmtree(d)
            except Exception as e:
                print(f"[!] Warning: Could not remove {d}: {e}")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=AirportFWDAnalyzer",
        "--onedir",             # onedir is faster to launch and more reliable for large scientific apps
        "--noconfirm",
        "--clean",
        "--add-data=engine/aircraft_db.json;engine",
        "--add-data=web;web",
        "--add-data=sample_data;sample_data",
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.loops",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=uvicorn.protocols",
        "--hidden-import=uvicorn.protocols.http",
        "--hidden-import=uvicorn.protocols.http.auto",
        "--hidden-import=uvicorn.protocols.websockets",
        "--hidden-import=uvicorn.protocols.websockets.auto",
        "--hidden-import=uvicorn.lifespan",
        "--hidden-import=uvicorn.lifespan.on",
        "--hidden-import=scipy.optimize",
        "--hidden-import=scipy.integrate",
        "--hidden-import=scipy.special",
        "--hidden-import=engine",
        "run_app.py"
    ]

    print(f"[*] Running command:\n    {' '.join(cmd)}\n")
    proc = subprocess.run(cmd)

    if proc.returncode == 0:
        exe_path = os.path.abspath("dist/AirportFWDAnalyzer/AirportFWDAnalyzer.exe")
        print("\n" + "=" * 70)
        print("  BUILD SUCCESSFUL!")
        print(f"  Executable created at:\n  {exe_path}")
        print("=" * 70)
    else:
        print(f"\n[!] Build failed with exit code {proc.returncode}")
        sys.exit(proc.returncode)

if __name__ == "__main__":
    build()
