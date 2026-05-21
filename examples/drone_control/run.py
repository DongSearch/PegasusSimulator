#!/usr/bin/env python3
"""
drone_control/run.py  —  ENTRY POINT

Steps performed on startup:
  1. Check for pip-installable dependencies (numpy, scipy, opencv-python, inputs).
     Missing packages are installed automatically via pip.
  2. Start Isaac Sim's SimulationApp  ← MUST happen before any omni/carb/pegasus import.
  3. Import and launch DroneApp.

Usage:
    python run.py              # normal GUI mode
    python run.py --headless   # no window (for remote / CI use)

System requirements (not auto-installed — must be set up manually):
    • NVIDIA Isaac Sim 4.x / 5.x  (provides isaacsim, omni.*, carb, pxr)
    • Pegasus Simulator extension  (provides pegasus.simulator.*)
    • NVIDIA GPU + matching driver
"""

import subprocess
import sys
import importlib
import os

# Add this folder to Python path so local modules (app, controller, …) are found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Add the PegasusSimulator extension to the Python path so 'pegasus.simulator.*' is importable.
# The extension lives in the workspace alongside this project.
_PEGASUS_EXT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),  # .../drone_control/
    "..", "..", "..",                             # .../gidong_ws/
    "PegasusSimulator_ext", "extensions", "pegasus.simulator",
)
sys.path.insert(0, os.path.normpath(_PEGASUS_EXT))

# ── 1. Dependency check + auto-install ───────────────────────────────────── #

# Map: import_name → pip install spec
_DEPS = {
    "numpy":  "numpy>=1.24",
    "scipy":  "scipy>=1.10",
    "cv2":    "opencv-python>=4.8",
    "inputs": "inputs>=0.5",
}


def _ensure_deps():
    missing = []
    for import_name, pip_spec in _DEPS.items():
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing.append(pip_spec)

    if not missing:
        return

    print(f"[run] Installing missing packages: {missing}")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet"] + missing,
            stderr=subprocess.STDOUT,
        )
        print("[run] Packages installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[run] pip install failed: {e}")
        print("[run] Please install manually:  pip install " + " ".join(missing))
        sys.exit(1)


# ── 2. Launch ─────────────────────────────────────────────────────────────── #

if __name__ == "__main__":
    _ensure_deps()

    # SimulationApp MUST be created before any omni / carb / pegasus import
    from isaacsim import SimulationApp   # noqa: E402  (intentional late import)

    headless = "--headless" in sys.argv
    simulation_app = SimulationApp({"headless": headless, "anti_aliasing": 0})

    # All further imports happen after Isaac Sim is live
    from app import DroneApp             # noqa: E402
    DroneApp(simulation_app).run()
