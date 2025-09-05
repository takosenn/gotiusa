
# ローカル座標系の値をグローバル座標系に変換する関数

import numpy as np
import math
from Handle import sim , visionSensor_handles

def coordinate_trans(theta_global, u):
    A = np.array(
        [
            [np.cos(theta_global), -np.sin(theta_global)],
            [np.sin(theta_global), np.cos(theta_global)],
        ]
    )
    u_vec_local = np.array([u[0], u[1]])
    u_vec = A @ u_vec_local
    return u_vec


def coordinate_target(j, ro_i):
    height, width = 256, 256
    fov_y = sim.getObjectFloatParam(
        visionSensor_handles[j], sim.visionfloatparam_perspective_angle
    )
    aspect = width / height
    fov_x = 2 * math.atan(math.tan(fov_y / 2) * aspect)  # 水平面の視野角
    depth_buffer = sim.getVisionSensorDepthBuffer(visionSensor_handles[j])
    depth_image = np.array(depth_buffer).reshape(height, width)
    ro_i = depth_image[height // 2, width // 2]  # 中央ピクセルの距離

    # 正規化座標 カメラの幅を基準にして-0.5から0.5の範囲に変換
    nx = (width / 2 / width) - 0.5
    ny = 0.5 - (height / 2 / height)

    # カメラ空間座標
    x_cam = ro_i * math.tan(fov_x / 2) * 2 * nx  # カメラに映る物体のx座標
    y_cam = ro_i * math.tan(fov_y / 2) * 2 * ny  # カメラに映る物体のy座標
    z_cam = ro_i  # カメラに映る物体のz座標（距離）

    # ワールド座標変換
    local_pos = [x_cam, y_cam, z_cam]
    sensor_matrix = sim.getObjectMatrix(visionSensor_handles[j], sim.handle_world)
    world_pos = sim.multiplyVector(sensor_matrix, local_pos)
    print(
        f"Agent{j+1} visionSensor 座標変換成功: 座標 =[{world_pos[0]:.2f}, {world_pos[1]:.2f}]"
    )
    return world_pos