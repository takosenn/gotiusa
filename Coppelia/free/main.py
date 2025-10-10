#これを実行するとシミュレーションスタート

from parameter import frames , frame_time 
from animation import Animation
from connect_Coppelia import Simulation
import time
import numpy as np

#import japanize_matplotlib      # type: ignore


class Main:
    def __init__(self):
        self.sim = Simulation()
        # Simulationのハンドルを取得してからAnimationに同じインスタンスを渡す
        from parameter import num_agents
        self.sim.get_handles(num_agents)
        self.ani = Animation()
        self.ani.sim = self.sim
        self.initial_target_pos = [0 , 5 , 2]
        self.initial_agent_pos = []
        for i in range(num_agents):
            agent_pos = [5*np.cos(i*np.pi/3),5+5*np.sin(i*np.pi/3),2]
            self.initial_agent_pos.append(agent_pos)

    def run(self):
        try:
            self.sim.connect()
            self.sim.start_simulation()
            self.sim.initial_settargetposition(self.initial_target_pos)
            self.sim.initial_setAgentpositions(self.initial_agent_pos)
            for i in range(10000):
                self.ani.animate(i)
                time.sleep(frame_time)
        except KeyboardInterrupt:
            print("ctrl+Cでシミュレーションが終了しました")
        finally:
            self.sim.stop_simulation()

controller = Main()
controller.run()