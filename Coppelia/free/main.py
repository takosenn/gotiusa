# これを実行するとシミュレーションスタート

from parameter import frames, frame_time , radius , radius_limit , initial_target_position , initial_agents_positions
from animation import Animation
from connect_Coppelia import Simulation
import time
import numpy as np


# import japanize_matplotlib      # type: ignore


class Main:
    def __init__(self):
        self.sim = Simulation()
        # Simulationのハンドルを取得してからAnimationに同じインスタンスを渡す
        from parameter import num_agents

        self.sim.get_handles(num_agents)
        self.ani = Animation()
        self.ani.sim = self.sim
        self.initial_target_pos = initial_target_position
        self.initial_agent_pos = []
        for i in range(num_agents):
            agent_pos = initial_agents_positions[i]
            self.initial_agent_pos.append(agent_pos)

    def run(self):
        try:
            self.sim.connect()
            self.sim.start_simulation()
            self.sim.initial_settargetposition(self.initial_target_pos)
            self.sim.initial_setAgentpositions(self.initial_agent_pos)
            for i in range(frames):
                print(f"現在のfor文を読んだ回数: {i}回目")
                self.ani.animate(i)
                time.sleep(frame_time)
                self.sim.step_simulation()
        except KeyboardInterrupt:
            print("ctrl+Cでシミュレーションが終了しました")
        finally:
            self.sim.stop_simulation()


controller = Main()
controller.run()
