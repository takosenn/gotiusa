from patroll import Patroll
from siege import Siege
from connect_coppelia import Simulation
from parameter import Params
import numpy as np
import time

class Main:
    def __init__(self , num_agents , frame_time , target_position , agent_positions):
        self.sim = Simulation()
        # Simulationのハンドルを取得してからAnimationに同じインスタンスを渡す
        self.sim.get_handles(num_agents)
        self.num_agents = num_agents
        self.frame_time = frame_time
        self.target_position = target_position
        self.agent_position = list(agent_positions)
        self.distance = []
        for i in range(self.num_agents):
            distance = np.linalg.norm(np.array(self.agent_position[i]) - self.target_position)
            self.distance.append(distance)
        self.patroll = Patroll(num_agents , self.target_position , self.agent_position , self.distance , sim=self.sim)
        self.siege = Siege(num_agents , frame_time , self.target_position , self.agent_position , self.distance)
        

    def run(self):
        try:
            self.sim.connect()
            self.sim.start_simulation()
            self.sim.initial_settargetposition(self.target_position)
            self.sim.initial_setAgentpositions(self.agent_position)
            for i in range(1000):
                j = i % self.num_agents
                print(f"現在のfor文を読んだ回数: {i}回目")
                current_time = i * self.frame_time
                print(f"現在の経過時間：{current_time}")
                if any(d <= Params["distance_threshold"] for d in self.distance):           #一つでも距離が10以下になったとき
                    None
                else:           #通常時巡回
                    self.distance , self.agent_position , self.target_position = self.patroll.animate()
                
                time.sleep(0.05)
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