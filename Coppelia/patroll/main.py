from test import Test
from connect_coppelia import Simulation
import numpy as np
import time

num_agents=4
class Main:
    def __init__(self):
        self.sim = Simulation()
        # Simulationのハンドルを取得してからAnimationに同じインスタンスを渡す

        self.sim.get_handles(num_agents)
        self.ani = Test(num_agents)
        self.ani.sim = self.sim
        self.initial_target_pos = [20, 20, 2]
        self.initial_agent_pos = []
        
        agent_position = (
            [5, 0, 2],
            [10, 5, 2],
            [5, 10, 2],
            [0, 5, 2],
            [3.3, 3.3, 2],
            [6.6, 6.6, 2],
        )
        self.initial_agent_pos = list(agent_position)

    def run(self):
        try:
            self.sim.connect()
            self.sim.start_simulation()
            self.sim.initial_settargetposition(self.initial_target_pos)
            self.sim.initial_setAgentpositions(self.initial_agent_pos)
            for i in range(1000):
                print(f"現在のfor文を読んだ回数: {i}回目")
                self.ani.animate()
                time.sleep(0.05)
                self.sim.step_simulation()
        except KeyboardInterrupt:
            print("ctrl+Cでシミュレーションが終了しました")
        finally:
            self.sim.stop_simulation()


controller = Main()
controller.run()