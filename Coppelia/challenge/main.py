# targetとAgentが合体

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib
from matplotlib.widgets import Button
from matplotlib.lines import Line2D
from parameter import (
    num_agents,
    center,
    radius,
    frames,
    xlim,
    ylim,
    R,
    d_i,
    frame_time,
    fps,
    Omega,
    random_walk_sigma,
    max_speed,
    target_pos,
    target_velocity,
)
from Handle import Agent_handles, target_handle, sim, visionSensor_handle
from DataStrage import (
    ro_i_history,
    eta_i_history,
    omega_i_history,
    alpha_i_history,
    u_vec_history,
    e_i_1_integral,
    e_i_2_integral,
)
from calculation import calculate_u

matplotlib.rcParams["font.family"] = "MS Gothic"  # Windows標準の日本語フォントを指定

# シミュレーション開始
if sim.getSimulationState() == sim.simulation_stopped:
    sim.startSimulation()
    print("Simulation started")

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
        vec = agent_positions[j] - np.array([x, y])
        ro_i = np.linalg.norm(vec)
        # ローカル座標系の定義: x軸=target方向, y軸=その直交方向

        e_r = vec / ro_i  # target方向の単位ベクトル（ローカルx軸）
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
        A = np.array(
            [
                [np.cos(theta_global), -np.sin(theta_global)],
                [np.sin(theta_global), np.cos(theta_global)],
            ]
        )
        u_vec_local = np.array([u[0], u[1]])
        u_vec = A @ u_vec_local
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
        # omega_i, omega_i_plus, omega_i_minusを[rad/sec]に変換
        omega_i_sec = omega_i_local * fps
        # u[0], u[1], u_vecを[m/sec]に変換
        u_vec_sec = u_vec * fps
        ro_i_history[j].append(ro_i)
        eta_i_history[j].append(eta)
        omega_i_history[j].append(omega_i_sec)  # [rad/sec]で保存
        alpha_i_history[j].append(alpha_i_local)  # [rad]で保存
        u_vec_history[j].append(u_vec_sec.copy())

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


ani = FuncAnimation(
    fig, animate, frames=frames, init_func=init, blit=True, interval=frame_time * 1000
)


# --- 再生/停止ボタンのみ ---
class AnimationControl:
    def __init__(self, anim):
        self.anim = anim
        self.running = True

    def toggle(self, event):
        if self.running:
            self.anim.event_source.stop()
        else:
            self.anim.event_source.start()
        self.running = not self.running


button_ax = plt.axes((0.85, 0.05, 0.1, 0.075))
button = Button(button_ax, "再生/停止")
control = AnimationControl(ani)
button.on_clicked(control.toggle)

plt.show()

sim.stopSimulation()
