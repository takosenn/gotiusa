
import time
import numpy as np
import math
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

num_agents = 6
radius_limit = 6
center = (0 , 0)

class Simulation:
    def __init__(self):
        self.client = RemoteAPIClient()
        self.sim = self.client.getObject('sim')
        self.Agent_handles = []
        self.target_handle = -1
        self.visionSensor_handles = []
    
    def connect(self):
        print("Coppeliasimに接続中...")
        self.client.setStepping(True)
        print("接続しました")

    def start_simulation(self):
        self.sim.stopSimulation()
        time.sleep(1)
        self.sim.startSimulation()
        print("Simulation開始します")

    def stop_simulation(self):
        self.sim.stopSimulation()
        print("Simulationを停止します")
    
    def step_simulation(self):
        self.client.step()
    
    def get_handles(self):
        try:
            print("ハンドルの取得を開始します")
            self.target_handle = self.sim.getObject(f"/target")
            print("Targetのハンドルを取得しました")
            for i in range(num_agents):
                object_name = f"Quadcopter[{i+1}]"
                self.Agent_hansle = self.sim.getObject(f"/target[{i+1}]")
                self.Agent_handles.append(self.Agent_handle)
                print("Agentのハンドルを取得しました")
                self.visionSensor_handle = self.sim.getObject(f"/{object_name}/visionSensor")
                self.visionSensor_handles.append(self.visionSensor_handle)
                print("visionSensorのハンドルを取得しました")
            print("すべてのハンドルの取得に成功しました")
        except Exception as e:
            print("ハンドル取得に失敗:" , e.args)

    def get_all_drone_state(self):
        drone_states = []
        for i in range(num_agents):
            drone_handle = self.sim.getObject(f"/Quadcopter[{i+1}]")
            position = self.sim.getObjectPosition(drone_handle, -1)
            drone_states.append(position)
        return drone_states

    def set_agent_position(self, j , Agents_pos_3d):
        self.sim.setObjectPosition(self.Agent_handles[j], -1, Agents_pos_3d)
    
    def set_target_position(self , target_pos_3d):
        self.sim.setObjectPosition(self.target_handle , -1 , target_pos_3d)

    def get_visionSensor_distance(self , j):
        result = self.sim.handleVisionSensor(self.visionSensor_handles[j])
        result = self.sim.getVisionSensorDepth(self.visionSensor_handles[j], 1, [0, 0], [0, 0])
        if isinstance(result, tuple) and len(result) == 2:
            depth_bytes, resolution = result  # resolutionは解像度[256,256]を表す

            # bytes → float32配列に変換
            floatingNumbers = self.sim.unpackFloatTable(depth_bytes, 0, 0, 0)
            floatingNumbers = np.array(floatingNumbers)
        print(f"visionSensorの距離測定に成功しました: 距離 = {min(floatingNumbers):.3f} [m]")
        return min(floatingNumbers)
    
    def set_visionSensor_param(self , j):
        ro_i = self.get_visionsensor_distance(j)
        if ro_i > 4:  # 広い視野角（84.6度）
            self.sim.setObjectFloatParam(
                self.visionSensor_handles[j],
                self.sim.visionfloatparam_perspective_angle,
                math.radians(45),
            )
        else:  # 狭い視野角（30度）
            self.sim.setObjectFloatParam(
                self.visionSensor_handles[j],
                self.sim.visionfloatparam_perspective_angle,
                math.radians(45),
            )

    def coodinate_target(self , j):
        height, width = 256, 256
        fov_y = self.sim.getObjectFloatParam(
            self.visionSensor_handles[j], self.sim.visionfloatparam_perspective_angle
        )
        aspect = width / height
        fov_x = 2 * math.atan(math.tan(fov_y / 2) * aspect)  # 水平面の視野角
        depth_buffer = self.sim.getVisionSensorDepthBuffer(self.visionSensor_handles[j])
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
        sensor_matrix = self.sim.getObjectMatrix(self.visionSensor_handles[j], self.sim.handle_world)
        world_pos = self.sim.multiplyVector(sensor_matrix, local_pos)
        print(
            f"Agent{j+1} visionSensor 座標変換成功: 座標 =[{world_pos[0]:.2f}, {world_pos[1]:.2f}]"
        )
        return world_pos
    
    def visionSenor_orientation(self , j):
        world_pos = self.coodinate_target(j)
        dx = world_pos[0]
        dy = world_pos[1]
        Yaw = np.arctan2(dy, dx)  # グローバル座標系での角度
        print(f"Agent{j+1}のいるべき角度: {Yaw/np.pi}π")
        # pose = {dx , dy , 2 , 0 , 0 , Yaw , 1}
        self.sim.setObjectOrientation(self.Agent_handles[j], self.sim.handle_parent, [0, 0, Yaw])

        height, width = 256, 256
        depth_buffer = self.sim.getVisionSensorDepthBuffer(self.visionSensor_handles[j])
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

        current_orientation = self.sim.getObjectOrientation(
            self.Agent_handles[j], self.sim.handle_parent
        )
        #ずれの向きに応じてYawを微調整（例: 1度ずつ）
        delta_yaw = np.sign(dx)*math.radians(45*dx/256)
        new_yaw = delta_yaw + current_orientation[2]
        self.sim.setObjectOrientation(
            self.Agent_handles[j],
            self.sim.handle_parent,
            [0, 0, new_yaw],
        )