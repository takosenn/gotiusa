
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time
from parameter import Params


class Simulation:
    def __init__(self):
        self.client = RemoteAPIClient()
        self.sim = self.client.require("sim")
        self.Drone_handles = []
        self.Agent_handles = []
        self.target_Drone_handle = self.sim.getObject("/Quadcopter[0]")
        self.target_handle = self.sim.getObject("/Quadcopter[0]/target")

    def connect(self):
        print("CoppeliaSimと接続中...")
        self.client.setStepping(True)  # 必要に応じて同期モードを有効にする
        print("接続に成功")

    def start_simulation(self):
        """シミュレーションを開始する"""
        self.sim.stopSimulation()
        time.sleep(1)  # 確実に停止するのを待つ
        self.sim.startSimulation()
        print("Simulationを開始")

    def stop_simulation(self):
        """シミュレーションを停止する"""
        self.sim.stopSimulation()
        print("Simulationを停止")

    def step_simulation(self):
        """シミュレーションを1ステップ進める（同期モード用）"""
        self.client.step()

    def get_handles(self):
        self.target_handle = self.sim.getObject("/Quadcopter[0]/target")
        self.target_Drone_handle = self.sim.getObject("/Quadcopter[0]")
        print("取得: Quadcopter[0] のtarget")
        # 各Agentの緑の球(target)のハンドル
        for i in range(Params["num_agents"]):
            object_name = f"Quadcopter[{i+1}]"
            Drone_handle = self.sim.getObject(f"/{object_name}")
            self.Drone_handles.append(Drone_handle)
            Agent_handle = self.sim.getObject(f"/{object_name}/target")
            self.Agent_handles.append(Agent_handle)
            print(f"取得: {object_name} のtarget")

    def change_handles(self , sorted_idx):
        for j in range(Params["num_agents"]):
            object_name = f"target[{sorted_idx[j]+1}]"
            Agent_handle = self.sim.getObject(f"/{object_name}")
            self.Agent_handles.append(Agent_handle)
            print(f"Agentハンドルの更新: Quadcopter[{j}]のハンドルを{object_name}")


    def initial_setAgentpositions(self, Agent_positions):
        for i in range(Params["num_agents"]):
            self.sim.setObjectPosition(self.Drone_handles[i], -1, Agent_positions[i])
            self.sim.setObjectPosition(self.Agent_handles[i], -1, Agent_positions[i])

    def initial_settargetposition(self, target_position):
        self.sim.setObjectPosition(self.target_Drone_handle, -1, target_position)
        self.sim.setObjectPosition(self.target_handle, -1, target_position)

    def setAgentposition(self, j, Agents_pos_3d):
        # Coppeliasim側でAgentの緑の球(target)の位置同期
        for j in range(Params["num_agents"]):
            self.sim.setObjectPosition(self.Agent_handles[j], -1, Agents_pos_3d[j])

    def settargetposition(self, target_pos_3d):
        # Coppeliasim側でtargetの緑の球(target)の位置同期
        self.sim.setObjectPosition(self.target_handle, -1, target_pos_3d)
