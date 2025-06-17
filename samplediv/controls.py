# controls.py
# 制御ロジックの実装

import numpy as np
from config import num_agents

def angular_distance_rad(angle1, angle2):
    diff = abs(angle1 - angle2)
    return min(diff, 2 * np.pi - diff)

# 隣接エージェントのインデックス取得
neighbor_indices = [((i-1)%num_agents, (i+1)%num_agents) for i in range(num_agents)]
