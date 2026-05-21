# Drone Control — Isaac Sim + Pegasus Simulator

A self-contained quadrotor flight controller for NVIDIA Isaac Sim using the Pegasus Simulator extension. Fly an Iris drone with a keyboard and/or joystick, with a live depth camera, minimap, and goal-input HUD — all in one window.

---

## Features

- **Hybrid input** — keyboard and joystick work simultaneously; joystick overrides when sticks are pushed
- **Geometric nonlinear controller** — SE(3) position + attitude control (no PX4 / ROS required)
- **Software depth camera** — PhysX ray-cast based, no GPU render pipeline needed
- **Unified HUD** — single `omni.ui` window with depth view, minimap, status, and manual goal entry
- **Auto-install pip deps** — `run.py` installs missing packages automatically on first launch
- **Portable** — copy only the `examples/drone_control/` folder to any machine with Isaac Sim + Pegasus

---

## Project Structure

```
examples/drone_control/
├── run.py            Entry point — checks deps, starts SimulationApp, launches DroneApp
├── app.py            DroneApp — wires world, drone, camera, depth, HUD
├── controller.py     HybridController — keyboard + joystick flight control (Backend)
├── depth_camera.py   SoftwareDepthCamera (PhysX) + FrustumDrawer (debug overlay)
├── hud.py            DroneHUD — unified omni.ui window (depth, minimap, status, goal)
├── drone_config.py   All tunable constants in one place
└── requirements.txt  pip packages (auto-installed by run.py)
```

---

## System Requirements

| Component | Version |
|---|---|
| NVIDIA Isaac Sim | 4.x or 5.x |
| Pegasus Simulator extension | latest compatible with your Isaac Sim |
| NVIDIA GPU + driver | required by Isaac Sim |
| Python | bundled with Isaac Sim (do **not** use system Python) |

> The pip packages (`numpy`, `scipy`, `opencv-python`, `inputs`) are installed automatically by `run.py` into Isaac Sim's Python environment.

---

## Running on a New Computer

### 1. Install Isaac Sim

