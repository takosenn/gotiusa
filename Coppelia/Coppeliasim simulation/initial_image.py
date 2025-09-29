# シミュレーションの下準備

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle
from parameter import center, xlim, ylim, radius, num_agents, radius_limit
from connect_Coppelia import Simulation

sim = Simulation()
sim.get_handles(num_agents)

def initial_image():
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
    circle = Circle(center, radius, fill=False, linestyle="dashed", color="blue")
    ax.add_patch(circle)

    # --- エージェントの初期角度を第i象限に配置（i=1:第1象限, i=2:第2象限, ...） ---
    target_positions = [0, 5, 0]
    sim.initial_settargetposition(target_positions)
    agent_positions = np.zeros((num_agents, 2))
    for i in range(num_agents):
        agent_positions[i] = [4 + np.sign(np.cos(np.pi * i)), 2 * i]
        sim.initial_setAgentpositions(
            i, [float(agent_positions[i][0]), float(agent_positions[i][1]), 2.0]
        )

    # 色分け用カラーマップ（tab10を利用）
    agent_colors = plt.get_cmap("tab10").colors[:num_agents]
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
    return fig, ax, point, agent_dots, agent_positions, agent_colors, sim
