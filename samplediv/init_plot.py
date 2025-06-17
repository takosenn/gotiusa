# init_plot.py
#初期描画？

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.lines import Line2D
from config import center, radius, xlim, ylim, num_agents

fig, ax = plt.subplots()
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.set_aspect("equal")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Example1")

point, = ax.plot([0], [radius], "ro", label="Target")
circle = Circle(center, radius, fill=False, linestyle='dashed', color='blue', label='軌道')
ax.add_patch(circle)

import numpy as np
agent_colors = plt.get_cmap('tab10').colors[:num_agents]

# ランダムな半径（target中心からの距離）
min_r = max(1, radius * 0.3)
max_r = radius * 1.5
radii = np.random.uniform(min_r, max_r, num_agents)
# ランダムな角度
angles = np.random.uniform(0, 2*np.pi, num_agents)
# 角度を昇順にソートし、その順でエージェント番号を割り当て
sort_idx = np.argsort(angles)
angles_sorted = angles[sort_idx]
radii_sorted = radii[sort_idx]  # 角度順に半径も並び替え

agent_positions = np.column_stack([
    center[0] + radii_sorted * np.cos(angles_sorted),
    center[1] + radii_sorted * np.sin(angles_sorted)
])

agent_dots = ax.scatter(agent_positions[:,0], agent_positions[:,1], c=agent_colors, label='Agents')

legend_elements = [Line2D([0], [0], marker='o', color='w', label=f'Agent {i+1}',
                          markerfacecolor=agent_colors[i], markersize=10)
                   for i in range(num_agents)]
ax.legend(handles=legend_elements, loc="center left", bbox_to_anchor=(1, 0.5))
