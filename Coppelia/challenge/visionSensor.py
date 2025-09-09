from Handle import sim, visionSensor_handles, Agent_handles, drone_handles
from parameter import measurable_distance
from DataStrage import ro_i_integral
import math
import numpy as np


# 距離測定
def distance(j):
    result = sim.handleVisionSensor(visionSensor_handles[j])
    result = sim.getVisionSensorDepth(visionSensor_handles[j], 1, [0, 0], [0, 0])
    if isinstance(result, tuple) and len(result) == 2:
        depth_bytes, resolution = result  # resolutionは解像度[256,256]を表す

        # bytes → float32配列に変換
        floatingNumbers = sim.unpackFloatTable(depth_bytes, 0, 0, 0)
        floatingNumbers = np.array(floatingNumbers)
        filtered = floatingNumbers[
            (floatingNumbers > 0.1) & (floatingNumbers < measurable_distance)
        ]
        # print(filtered)
        ro_i = min(floatingNumbers)
        if not hasattr(distance, "prev_ro_i"):
            distance.prev_ro_i = ro_i
        # ro_iが前回値+0.5より大きい場合にYawを90度回転
        #if ro_i > distance.prev_ro_i + 0.5:
        #    # 現在のYawを取得
        #    current_orientation = sim.getObjectOrientation(
        #        Agent_handles[j], sim.handle_parent
        #    )
        #    new_yaw = current_orientation[2] + math.radians(90)
        #    sim.setObjectOrientation(
        #        Agent_handles[j],
        #        sim.handle_parent,
        #        [current_orientation[0], current_orientation[1], new_yaw],
        #    )
        #    print(f"Agent{j+1} Yawを90度回転させました")
        # ro_i = min(visionSenosr_distance)  # 画面内の最短距離[m] カメラから見た物体までの距離
        
        if ro_i > 4:  # 広い視野角（84.6度）
            sim.setObjectFloatParam(
                visionSensor_handles[j],
                sim.visionfloatparam_perspective_angle,
                math.radians(45),
            )
        else:  # 狭い視野角（30度）
            sim.setObjectFloatParam(
                visionSensor_handles[j],
                sim.visionfloatparam_perspective_angle,
                math.radians(45),
            )
        sim.setObjectFloatParam(visionSensor_handles[j] , sim.visionfloatparam_near_clipping, 0.1)
        sim.setObjectFloatParam(visionSensor_handles[j] , sim.visionfloatparam_far_clipping, ro_i + 0.5)
        print(f"Agent{j+1} visionSensor 測定成功: 距離 = {ro_i:.3f} [m]")
        distance.prev_ro_i = ro_i.copy()
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
    center_pixcel_distance = depth_image[height // 2, width // 2]  # 中央ピクセルの距離

    # 正規化座標 カメラの幅を基準にして-0.5から0.5の範囲に変換
    nx = (width / 2 / width) - 0.5
    ny = 0.5 - (height / 2 / height)

    # カメラ空間座標
    x_cam = (
        center_pixcel_distance * math.tan(fov_x / 2) * 2 * nx
    )  # カメラに映る物体のx座標
    y_cam = (
        center_pixcel_distance * math.tan(fov_y / 2) * 2 * ny
    )  # カメラに映る物体のy座標
    z_cam = center_pixcel_distance  # カメラに映る物体のz座標（距離）

    # ワールド座標変換
    local_pos = [x_cam, y_cam, z_cam]
    sensor_matrix = sim.getObjectMatrix(visionSensor_handles[j], sim.handle_world)
    world_pos = sim.multiplyVector(sensor_matrix, local_pos)
    print(
        f"Agent{j+1} visionSensor 座標変換成功: 座標 =[{world_pos[0]:.2f}, {world_pos[1]:.2f}]"
    )
    return world_pos

def to_native(x):
    if isinstance(x, (np.int64, np.int32)):
        return int(x)
    elif isinstance(x, (np.float64, np.float32)):
        return float(x)
    return x


def sensor_orientation(j, world_pos):
    dx = world_pos[0]
    dy = world_pos[1]
    Yaw = np.arctan2(dy, dx)  # グローバル座標系での角度
    print(f"Agent{j+1}のいるべき角度: {Yaw/np.pi}π")
    # pose = {dx , dy , 2 , 0 , 0 , Yaw , 1}
    sim.setObjectOrientation(Agent_handles[j], sim.handle_parent, [0, 0, Yaw])

    height, width = 256, 256
    depth_buffer = sim.getVisionSensorDepthBuffer(visionSensor_handles[j])
    depth_image = np.array(depth_buffer).reshape(height, width)

    # 最小値のインデックス（対象物の位置）を取得
    min_idx = np.argmin(depth_image)
    min_y, min_x = np.unravel_index(min_idx, (height, width))

    # 画像中央との差分
    center_x, center_y = width // 2, height // 2
    dx = min_x - center_x   #センサーの中心と物体との距離ピクセル
    #rotation_angle = 30 / width * dx

    #sim.setObjectOrientation(Agent_handles[j],sim.handle_parent,[0, 0, rotation_angle])
    # ずれが大きい場合Yawを調整
    if dx > 10 or dx < -10:  # 10ピクセル以上ずれていたら
        current_orientation = sim.getObjectOrientation(
            Agent_handles[j], sim.handle_parent
        )
        #ずれの向きに応じてYawを微調整（例: 1度ずつ）
        delta_yaw = np.sign(dx)*math.radians(45*dx/256)
        new_yaw = delta_yaw + current_orientation[2]
        sim.setObjectOrientation(
            Agent_handles[j],
            sim.handle_parent,
            [0, 0, new_yaw],
        )