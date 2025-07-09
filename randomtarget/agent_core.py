"""
agent_initializer.py
エージェントの初期配置・隣接情報の計算を担当。
"""

import numpy as np
from config import num_agents, radius, center

# --- エージェントの初期角度を等間隔で配置(0 <= alpha_1 < ... < alpha_6 < 2π) ---
angles = np.linspace(0, 2 * np.pi, num_agents, endpoint=False)  # 等間隔
agent_radii = np.full(num_agents, 6.0)  # 半径6で全エージェント同じ
agent_positions = np.column_stack(
    [center[0] + agent_radii * np.cos(angles), center[1] + agent_radii * np.sin(angles)]
)
agent_ids = list(range(1, num_agents + 1))  # 1~6のエージェント番号

# 各エージェントが隣接エージェント（前後の番号）の座標を知る
neighbor_indices = [
    ((i - 1) % num_agents, (i + 1) % num_agents) for i in range(num_agents)
]
agent_neighbors = []
for i in range(num_agents):
    left_idx = (i - 1) % num_agents
    right_idx = (i + 1) % num_agents
    left_pos = agent_positions[left_idx]
    right_pos = agent_positions[right_idx]
    agent_neighbors.append((left_pos, right_pos))
# agent_neighbors[i] = (左隣の座標, 右隣の座標)
