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
├── config.py         All tunable constants in one place
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

## Configuration (`config.py`)

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

**`ModuleNotFoundError: No module named 'pegasus'`**  
→ The Pegasus Simulator extension is not installed. The `pegasus.simulator.*` package is not part of Isaac Sim itself — it must be installed separately.

1. Clone the full PegasusSimulator repository:
   ```bash
   git clone https://github.com/PegasusSimulator/PegasusSimulator.git
   ```
2. Install the extension into Isaac Sim's Python environment:
   ```bash
   cd PegasusSimulator
   <isaac_sim_python> -m pip install --editable extensions/pegasus.simulator
   ```
   Replace `<isaac_sim_python>` with your Isaac Sim Python path (see step 4 in *Running on a New Computer* above).
3. Enable the extension inside Isaac Sim:  
   **Window → Extensions → search "Pegasus" → Enable**

> **Quick workaround** — if you just want to test without installing, add the path manually at the top of `run.py` (after `sys.path.insert` on line 27):
> ```python
> sys.path.insert(0, "/path/to/PegasusSimulator/extensions/pegasus.simulator")
> ```

---

**`ModuleNotFoundError: No module named 'pymavlink'`**  
→ Importing `pegasus.simulator.params` triggers the extension's `__init__.py`, which chains through the UI layer into the PX4/ArduPilot backends that require `pymavlink`. Since this app doesn't use those backends, the fix is to stop the `__init__.py` from eagerly loading the extension.

In the cloned `PegasusSimulator_ext` repo, edit:  
`extensions/pegasus.simulator/pegasus/simulator/__init__.py`

Comment out the extension import:
```python
# from .extension import Pegasus_SimulatorExtension
```

This is already applied in `PegasusSimulator_ext/` in this workspace. If you re-clone the extension, apply the same patch.

---

**`ModuleNotFoundError: No module named 'isaacsim'`**  
→ You are using system Python. Use Isaac Sim's bundled `python.sh` / `python.bat` instead.

**`[Ctrl] keyboard failed: ...`**  
→ The Isaac Sim window must have focus for keyboard events to register. Click on the viewport.

**`[Ctrl] no gamepad found — keyboard only`**  
→ Plug in the controller before launching, or install the `inputs` package manually:  
`<isaac_sim_python> -m pip install inputs`

**Drone spins or drifts after takeoff**  
→ Tune `KP`, `KD`, `KI` in `config.py`. Lower `KP` first if oscillation is observed.

**Depth image shows all white (max range)**  
→ PhysX scene query interface failed to initialize. Check the Isaac Sim log for `[DepthCam]` messages.

**Black Gridroom environment not found**  
→ The Pegasus extension must be enabled and its assets downloaded. Re-run the Pegasus setup script.
