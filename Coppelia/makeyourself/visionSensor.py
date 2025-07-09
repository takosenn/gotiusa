# visionSensor
# visionsensorで距離を取得する

import numpy as np
from init_parameter import num_agents
from SecondD_ani_init import agent_positions
from target_move import target_pos
from connect_Coppeliasim import sim, visionSensorHandles

for j in range(num_agents):
    ro_i = None  # VisionSensorでの距離計測値
    try:
        visionSensorHandle = visionSensorHandles[j]
        result = sim.getVisionSensorDepth(visionSensorHandle)
        if result is not None:
            depthBuffer, resolution = result
            depthArray = np.array(depthBuffer, dtype=np.float64)
            if len(resolution) == 2:
                depthArray = depthArray.reshape(resolution)
            nearClip = sim.getObjectFloatParam(
                visionSensorHandle, sim.visionfloatparam_near_clipping
            )
            farClip = sim.getObjectFloatParam(
                visionSensorHandle, sim.visionfloatparam_far_clipping
            )
            realDepth = nearClip + (farClip - nearClip) * depthArray
            valid_mask = realDepth < (farClip - 1e-4)
            if np.any(valid_mask):
                minDist = np.min(realDepth[valid_mask])
                if np.isfinite(minDist):
                    ro_i = minDist
                    print(f"[Drone{j+1}] VisionSensorで検知: ro_i = {ro_i:.2f} m")
                else:
                    print(f"[Drone{j+1}] VisionSensor: 有効な物体なし")
            else:
                print(f"[Drone{j+1}] VisionSensor: 物体未検知")
    except Exception as e:
        print(f"[Drone{j+1}] VisionSensor error: {e}")

    if ro_i is None:
        vec = agent_positions[j] - np.array(target_pos)
        ro_i = np.linalg.norm(vec)
        print(f"[Drone{j+1}] 計算値: ro_i = {ro_i:.2f} m")
