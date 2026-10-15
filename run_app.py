"""
Airport FWD Data Analyzer & FAA Pavement Evaluator
One-click application launcher. Starts server and opens web browser automatically.
"""

import os
import sys
import time
import webbrowser
import threading

def check_dependencies():
    """Verify that required packages are installed."""
    if getattr(sys, 'frozen', False):
        return
    required = ["fastapi", "uvicorn", "numpy", "scipy"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"[!] Warning: Missing dependencies: {', '.join(missing)}")
        print(f"    Installing via pip: pip install {' '.join(missing)}")
        os.system(f"{sys.executable} -m pip install {' '.join(missing)}")

def open_browser(url: str, delay_seconds: float = 1.2):
    """Opens browser after server starts."""
    time.sleep(delay_seconds)
    print(f"\n[*] Launching browser: {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[*] Could not open browser automatically: {e}")
        print(f"[*] Please navigate to {url} manually.")

def main():
    print("=" * 70)
    print("  AIRPORT FWD DATA ANALYZER & FAA PAVEMENT EVALUATOR")
    print("  FAA AC 150/5320-6G • BAKFAA 3.4.4 • FAARFIELD 2.1")
    print("=" * 70)

    check_dependencies()

    port = 8000
    host = "127.0.0.1"
    url = f"http://{host}:{port}"

    print(f"[*] Server starting on {url} ...")
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    import uvicorn
    from server import app
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    main()
