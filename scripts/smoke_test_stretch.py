"""Headless smoke test: load Rs_int with the Stretch robot, step it, save one RGB frame.

Checks that the simulator, the GPU/driver and the downloaded assets all work together.
Expect roughly 3 minutes on the first run (shader compilation) and a flood of harmless
"DEPRECATED: get/setDofFrictionProperties" warnings.

Usage (with the environment activated):
    python scripts/smoke_test_stretch.py [output.png]
"""

import os
import sys
import time

os.environ.setdefault("OMNIGIBSON_HEADLESS", "1")
os.environ.setdefault("OMNI_KIT_ACCEPT_EULA", "YES")

import numpy as np
import torch as th

import omnigibson as og

OUT_PATH = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else "stretch_rgb.png")

cfg = {
    "scene": {"type": "InteractiveTraversableScene", "scene_model": "Rs_int"},
    "robots": [
        {
            # Note: "model" (not the deprecated "type") selects the robot in v3.9.3.
            "model": "stretch",
            "name": "stretch",
            "obs_modalities": ["rgb", "depth"],
            # The default camera resolution is 64x64, which is too small to eyeball.
            "sensor_config": {"VisionSensor": {"sensor_kwargs": {"image_height": 512, "image_width": 512}}},
        }
    ],
}


def walk(d, prefix=""):
    for k, v in d.items():
        if isinstance(v, dict):
            yield from walk(v, f"{prefix}{k}/")
        else:
            yield f"{prefix}{k}", v


try:
    t0 = time.time()
    env = og.Environment(configs=cfg)
    print(f"[smoke] env created in {time.time() - t0:.1f}s")
    # An OmniGibson env is always a set of parallel envs: robots is list[list[Robot]].
    robot = env.robots[0][0]
    print(f"[smoke] robot={type(robot).__name__} action_dim={robot.action_dim}")
    t1 = time.time()
    for _ in range(30):
        # step() takes a flat action tensor when there is a single env, and returns lists.
        obs_list, *_ = env.step(th.zeros(robot.action_dim))
    print(f"[smoke] 30 steps in {time.time() - t1:.1f}s")
    obs = obs_list[0]
    saved = False
    for k, v in walk(obs):
        print(f"[smoke] obs {k}: {tuple(v.shape) if hasattr(v, 'shape') else type(v).__name__}")
        if not saved and k.endswith("rgb") and hasattr(v, "ndim") and v.ndim == 3:
            from PIL import Image

            arr = v[..., :3].cpu().numpy()
            if arr.dtype != np.uint8:
                arr = (arr * 255 if arr.max() <= 1 else arr).clip(0, 255).astype(np.uint8)
            Image.fromarray(arr).save(OUT_PATH)
            saved = True
    print(f"[smoke] saved rgb to {OUT_PATH}: {saved}")
    print("[smoke] DONE")
finally:
    # Without this, an uncaught exception makes Python segfault on exit.
    og.shutdown()
