import numpy as np
import time
from connect_coppelia import Simulation


class Test:
    def __init__(self, num_agents):
        self.sim = Simulation()
        self.initial_target_position = [15, 15, 2]
        # keep initial_target_position as a plain list for API calls,
        # but use a numpy array for internal element-wise updates
        self.target_position = np.array(self.initial_target_position, dtype=float)
        self.frame = 10000
        self.agent_positions = []

        agent_position = (
            [5, 0, 2],
            [10, 5, 2],
            [5, 10, 2],
            [0, 5, 2],
            [3.3, 3.3, 2],
            [6.6, 6.6, 2],
        )
        self.agent_positions = list(agent_position)

        

    def animate(self):

        for i in range(4):
            # 右下
            if self.agent_positions[i][1] <= 0:
                if self.agent_positions[i][0] >= 10:
                    self.agent_positions[i][1] += 0.1
                else:
                    self.agent_positions[i][0] += 0.1
            elif self.agent_positions[i][1] >= 10:
                if self.agent_positions[i][0] <= 0:
                    self.agent_positions[i][1] -= 0.1
                else:
                    self.agent_positions[i][0] -= 0.1
            elif self.agent_positions[i][0] <= 0:
                if self.agent_positions[i][1] <= 0:
                    self.agent_positions[i][0] += 0.1
                else:
                    self.agent_positions[i][1] -= 0.1
            elif self.agent_positions[i][0] >= 10:
                if self.agent_positions[i][1] >= 10:
                    self.agent_positions[i][0] -= 0.1
                else:
                    self.agent_positions[i][1] += 0.1
            print(f"Agent {i} position: {self.agent_positions[i]}")
        # element-wise update using numpy array
        self.target_position += np.array([-0.1, -0.1, 0], dtype=float)
        print(self.target_position)

        # send updated positions to the simulation (convert numpy -> list)
        self.sim.setAgentposition(i, self.agent_positions)
        self.sim.settargetposition(self.target_position.tolist())

        self.sim.step_simulation()

