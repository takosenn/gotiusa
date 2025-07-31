import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from coordinate_transformation import coordinate_trans
from parameter import (
    center,
    xlim,
    ylim,
    radius,
    max_speed,
    random_walk_sigma,
    frame_time,
    R,
    num_agents,
    d_i,
    target_pos,
    target_velocity,
    radius_limit,
)
from calculation import calculate_u
from Handle import (
    Agent_handles,
    target_handle,
    sim,
    drone_handles,
    visionSensor_handles,
)
from DataStrage import e_i_1_integral, e_i_2_integral
from visionSensor import (
    distance,
    coodinate_target,
    sensor_orientation,
)  # , orientation_to_target
import math

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

for i in range(num_agents):
    theta = 2 * np.pi * i / num_agents

    r = radius_limit  # ランダム性を排除し、一定の半径で配置
    agent_positions[i, 0] = center[0] + r * np.cos(theta)
    agent_positions[i, 1] = center[1] + r * np.sin(theta)
    #sim.setObjectOrientation(visionSensor_handles[i],  [0 , np.pi*2/(i+1) , 0] , sim.handle_world )


# 色分け用カラーマップ（tab10を利用）
cmap = plt.get_cmap("tab10")
agent_colors = [cmap(i) for i in range(num_agents)]
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

# --- アニメーション関数 ---

def init():
    point.set_data([0], [radius])
    agent_dots.set_offsets(agent_positions)
    return point, agent_dots

def animate(i):
    global target_pos, target_velocity
    # targetのランダムウォーク
    # 速度にランダムな変化を加える。一瞬で枠外に飛び出さないように
    target_velocity += np.random.normal(0, random_walk_sigma, size=2)
    # 最大速度制限
    speed = np.linalg.norm(target_velocity)
    if speed > max_speed:
        target_velocity = target_velocity / speed * max_speed

    # 位置を更新
    target_pos += target_velocity * frame_time
    x, y = target_pos
    point.set_data([x], [y])
    agent_dots.set_offsets(agent_positions)

    if not hasattr(animate, "prev_agent_pos"):
        animate.prev_agent_pos = agent_positions.copy()
    if not hasattr(animate, "prev_target_pos"):
        animate.prev_target_pos = np.array([x, y])

    for j in range(num_agents):
        ro_i = distance(j)
        world_pos = np.round(coodinate_target(j,ro_i),2)
        e_r = (world_pos[0]/math.sqrt(world_pos[0]**2 + world_pos[1]**2),world_pos[1]/math.sqrt(world_pos[0]**2 + world_pos[1]**2))
        # ローカル座標系の定義: x軸=target方向, y軸=その直交方向
        #e_r = vec / ro_i  # target方向の単位ベクトル（ローカルx軸）
        e_theta = np.array([-e_r[1], e_r[0]])  # ローカルy軸
        # ローカル座標系でtargetや隣接エージェントの情報を取得
        # targetの相対速度（ローカル）
        agent_velocity = (agent_positions[j] - animate.prev_agent_pos[j]) / frame_time
        relative_velocity = agent_velocity - target_velocity
        relative_velocity_local = np.array(
            [np.dot(relative_velocity, e_r), np.dot(relative_velocity, e_theta)]
        )
        # 隣接エージェントのローカル角度
        idx_plus = (j + 1) % num_agents
        idx_minus = (j - 1) % num_agents
        vec_plus = agent_positions[idx_plus] - agent_positions[j]
        vec_minus = agent_positions[idx_minus] - agent_positions[j]
        theta_plus_local = np.arctan2(np.dot(vec_plus, e_theta), np.dot(vec_plus, e_r))
        theta_minus_local = np.arctan2(
            np.dot(vec_minus, e_theta), np.dot(vec_minus, e_r)
        )
        theta_now_local = 0.0  # 自分自身から見たtarget方向は常に0
        # ローカル角速度
        if not hasattr(animate, "prev_theta_local"):
            animate.prev_theta_local = np.zeros(num_agents)
        omega_i_local = theta_now_local - animate.prev_theta_local[j]
        omega_i_local = (omega_i_local + np.pi) % (2 * np.pi) - np.pi
        animate.prev_theta_local[j] = theta_now_local
        # 隣接エージェントのローカル角速度
        if not hasattr(animate, "prev_theta_plus_local"):
            animate.prev_theta_plus_local = np.zeros(num_agents)
        if not hasattr(animate, "prev_theta_minus_local"):
            animate.prev_theta_minus_local = np.zeros(num_agents)
        omega_i_plus_local = theta_plus_local - animate.prev_theta_plus_local[j]
        omega_i_plus_local = (omega_i_plus_local + np.pi) % (2 * np.pi) - np.pi
        omega_i_minus_local = theta_minus_local - animate.prev_theta_minus_local[j]
        omega_i_minus_local = (omega_i_minus_local + np.pi) % (2 * np.pi) - np.pi
        animate.prev_theta_plus_local[j] = theta_plus_local
        animate.prev_theta_minus_local[j] = theta_minus_local
        # ローカル角距離
        alpha_i_local = abs(theta_plus_local - theta_now_local)
        alpha_i_minus_local = abs(theta_minus_local - theta_now_local)
        # --- 制御プロトコルu_iの計算（ローカル座標系） ---
        eta = relative_velocity_local[0]
        eta_norm = abs(eta)
        u = calculate_u(
            d_i,
            ro_i,
            omega_i_local,
            omega_i_plus_local,
            omega_i_minus_local,
            alpha_i_local,
            alpha_i_minus_local,
            eta_norm,
            e_i_1_integral,
            e_i_2_integral,
            j,
            i,
        )

        # --- ローカル→グローバル変換 ---
        theta_global = np.arctan2(e_r[1], e_r[0])
        u_vec = coordinate_trans(theta_global, u)

        sensor_orientation(j,world_pos)
        # 位置を仮更新
        new_pos = agent_positions[j] + u_vec * frame_time
        # targetとの距離を計算
        dist_to_target = np.linalg.norm(new_pos - target_pos)
        if dist_to_target >= R:
            agent_positions[j] = new_pos
        else:
            # R未満なら、targetから距離Rの位置に補正
            direction = (new_pos - target_pos) / np.linalg.norm(new_pos - target_pos)
            agent_positions[j] = target_pos + direction * R

    animate.prev_agent_pos = agent_positions.copy()
    animate.prev_target_pos = np.array([x, y])

    # Coppeliasim側でAgentの緑の球(target)の位置同期
    for j in range(num_agents):
        Agents_pos_3d = [agent_positions[j][0], agent_positions[j][1], 2.0]
        sim.setObjectPosition(Agent_handles[j], -1, Agents_pos_3d)
    # Coppeliasim側でtargetの緑の球(target)の位置同期
    target_pos_3d = [target_pos[0], target_pos[1], 2.0]
    sim.setObjectPosition(target_handle, -1, target_pos_3d)
    return point, agent_dots