Download and install NVIDIA Isaac Sim from the [Omniverse Launcher](https://www.nvidia.com/en-us/omniverse/) or follow the [Isaac Sim documentation](https://docs.omniverse.nvidia.com/isaacsim/).

### 2. Install the Pegasus Simulator Extension

Follow the [Pegasus Simulator installation guide](https://pegasussimulator.github.io/PegasusSimulator/).  
After installation, enable the extension inside Isaac Sim:  
**Window → Extensions → search "Pegasus" → Enable**

### 3. Copy the `drone_control` folder

```bash
# Clone this repo (or copy just the folder)
git clone https://github.com/DongSearch/PegasusSimulator.git
# The only folder you need:
# PegasusSimulator/examples/drone_control/
```

### 4. Find Isaac Sim's Python executable

Isaac Sim ships its own Python. Its location depends on your install method:

| Install method | Python path |
|---|---|
| Omniverse Launcher (Linux) | `~/.local/share/ov/pkg/isaac-sim-*/python.sh` |
| Omniverse Launcher (Windows) | `C:\Users\<user>\AppData\Local\ov\pkg\isaac-sim-*\python.bat` |
| Docker / custom | `<isaac_sim_root>/python.sh` |

### 5. Launch

```bash
# Linux
~/.local/share/ov/pkg/isaac-sim-4.x.x/python.sh  examples/drone_control/run.py

# Windows (Command Prompt)
C:\...\isaac-sim-4.x.x\python.bat  examples\drone_control\run.py

# Headless mode (no GUI window, for remote / CI)
~/.local/share/ov/pkg/isaac-sim-4.x.x/python.sh  examples/drone_control/run.py --headless
```

On first run, missing pip packages are installed automatically. Subsequent launches skip the check.

---

## Controls

### Keyboard

| Key | Action |
|---|---|
| `T` | Takeoff |
| `L` | Land |
| `W` / `S` | Fly forward / backward |
| `A` / `D` | Strafe left / right |
| `Q` / `E` | Yaw left / right |
| `↑` / `↓` | Increase / decrease altitude |

### Joystick (Xbox / PS layout)

| Input | Action |
|---|---|
| `A` / `×` (south button) | Takeoff |
| `B` / `○` (east button) | Land |
| Left stick up/down | Fly forward / backward |
| Left stick left/right | Strafe |
| Right stick left/right | Yaw |
| Right stick up/down | Altitude |

> Joystick sticks override keyboard movement while pushed beyond the dead zone. Both inputs can trigger takeoff/land independently.

---

## HUD Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  LEFT PANEL (400 px)              RIGHT PANEL                   │
│  ─────────────────                ──────────                    │
│  Keyboard hints                   Depth GRAY  │  Depth COLOR    │
│  Joystick hints                   (320×240)   │  (320×240)      │
│                                   ────────────────────────────  │
│  Live status                      MINIMAP (480×300)             │
│  • Input source                   • Grid  • Drone dot           │
│  • Airborne / Landed              • Heading arrow               │
│  • Position XYZ                   • FOV cone                    │
│  • Target XYZ                     • Goal crosshair              │
│                                   ────────────────────────────  │
│  Manual goal entry                Map status label              │
│  [X] [Y] [Z]  [Go]  [Land]                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Configuration (`drone_config.py`)

| Parameter | Default | Description |
|---|---|---|
| `TAKEOFF_ALT` | `1.5` m | Target altitude on takeoff |
| `MOVE_SPEED` | `3.0` m/s | Translation speed (keyboard & joystick) |
| `YAW_RATE_DEG` | `90.0` °/s | Yaw rotation speed |
| `KP / KD / KI` | `10 / 8.5 / 1.5` | Position PID gains |
| `KR / KW` | `3.5 / 0.5` | Attitude control gains |
| `DRONE_MASS` | `1.5` kg | Must match the Iris URDF |
| `DEPTH_RES_W/H` | `64 × 48` px | Depth ray-cast grid resolution |
| `DEPTH_FOV_DEG` | `70°` | Horizontal field of view |
| `DEPTH_MAX_M` | `15.0` m | Maximum depth range |
| `DEPTH_UPDATE_N` | `8` | Re-cast depth every N physics steps |
| `SPAWN_X/Y/Z` | `0, 0, 0.07` m | Initial drone spawn position |

---

## Troubleshooting

All errors below were encountered during development on Isaac Sim 5.1 with the
PegasusSimulator extension cloned locally. Solutions are listed in the order they
typically appear on a fresh setup.

---

### Import / Module errors

#### `ModuleNotFoundError: No module named 'pegasus'`

**Cause:** `pegasus.simulator` is not part of Isaac Sim — it is a separate extension
that must be present on the Python path before any `from pegasus.simulator...` import.

**Fix (this repo):** `run.py` already adds the cloned extension to `sys.path`
automatically. All you need is the extension source to be cloned next to this repo:

```
gidong_ws/
├── PegasusSimulator/          ← this repo
└── PegasusSimulator_ext/      ← official extension source (clone once)
```

```bash
cd /home/rokey/gidong_ws
git clone https://github.com/PegasusSimulator/PegasusSimulator.git PegasusSimulator_ext
```

`run.py` resolves the path relative to itself, so no further configuration is needed.

**Fix (other machines / standard install):**

```bash
# 1. Clone the extension
git clone https://github.com/PegasusSimulator/PegasusSimulator.git

# 2. Install into Isaac Sim's Python environment
cd PegasusSimulator
<isaac_sim_python> -m pip install --editable extensions/pegasus.simulator

# 3. Enable inside Isaac Sim UI
#    Window → Extensions → search "Pegasus" → Enable
```

---

#### `ModuleNotFoundError: No module named 'pymavlink'`

**Cause:** `multirotor.py` unconditionally imports `PX4MavlinkBackend`, which imports
`pymavlink`. This happens even if you never use the PX4 backend — the import cannot
be skipped. The error appears as soon as `Multirotor` or `MultirotorConfig` is imported.

**Fix:** Install `pymavlink` into Isaac Sim's Python environment (one-time, per machine):

```bash
# Linux — source install
<isaac_sim_root>/_build/linux-x86_64/release/python.sh -m pip install pymavlink

# Example path on this machine:
/home/rokey/dev_ws/isaac_sim/isaacsim/_build/linux-x86_64/release/python.sh -m pip install pymavlink
```

This covers both `px4_mavlink_backend.py` and `ardupilot_mavlink_backend.py` since
both import `pymavlink`.

**Also required — patch the extension `__init__.py`:**  
The extension's `pegasus/simulator/__init__.py` eagerly imports the full Isaac Sim
extension class, which pulls in the UI layer and all backends. Comment out that line
so the Python library can be used standalone:

```python
# In PegasusSimulator_ext/extensions/pegasus.simulator/pegasus/simulator/__init__.py
# Comment out:
# from .extension import Pegasus_SimulatorExtension
```

This patch is already applied in `PegasusSimulator_ext/` in this workspace.  
If you re-clone the extension, reapply it.

---

#### `NameError: name 'LOADER_DIR' is not defined`

**Cause:** Isaac Sim's cv2 prebundle contains a file at  
`omni.pip.compute/pip_prebundle/cv2/config.py`.  
When cv2 loads, it caches that file in `sys.modules` under the key `config`.  
Any subsequent `from config import ...` in your code resolves to cv2's file
instead of the local one — regardless of `sys.path` order.

**Fix (already applied):** The local settings file was renamed from `config.py` to
`drone_config.py`. All four files that import it (`app.py`, `controller.py`,
`depth_camera.py`, `hud.py`) use `from drone_config import ...`.

If you copied the project from an older version that still has `config.py`:

```bash
mv examples/drone_control/config.py examples/drone_control/drone_config.py
# Then in app.py, controller.py, depth_camera.py, hud.py:
# replace every  'from config import'  with  'from drone_config import'
```

---

#### `ModuleNotFoundError: No module named 'isaacsim'`

**Cause:** You are running with system Python instead of Isaac Sim's bundled Python.
`isaacsim`, `omni`, `carb`, and `pxr` are only available inside Isaac Sim's Python.

**Fix:** Use Isaac Sim's `python.sh` / `python.bat` to launch the script:

```bash
# Linux
~/.local/share/ov/pkg/isaac-sim-4.x.x/python.sh examples/drone_control/run.py

# Or with the source-install path on this machine:
/home/rokey/dev_ws/isaac_sim/isaacsim/_build/linux-x86_64/release/python.sh examples/drone_control/run.py
```

See *Step 4 — Find Isaac Sim's Python executable* above for all install-method paths.

---

### Input issues

**`[Ctrl] no gamepad found — keyboard only`**  
Plug in the controller before launching. Or install the `inputs` package manually:
```bash
<isaac_sim_python> -m pip install inputs
```

**`[Ctrl] keyboard failed: ...`**  
The Isaac Sim viewport must have focus for keyboard events to register. Click on
the 3D viewport after launch.

---

### Simulation / visual issues

**Drone spins or drifts after takeoff**  
Tune `KP`, `KD`, `KI` in `drone_config.py`. Lower `KP` first if oscillation is seen.

**Depth image shows all white (max range)**  
The PhysX scene query interface failed to initialize. Check the Isaac Sim log for
`[DepthCam]` messages.

**Black Gridroom environment not found**  
The Pegasus extension assets were not downloaded. Re-run the Pegasus setup script and
confirm the extension is enabled in **Window → Extensions**.
