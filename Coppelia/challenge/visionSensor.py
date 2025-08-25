from Handle import sim, visionSensor_handles, Agent_handles, target_handle
import math
import numpy as np


def get_drone_role(handle):
    data = sim.readCustomDataBlock(handle, "drone_role")
    if data is not None:
        return data  # 文字列に変換
    return None


# 距離測定
def distance(j):
    result = sim.handleVisionSensor(visionSensor_handles[j])
    result = sim.getVisionSensorDepth(visionSensor_handles[j], 1, [0, 0], [0, 0])
    if isinstance(result, tuple) and len(result) == 2:
        depth_bytes, resolution = result  # resolutionは解像度[256,256]を表す

        # bytes → float32配列に変換
        floatingNumbers = sim.unpackFloatTable(depth_bytes, 0, 0, 0)
        ro_i = min(floatingNumbers)  # 画面内の最短距離[m]
        if ro_i > 4:  # 広い視野角（84.6度）
            sim.setObjectFloatParam(
                visionSensor_handles[j],
                sim.visionfloatparam_perspective_angle,
                math.radians(40),
            )
        else:  # 狭い視野角（30度）
            sim.setObjectFloatParam(
                visionSensor_handles[j],
                sim.visionfloatparam_perspective_angle,
                math.radians(30),
            )
        print(f"Agent{j+1} visionSensor 測定成功: 距離 = {ro_i:.3f} [m]")

        role = sim.readCustomDataBlock(visionSensor_handles[j], "drone_role")

        if role == "target":
            print("これはターゲットです")
        elif role == "Agent":
            print("これはAgentです")
        else:
            print("識別情報なし")

    return ro_i


# カメラ座標系からワールド座標系への変換 targetを中心とした座標系から見たAgentの座標
def coodinate_target(j, ro_i):
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
    dx = world_pos[0]
    dy = world_pos[1]
    Yaw = np.arctan2(dy, dx)  # グローバル座標系での角度
    # pose = {dx , dy , 2 , 0 , 0 , Yaw , 1}
    sim.setObjectOrientation(Agent_handles[j], sim.handle_parent, [0, 0, Yaw])

    return world_pos
