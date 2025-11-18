import numpy as np
from parameter import Params
from typing import Optional
from connect_coppelia import Simulation


class Patroll:
    def __init__(self, num_agents, target_position, agent_positions, distance):
        self.frame = 10000
        # remember how many agents we manage
        self.num_agents = num_agents
        self.target_position = target_position
        self.prev_target_position = np.copy(self.target_position)
        self.agent_positions = list(agent_positions)
        self.prev_agent_positions = np.copy(self.agent_positions)
        self.distance = list(distance)
        self.prev_distance = []

    def reorder(self, sorted_idx):
        """sorted_idx の順に Patroll の内部状態を並び替える"""
        # agent_positions
        self.agent_positions = [self.agent_positions[idx] for idx in sorted_idx]
        # prev_agent_positions: keep as numpy array
        try:
            self.prev_agent_positions = np.array(
                [self.prev_agent_positions[idx] for idx in sorted_idx]
            )
        except Exception:
            self.prev_agent_positions = np.array(
                [self.prev_agent_positions[idx].copy() for idx in sorted_idx]
            )
        # distance lists
        self.distance = [self.distance[idx] for idx in sorted_idx]
        # prev_distance may be a list or numpy array; check length safely
        try:
            has_prev = len(self.prev_distance) > 0
        except Exception:
            has_prev = False
        if has_prev:
            self.prev_distance = [self.prev_distance[idx] for idx in sorted_idx]

    def animate(self):

        self.prev_agent_positions = np.copy(self.agent_positions)
        for i in range(4):
            # 右下
            if self.agent_positions[i][1] <= 0:
                if self.agent_positions[i][0] >= 10:
                    self.agent_positions[i][1] += Params["patroll_direction"]
                else:
                    self.agent_positions[i][0] += Params["patroll_direction"]
            # 左上
            elif self.agent_positions[i][1] >= 10:
                if self.agent_positions[i][0] <= 0:
                    self.agent_positions[i][1] -= Params["patroll_direction"]
                else:
                    self.agent_positions[i][0] -= Params["patroll_direction"]
            # 左下
            elif self.agent_positions[i][0] <= 0:
                if self.agent_positions[i][1] <= 0:
                    self.agent_positions[i][0] += Params["patroll_direction"]
                else:
                    self.agent_positions[i][1] -= Params["patroll_direction"]
            # 右上
            elif self.agent_positions[i][0] >= 10:
                if self.agent_positions[i][1] >= 10:
                    self.agent_positions[i][0] -= Params["patroll_direction"]
                else:
                    self.agent_positions[i][1] += Params["patroll_direction"]
        for i in range(4, 6):
            # 左下
            if self.agent_positions[i][0] <= 3.3:
                if self.agent_positions[i][1] <= 6.6:
                    self.agent_positions[i][1] += Params["patroll_direction"]
                else:
                    self.agent_positions[i][0] += Params["patroll_direction"]
            # 右上
            elif self.agent_positions[i][1] >= 6.6:
                if self.agent_positions[i][0] >= 6.6:
                    self.agent_positions[i][1] -= Params["patroll_direction"]
                else:
                    self.agent_positions[i][0] += Params["patroll_direction"]
            # 左上
            elif self.agent_positions[i][0] >= 6.6:
                if self.agent_positions[i][1] <= 3.3:
                    self.agent_positions[i][0] -= Params["patroll_direction"]
                else:
                    self.agent_positions[i][1] -= Params["patroll_direction"]
            # 右下
            elif self.agent_positions[i][1] <= 3.3:
                if self.agent_positions[i][0] <= 3.3:
                    self.agent_positions[i][1] += Params["patroll_direction"]
                else:
                    self.agent_positions[i][0] -= Params["patroll_direction"]

        # element-wise update using numpy array

        self.prev_distance = np.copy(self.distance)
        for i in range(self.num_agents):
            self.distance[i] = np.linalg.norm(
                np.array(self.agent_positions[i]) - np.array(self.target_position)
            )
        # send updated positions to the simulation (convert numpy -> list)

        return self.distance, self.prev_agent_positions, self.agent_positions
