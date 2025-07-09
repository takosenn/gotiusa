
# neighborAgent_distance
# 隣接Agentの距離計算


from init_parameter import num_agents
from SecondD_ani_init import agent_positions
import numpy as np

agent_neighbors = []
for i in range(num_agents):
    left_idx = (i - 1) % num_agents
    right_idx = (i + 1) % num_agents
    left_pos = agent_positions[left_idx]
    right_pos = agent_positions[right_idx]
    agent_neighbors.append((left_pos, right_pos))
    
    dist_left = np.linalg.norm(agent_positions[i] - agent_positions[left_idx])      #Agent(i-1)との距離
    dist_right = np.linalg.norm(agent_positions[i] - agent_positions[right_idx])    #Agent(i+1)との距離
# agent_neighbors[i] = (左隣の座標, 右隣の座標)
