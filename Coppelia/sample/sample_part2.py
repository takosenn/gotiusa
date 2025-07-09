# sample_part2.py
from sample_part1 import *

# --- 初期化 ---
fig, ax = plt.subplots()
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.set_aspect("equal")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Example1")

# 目標の軌道
(point,) = ax.plot([0], [radius], "ro", label="Target")

# --- エージェントの初期角度を第i象限に配置（i=1:第1象限, i=2:第2象限, ...） ---
agent_positions = np.zeros((num_agents, 2))
radius_limit = 6  # 配置半径（中心からの距離）

for i in range(num_agents):
    theta = 2 * np.pi * i / num_agents
    r = radius_limit  # ランダム性を排除し、一定の半径で配置
    agent_positions[i, 0] = center[0] + r * np.cos(theta)
    agent_positions[i, 1] = center[1] + r * np.sin(theta)

agent_ids = list(range(1, num_agents + 1))  # 1~nのエージェント番号
# 色分け用カラーマップ（tab10を利用）
agent_colors = plt.get_cmap("tab10")(np.linspace(0, 1, num_agents))
agent_dots = ax.scatter(
    agent_positions[:, 0], agent_positions[:, 1], c=agent_colors, label="Agents"
)
# --- エージェント番号と色の凡例を追加 ---
legend_elements = [
    Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        label=f"Agent {i+1}",
        markerfacecolor=agent_colors[i],
        markersize=10,
    )
    for i in range(num_agents)
]
ax.legend(handles=legend_elements, loc="center left", bbox_to_anchor=(1, 0.5))

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

for i in range(num_agents):
    left_idx = (i - 1) % num_agents
    right_idx = (i + 1) % num_agents
    dist_left = np.linalg.norm(agent_positions[i] - agent_positions[left_idx])
    dist_right = np.linalg.norm(agent_positions[i] - agent_positions[right_idx])
