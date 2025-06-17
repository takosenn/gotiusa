# animation_data.py
from config import num_agents
from typing import List

ro_i_history: List[list] = [[] for _ in range(num_agents)]
eta_i_history: List[list] = [[] for _ in range(num_agents)]
omega_i_history: List[list] = [[] for _ in range(num_agents)]
alpha_i_history: List[list] = [[] for _ in range(num_agents)]
u_vec_history: List[list] = [[] for _ in range(num_agents)]
a_vec_history: List[list] = [[] for _ in range(num_agents)]


def init(point, agent_dots, agent_positions, radius):
    point.set_data([0], [radius])
    agent_dots.set_offsets(agent_positions)
    return point, agent_dots
