from patroll import Patroll
from Encircle import Siege
from connect_coppelia import Simulation
from parameter import Params
import numpy as np
import time
from csv_save import set_csv_header
from datetime import datetime

"""現実時間の日本時間"""
Japan_time = datetime.now()

"""CSVのヘッダーを設定"""
set_csv_header(Japan_time, "ro_i")
set_csv_header(Japan_time, "theta")
set_csv_header(Japan_time, "alpha_i")
set_csv_header(Japan_time, "alpha_i_minus")
set_csv_header(Japan_time, "omega_i")
set_csv_header(Japan_time, "eta")
set_csv_header(Japan_time, "e_i_1")
set_csv_header(Japan_time, "e_i_2")
set_csv_header(Japan_time, "fi")

class Main:
    def __init__(self , num_agents , frame_time , target_position , agent_positions):
        self.sim = Simulation()
        # Simulationのハンドルを取得してからAnimationに同じインスタンスを渡す
        self.sim.get_handles(num_agents)
        self.num_agents = num_agents
        self.frame_time = frame_time
        self.target_position = target_position
        self.agent_position = list(agent_positions)
        self.prev_target_position = np.copy(self.target_position)
        self.prev_agent_positions = np.copy(self.agent_position)
        self.distance = []
        for i in range(self.num_agents):
            distance = np.linalg.norm(np.array(self.agent_position[i]) - self.target_position)
            self.distance.append(distance)
        self.patroll = Patroll(num_agents , self.target_position , self.agent_position , self.distance)
        self.siege = Siege(num_agents , frame_time , self.target_position , self.agent_position , self.distance)


    def run(self):
        try:
            self.sim.connect()
            self.sim.start_simulation()
            self.sim.initial_settargetposition(self.target_position)
            self.sim.initial_setAgentpositions(self.agent_position)
            for i in range(Params["frames"]):
                print(f"現在のfor文を読んだ回数: {i}回目")
                current_time = i * self.frame_time
                print(f"現在の経過時間：{current_time}")
                if any(d <= Params["distance_threshold"] for d in self.distance):           #一つでも距離が10以下になったとき
                    self.prev_agent_positions = np.copy(self.agent_position)
                    self.agent_position , self.distance = self.siege.animate(i , Japan_time , current_time , self.agent_position , self.prev_agent_positions , self.prev_target_position , self.target_position)
                    for k in range(self.num_agents):
                        self.distance[k] = np.linalg.norm(np.array(self.agent_position[k]) - np.array(self.target_position))
                else:           #通常時巡回
                    self.distance , self.prev_agent_positions , self.agent_position = self.patroll.animate()
                self.prev_target_position = np.copy(self.target_position)
                self.target_position += np.array([-0.1, -0.1, 0], dtype=float)
                for j in range(self.num_agents):
                    self.sim.setAgentposition(j, self.agent_position)
                    self.sim.settargetposition(self.target_position.tolist())
                time.sleep(Params["frame_time"])
                self.sim.step_simulation()
        except KeyboardInterrupt:
            print("ctrl+Cが押されました。")
        finally:
            self.sim.stop_simulation()


controller = Main(
    num_agents = Params["num_agents"] ,
    frame_time = Params["frame_time"],
    target_position = Params["target_position"] ,
    agent_positions = Params["agent_position"]
)
controller.run()