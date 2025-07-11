from parameter import num_agents
from Handle import sim
import numpy as np


def distance():
    for i in range(num_agents):
        object_name = f"Quadcopter[{i+1}]"
        visionSensor_handle = sim.getObject(f"/{object_name}/visionSensor")
        print(f"取得: {object_name}のvisionSensor")

        result, resolution = sim.getVisionSensorDepth(visionSensor_handle[i])
        depthBuffer, resolution = result
        depthArray = np.array(depthBuffer, dtype=np.float64)
        if len(resolution) == 2:
            depthArray = depthArray.reshape(resolution)
        nearClip = sim.getObjectFloatParam(
            visionSensor_handle, sim.visionfloatparam_near_clipping
        )
        farClip = sim.getObjectFloatParam(
            visionSensor_handle, sim.visionfloatparam_far_clipping
        )
        realDepth = nearClip + (farClip - nearClip) * depthArray
        valid_mask = realDepth < (farClip - 1e-4)
        if np.any(valid_mask):
            minDist = np.min(realDepth[valid_mask])
            if np.isfinite(minDist):
                ro_i = minDist
                print(f"[Drone{i+1}] VisionSensorで検知: ro_i = {ro_i:.2f} m")
            else:
                print(f"[Drone{i+1}] VisionSensor: 有効な物体なし")
        else:
            print(f"[Drone{i+1}] VisionSensor: 物体未検知")
            print(f"中心の距離: {ro_i:.3f} m")

        visionSensor_orientation = sim.getObjectOrientation(visionSensor_handle[i], -1)
        yaw_angle = visionSensor_orientation[2]
        vision_direction = np.array([np.cos(yaw_angle), np.sin(yaw_angle)])
        vec = vision_direction * ro_i
        print(
            f"[Drone{i+1}] VisionSensor値からvec計算: ro_i = {ro_i:.2f} m, 角度 = {np.degrees(yaw_angle):.1f}°"
        )
    return vec, ro_i
