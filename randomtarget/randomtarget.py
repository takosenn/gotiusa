# targetとAgentが合体

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
import matplotlib
from matplotlib.widgets import Button
from matplotlib.lines import Line2D

matplotlib.rcParams["font.family"] = "MS Gothic"  # Windows標準の日本語フォントを指定

# --- パラメータ設定（論文 Example1 Fig.3 準拠） ---
center = (0, 0)
radius = 20  # targetの軌道半径
frames = 10000
xlim = (-30, 30)  # x軸の限界
ylim = (-30, 30)  # y軸の限界
R = 8  # targetとAgentの理想の距離
d_i = np.pi / 3  # Agentiとその隣接Agenti+-の理想角度
frame_time = 0.05  # interval=50msの場合    アニメーション全体の速度を調整
fps = 1 / frame_time
omega_target = 0.12 / fps  # targetの角速度0.12
Omega = 2 / fps  # Ω=2
num_agents = 6  # agentの数6

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
# circle = Circle(
#     center, radius, fill=False, linestyle="dashed", color="blue", label="軌道"
# )
# ax.add_patch(circle)

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
# ro_i（targetと各Agentの距離）表示用テキスト（グラフ外右側に配置）
roi_text = ax.text(
    0.05,
    0.10,
    "",
    transform=ax.transAxes,
    ha="left",
    va="center",
    fontsize=8,
    color="black",
)

# --- targetのランダムウォーク用初期化 ---
target_pos = np.array([0.0, 0.0])  # 初期位置（円運動の初期値と同じ）
target_velocity = np.zeros(2)  # 初期速度

# ランダムウォークのパラメータ
random_walk_sigma = 0.5  # 1フレームごとの速度変化の標準偏差
max_speed = 2.0  # targetの最大速度


def init():
    point.set_data([0], [radius])
    agent_dots.set_offsets(agent_positions)
    roi_text.set_text("")
    return point, agent_dots, roi_text


def angular_distance_rad(angle1, angle2):
    diff = abs(angle1 - angle2)
    return min(diff, 2 * np.pi - diff)


# --- グラフ用データ保存リスト ---
ro_i_history: list = [[] for _ in range(num_agents)]
eta_i_history: list = [[] for _ in range(num_agents)]
omega_i_history: list = [[] for _ in range(num_agents)]
alpha_i_history: list = [[] for _ in range(num_agents)]
u_vec_history: list = [[] for _ in range(num_agents)]
a_vec_history: list = [[] for _ in range(num_agents)]
relative_velocity_history: list = [[] for _ in range(num_agents)]
# e_i_1, e_i_2の時間積分値（各エージェントごと）
e_i_1_integral = [0.0 for _ in range(num_agents)]
e_i_2_integral = [0.0 for _ in range(num_agents)]


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
    # 色分けを毎フレーム反映
    agent_dots.set_color(agent_colors)

    if not hasattr(animate, "prev_agent_pos"):
        animate.prev_agent_pos = agent_positions.copy()
    if not hasattr(animate, "prev_target_pos"):
        animate.prev_target_pos = np.array([x, y])

    roi_lines = []
    for j in range(num_agents):
        vec = agent_positions[j] - np.array([x, y])
        ro_i = np.linalg.norm(vec)
        # ローカル座標系の定義: x軸=target方向, y軸=その直交方向
        if ro_i > 0:
            e_r = vec / ro_i  # target方向の単位ベクトル（ローカルx軸）
            e_theta = np.array([-e_r[1], e_r[0]])  # ローカルy軸
            # ローカル座標系でtargetや隣接エージェントの情報を取得
            # targetの相対速度（ローカル）
            agent_velocity = (
                agent_positions[j] - animate.prev_agent_pos[j]
            ) / frame_time
            relative_velocity = agent_velocity - target_velocity
            relative_velocity_local = np.array(
                [np.dot(relative_velocity, e_r), np.dot(relative_velocity, e_theta)]
            )
            # 隣接エージェントのローカル角度
            idx_plus = (j + 1) % num_agents
            idx_minus = (j - 1) % num_agents
            vec_plus = agent_positions[idx_plus] - agent_positions[j]
            vec_minus = agent_positions[idx_minus] - agent_positions[j]
            theta_plus_local = np.arctan2(
                np.dot(vec_plus, e_theta), np.dot(vec_plus, e_r)
            )
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
            if i == 0:
                e_i_1 = 0
                e_i_2 = 0
            else:
                tau_i_1 = 0.5
                tau_i_2 = 0.5
                e_i_1 = tau_i_1 * abs(ro_i - R + eta_norm)
                e_i_2 = tau_i_2 * abs(ro_i * (omega_i_local + Omega - omega_i_local))
            e_i_1_integral[j] += e_i_1 * frame_time
            e_i_2_integral[j] += e_i_2 * frame_time
            fi = (d_i * alpha_i_local - d_i * alpha_i_minus_local) / (2 * d_i)
            zi = (
                d_i * (omega_i_plus_local - omega_i_local)
                - d_i * (omega_i_local - omega_i_minus_local)
            ) / (2 * d_i)
            u_r = (
                -ro_i * omega_i_local**2
                - eta_norm
                - e_i_1_integral[j] * np.sign(ro_i - R + eta_norm)
            )
            u_theta = (
                (omega_i_local + Omega + fi) * eta_norm
                + zi * ro_i
                + e_i_2_integral[j] * np.sign(fi + Omega - omega_i_local)
            )
            if ro_i > 1.1 * R or ro_i < 0.9 * R:
                u_r = u_r * 0.5
            else:
                u_r = u_r * 0.1
            if alpha_i_local < np.pi / 3.6 or alpha_i_local > np.pi / 2.4:
                u_theta = u_theta * 2
            else:
                u_theta = u_theta * 1
            # --- ローカル→グローバル変換 ---
            theta_global = np.arctan2(e_r[1], e_r[0])
            A = np.array(
                [
                    [np.cos(theta_global), -np.sin(theta_global)],
                    [np.sin(theta_global), np.cos(theta_global)],
                ]
            )
            u_vec_local = np.array([u_r, u_theta])
            u_vec = A @ u_vec_local
            agent_positions[j] += u_vec * frame_time

            # omega_i, omega_i_plus, omega_i_minusを[rad/sec]に変換
            omega_i_sec = omega_i_local * fps

            # u_r, u_theta, u_vecを[m/sec]に変換
            u_vec_sec = u_vec * fps

            ro_i_history[j].append(ro_i)
            eta_i_history[j].append(eta)
            omega_i_history[j].append(omega_i_sec)  # [rad/sec]で保存
            alpha_i_history[j].append(alpha_i_local)  # [rad]で保存
            u_vec_history[j].append(u_vec_sec.copy())
            # 加速度計算（2フレーム目以降)
            if len(u_vec_history[j]) > 1:
                a_vec = (u_vec_history[j][-1] - u_vec_history[j][-2]) / frame_time
                a_vec_history[j].append(np.linalg.norm(a_vec))  # 大きさ[m/s^2]
            else:
                a_vec_history[j].append(0.0)
        else:
            # ro_i<=0 の場合は値を0で記録し、位置更新しない
            roi_lines.append(f"Agent{j+1}")
            roi_lines.append(f"  ro_i={ro_i:.2f} (<=0, skipped)")
            roi_lines.append(f"  --- skipped ---")

    roi_text.set_text("\n".join(roi_lines))
    animate.prev_agent_pos = agent_positions.copy()
    animate.prev_target_pos = np.array([x, y])
    return point, agent_dots, roi_text


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
