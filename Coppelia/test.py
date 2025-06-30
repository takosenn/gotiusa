import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
import matplotlib
from matplotlib.widgets import Button
from matplotlib.lines import Line2D
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

matplotlib.rcParams["font.family"] = "MS Gothic"  # Windows標準の日本語フォントを指定

# --- パラメータ設定（論文 Example1 Fig.3 準拠） ---
center = (0, 0)
radius = 20  # targetの軌道半径
frames = 10000
xlim = (-30, 30)  # x軸の限界
ylim = (-30, 30)  # y軸の限界
R = 8  # targetとAgentの理想の距離
num_agents = 6  # agentの数6
d_i = 2*np.pi / num_agents  # Agentiとその隣接Agenti+-の理想角度
frame_time = 0.05  # interval=50msの場合    アニメーション全体の速度を調整
fps = 1 / frame_time
omega_target = 0.12 / fps  # targetの角速度0.12
Omega = 2 / fps  # Ω=2

# --- エージェントの初期角度を昇順で配置（0 <= alpha_1 < ... < alpha_6 < 2π） ---
angles = np.random.dirichlet(np.ones(num_agents)) * (2 * np.pi)
angles = np.sort(angles)  # 昇順（角距離条件は維持）

# --- エージェントの初期角度を昇順で配置（0 <= alpha_1 < ... < alpha_6 < 2π） ---
angles = np.random.dirichlet(np.ones(num_agents)) * (2 * np.pi)
angles = np.sort(angles)  # 昇順（角距離条件は維持）

# すべてのAgentの初期角距離の和が2πになるように、円周上に配置
agent_radii = np.random.uniform(
    radius - 2, radius + 2, num_agents
)  # 半径はtarget近傍でランダム
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

for i in range(num_agents):
    left_idx = (i - 1) % num_agents
    right_idx = (i + 1) % num_agents
    dist_left = np.linalg.norm(agent_positions[i] - agent_positions[left_idx])
    dist_right = np.linalg.norm(agent_positions[i] - agent_positions[right_idx])

# --- targetのランダムウォーク用初期化 ---
target_pos = np.array([0.0, 0.0])  # 初期位置（円運動の初期値と同じ）
target_velocity = np.zeros(2)  # 初期速度

# ランダムウォークのパラメータ
random_walk_sigma = 0.5  # 1フレームごとの速度変化の標準偏差
max_speed = 2.0  # targetの最大速度








# CoppeliaSimに接続
client = RemoteAPIClient()
sim = client.require('sim')

# ドローンの数
num_drones = 7

# ドローンのハンドルを取得して移動
for i in range(num_drones):
    object_name = f'Quadcopter[{i}]'

    try:
        drone_handle = sim.getObject(f'/{object_name}')
        print(f"'{object_name}' を取得しました")

        # 現在位置を取得
        start_pos = sim.getObjectPosition(drone_handle, -1)

        # Y軸方向に1メートル移動
        target_pos = [start_pos[0], start_pos[1] + 4.0, start_pos[2]]

        # 位置を設定（瞬間移動）
        sim.setObjectPosition(drone_handle, -1, target_pos)
        print(f"'{object_name}' を移動しました -> {target_pos}")

    except Exception as e:
        print(f"オブジェクト '{object_name}' の取得に失敗しました: {e}")
