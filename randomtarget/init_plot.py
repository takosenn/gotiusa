"""
plot_setup.py
matplotlibによる描画領域・凡例・UI部品の初期化を担当。
"""

import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import Circle
from matplotlib.lines import Line2D
from matplotlib.widgets import Button
from config import xlim, ylim, num_agents, radius

matplotlib.rcParams["font.family"] = "MS Gothic"

# --- 初期化 ---
fig, ax = plt.subplots()
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.set_aspect("equal")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Example1")

(point,) = ax.plot([0], [radius], "ro", label="Target")

agent_colors = plt.get_cmap("tab10").colors[:num_agents]

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
