# 2Dani_init
# 2Dアニメーションの初期化

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
from init_parameter import xlim, ylim, radius, num_agents, center, radius_limit

# --- 図と座標軸の初期化 ---
fig, ax = plt.subplots()  # 新しい図(fig)と座標軸(ax)を作成
ax.set_xlim(xlim)  # x軸の表示範囲を設定
ax.set_ylim(ylim)  # y軸の表示範囲を設定
ax.set_aspect("equal")  # x, y軸のスケールを等しくする（円が歪まないように）
ax.set_xlabel("x")  # x軸ラベル
ax.set_ylabel("y")  # y軸ラベル
ax.set_title("Example1")  # グラフタイトル

# --- 目標（ターゲット）の軌道を描画（初期位置のみプロット） ---
(point,) = ax.plot([0], [radius], "ro", label="Target")

# --- エージェントの初期配置 ---
# 各エージェントを円周上に等間隔で配置（第i象限に分布）
agent_positions = np.zeros(
    (num_agents, 2)
)  # エージェントの座標格納用配列 num_agents行2列のすべての要素が0の配列

for i in range(num_agents):
    theta = 2 * np.pi * i / num_agents  # 各エージェントの角度（等間隔）
    r = radius_limit  # 半径は一定（ランダム性なし）
    agent_positions[i, 0] = center[0] + r * np.cos(theta)  # x座標
    agent_positions[i, 1] = center[1] + r * np.sin(theta)  # y座標


# --- エージェントの描画 ---
agent_ids = list(range(1, num_agents + 1))  # 1~nのエージェント番号リスト
# 色分け用カラーマップ（tab10: 最大10色のカラーマップを利用）
# エージェントを色分けして描画
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
# 凡例をグラフの外側（左中央）に表示
ax.legend(handles=legend_elements, loc="center left", bbox_to_anchor=(1, 0.5))
