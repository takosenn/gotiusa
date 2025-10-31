
import numpy as np

class Siege:
    def __init__(self, num_agents , frame_time , target_position , agent_positions, distance):
        self.num_agents = num_agents
        self.frame_time = frame_time
        self.target_position = target_position
        self.agent_positions = list(agent_positions)
        self.ro_i = list(distance)
        self.relative_coordinate = self.agent_positions - self.target_position

    def animate(self):
        for i in range(self.num_agents):
            i_plus = (i+1)%self.num_agents
            i_minus = (i-1)%self.num_agents
