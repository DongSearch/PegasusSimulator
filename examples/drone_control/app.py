"""
drone_control/app.py
DroneApp — main Isaac Sim application.

Spawns a single Iris quadrotor in the Black Gridroom environment,
wires up keyboard + joystick control, depth camera, and the unified HUD.
No warehouse, no grab system, no ArUco — pure drone flight.

Called from run.py after SimulationApp has been started.
"""

import os
import sys
import numpy as np
import carb
import omni.timeline
import omni.usd
from omni.isaac.core.world import World
from scipy.spatial.transform import Rotation

from pegasus.simulator.params import ROBOTS, SIMULATION_ENVIRONMENTS
from pegasus.simulator.logic.vehicles.multirotor import Multirotor, MultirotorConfig
from pegasus.simulator.logic.interface.pegasus_interface import PegasusInterface

# Make local modules importable regardless of working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    SPAWN_X, SPAWN_Y, SPAWN_Z,
    CAM_PRIM_PATH, CAM_FOCAL_LENGTH, CAM_MOUNT_FWD,
    DEPTH_UPDATE_N,
)
from controller  import HybridController
from depth_camera import SoftwareDepthCamera, FrustumDrawer
from hud          import DroneHUD


class DroneApp:
    WARMUP_STEPS = 200   # physics steps before enabling depth capture + HUD

    def __init__(self, simulation_app):
        self._sim_app = simulation_app
        self.timeline = omni.timeline.get_timeline_interface()

        # ── World ─────────────────────────────────────────────────────────
        pg = PegasusInterface()
        pg._world = World(**pg._world_settings)
        self.world = pg.world
        pg.load_environment(SIMULATION_ENVIRONMENTS["Black Gridroom"])

        # ── Drone ─────────────────────────────────────────────────────────
        self.controller = HybridController()
        cfg = MultirotorConfig()
        cfg.backends = [self.controller]

        Multirotor(
            "/World/quadrotor", ROBOTS["Iris"], 0,
            [SPAWN_X, SPAWN_Y, SPAWN_Z],
            Rotation.from_euler("XYZ", [0, 0, 0], degrees=True).as_quat(),
            config=cfg,
        )

        self.world.reset()

        # ── Front-facing RGB camera prim (drives the viewport) ────────────
        stage = omni.usd.get_context().get_stage()
        try:
            from pxr import UsdGeom, Gf
            cam = UsdGeom.Camera.Define(stage, CAM_PRIM_PATH)
            cam.GetFocalLengthAttr().Set(CAM_FOCAL_LENGTH)
            xf = UsdGeom.Xformable(cam.GetPrim())
            xf.AddTranslateOp().Set(Gf.Vec3d(CAM_MOUNT_FWD, 0.0, 0.0))
            xf.AddRotateYOp().Set(-90.0)   # look forward (+X in drone frame)
            carb.log_warn(f"[App] Camera prim OK → {CAM_PRIM_PATH}")
        except Exception as e:
            carb.log_warn(f"[App] Camera prim failed: {e}")

        # ── Sub-systems ───────────────────────────────────────────────────
        self.depth_cam = SoftwareDepthCamera()
        self.frustum   = FrustumDrawer()
        self.hud       = DroneHUD(self.controller)

        self._step_count = 0

        carb.log_warn(
            "\n╔══════════════════════════════════════╗"
            "\n║  Drone Control  —  Hybrid Input      ║"
            "\n╠══════════════════════════════════════╣"
            "\n║  KEYBOARD: T=Takeoff  L=Land         ║"
            "\n║    WASD=Move  QE=Yaw  ↑↓=Alt         ║"
            "\n╠══════════════════════════════════════╣"
            "\n║  JOYSTICK: A/×=Takeoff  B/○=Land     ║"
            "\n║    L-stick=Move  R-stick=Yaw/Alt      ║"
            "\n╚══════════════════════════════════════╝\n"
        )

    # ── Per-step update ────────────────────────────────────────────────────── #

    def _update(self):
        if self._step_count < self.WARMUP_STEPS:
            return
        if not self.controller._received_first_state:
            return

        drone_pos = self.controller.p
        drone_R   = self.controller.R

        depth = self.depth_cam.capture(drone_pos, drone_R,
                                       update_every=DEPTH_UPDATE_N)
        if depth is None:
            return

        self.hud.update_depth(depth, float(drone_pos[2]))
        self.hud.update_status(
            self.controller.active_input,
            self.controller.is_airborne,
            drone_pos,
            self.controller.target_pos,
        )
        self.hud.update_map(
            drone_pos,
            drone_R,
            self.controller.target_pos if self.controller.is_airborne else None,
        )

        cam_origin = drone_pos + drone_R.apply(
            np.array([CAM_MOUNT_FWD, 0.0, 0.0]))
        self.frustum.update(
            cam_origin, self.depth_cam._rays_body, drone_R, self.depth_cam)

    # ── Main loop ──────────────────────────────────────────────────────────── #

    def run(self):
        self.depth_cam.initialize()
        self.frustum.initialize()
        self.timeline.play()

        # Ensure keyboard subscription is active (timeline.play() calls start())
        if self.controller._key_sub is None:
            self.controller.start()

        # Open RGB camera viewport window
        try:
            from isaacsim.core.utils.viewports import create_viewport_for_camera
            create_viewport_for_camera(
                viewport_name="Drone Front Camera",
                camera_prim_path=CAM_PRIM_PATH,
                width=480, height=360,
            )
            carb.log_warn("[App] RGB viewport opened.")
        except Exception as e:
            carb.log_warn(f"[App] RGB viewport failed: {e}")

        while self._sim_app.is_running():
            self.world.step(render=True)
            self._step_count += 1
            self._update()

        carb.log_warn("[App] Shutting down.")
        self.controller.stop()
        self.timeline.stop()
        self._sim_app.close()
