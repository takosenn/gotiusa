import numpy as np
import time
from typing import Optional
from connect_coppelia import Simulation

class Test:
    def __init__(self, num_agents, sim: Optional[Simulation] = None):
        # allow caller to inject Simulation instance; otherwise create one
        self.sim = sim if sim is not None else Simulation()
        self.initial_target_position = [20, 20, 2]
        # keep initial_target_position as a plain list for API calls,
        # but use a numpy array for internal element-wise updates
        self.target_position = np.array(self.initial_target_position, dtype=float)
        self.frame = 10000
        self.agent_positions = []
        # remember how many agents we manage
        self.num_agents = num_agents

        agent_position = (
            [5, 0, 2],
            [10, 5, 2],
            [5, 10, 2],
            [0, 5, 2],
            [3.3, 6.6, 2],
            [6.6, 3.3, 2],
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
            #左上
            elif self.agent_positions[i][1] >= 10:
                if self.agent_positions[i][0] <= 0:
                    self.agent_positions[i][1] -= 0.1
                else:
                    self.agent_positions[i][0] -= 0.1
            #左下
            elif self.agent_positions[i][0] <= 0:
                if self.agent_positions[i][1] <= 0:
                    self.agent_positions[i][0] += 0.1
                else:
                    self.agent_positions[i][1] -= 0.1
            #右上
            elif self.agent_positions[i][0] >= 10:
                if self.agent_positions[i][1] >= 10:
                    self.agent_positions[i][0] -= 0.1
                else:
                    self.agent_positions[i][1] += 0.1
        for i in range(2):
            j = i + 4
            #左下
            if self.agent_positions[j][0] <= 3.3:
                if self.agent_positions[j][1] <= 6.6:
                    self.agent_positions[j][1] += 0.1
                else:
                    self.agent_positions[j][0] += 0.1
            #右上
            elif self.agent_positions[j][1] >= 6.6:
                if self.agent_positions[j][0] >= 6.6:
                    self.agent_positions[j][1] -= 0.1
                else:
                    self.agent_positions[j][0] += 0.1
            #左上
            elif self.agent_positions[j][0] >= 6.6:
                if self.agent_positions[j][1] <= 3.3:
                    self.agent_positions[j][0] -= 0.1
                else:
                    self.agent_positions[j][1] -= 0.1
            #右下
            elif self.agent_positions[j][1] <= 3.3:
                if self.agent_positions[j][0] <= 3.3:
                    self.agent_positions[j][1] += 0.1
                else:
                    self.agent_positions[j][0] -= 0.1

        # element-wise update using numpy array
        self.target_position += np.array([-0.1, -0.1, 0], dtype=float)

        # send updated positions to the simulation (convert numpy -> list)
        for i in range(self.num_agents):
            self.sim.setAgentposition(i, self.agent_positions)
        self.sim.settargetposition(self.target_position.tolist())

        self.sim.step_simulation()