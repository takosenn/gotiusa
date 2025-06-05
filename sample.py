import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
import matplotlib
from matplotlib.widgets import Button
from matplotlib.lines import Line2D

matplotlib.rcParams['font.family'] = 'MS Gothic'  # Windows標準の日本語フォントを指定

# --- パラメータ設定（論文 Example1 Fig.3 準拠） ---
center = (0, 0)
radius = 20                 #targetの軌道半径
frames = 5000
xlim = (-30, 30)            #x軸の限界
ylim = (-30, 30)            #y軸の限界
R=4                         #targetとAgentの理想の距離
d_i=np.pi/3                 #Agentiとその隣接Agenti+-の理想角度
l1=7                        #プロトコル(12)の制御パラメータ
l2=7                        #プロトコル(12)の制御パラメータ
frame_time = 0.05           # interval=50msの場合
fps = 1 / frame_time
omega_target = 0.12 /fps        # targetの角速度0.12
omega = 0.12 / fps               # 各Agentの理想角速度0.12
Omega = 2 / fps               # Ω=2

# --- 初期化 ---
fig, ax = plt.subplots()
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.set_aspect("equal")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Example1")

# 目標の軌道
point, = ax.plot([0], [radius], "ro", label="Target")
circle = Circle(center, radius, fill=False, linestyle='dashed', color='blue', label='軌道')
ax.add_patch(circle)

# --- エージェントの初期角度を昇順で配置（0 <= alpha_1 < ... < alpha_6 < 2π） ---
num_agents = 6
angles = np.sort(np.random.uniform(0, 2 * np.pi, num_agents))  # 昇順
agent_positions = np.column_stack([
    center[0] + radius * np.cos(angles),
    center[1] + radius * np.sin(angles)
])
agent_ids = list(range(1, num_agents+1))  # 1~6のエージェント番号
# 色分け用カラーマップ（tab10を利用）
agent_colors = plt.get_cmap('tab10').colors[:num_agents]
agent_dots = ax.scatter(agent_positions[:,0], agent_positions[:,1], c=agent_colors, label='Agents')
# --- エージェント番号と色の凡例を追加 ---
legend_elements = [Line2D([0], [0], marker='o', color='w', label=f'Agent {i+1}',
                          markerfacecolor=agent_colors[i], markersize=10)
                   for i in range(num_agents)]
ax.legend(handles=legend_elements, loc="center left", bbox_to_anchor=(1, 0.5))

# 各エージェントが隣接エージェント（前後の番号）の座標を知る
neighbor_indices = [((i-1)%num_agents, (i+1)%num_agents) for i in range(num_agents)]
agent_neighbors = []
for i in range(num_agents):
    left_idx = (i-1) % num_agents
    right_idx = (i+1) % num_agents
    left_pos = agent_positions[left_idx]
    right_pos = agent_positions[right_idx]
    agent_neighbors.append((left_pos, right_pos))
# agent_neighbors[i] = (左隣の座標, 右隣の座標)

for i in range(num_agents):
    left_idx = (i-1) % num_agents
    right_idx = (i+1) % num_agents
    dist_left = np.linalg.norm(agent_positions[i] - agent_positions[left_idx])
    dist_right = np.linalg.norm(agent_positions[i] - agent_positions[right_idx])



# --- アニメーション関数 ---
# ro_i（targetと各Agentの距離）表示用テキスト（グラフ外右側に配置）
roi_text = ax.text(0.05, 0.10, '', transform=ax.transAxes, ha='left', va='center', fontsize=8, color='black')

def init():
    point.set_data([0], [radius])
    agent_dots.set_offsets(agent_positions)
    roi_text.set_text('')
    return point, agent_dots, roi_text

def angular_distance_rad(angle1, angle2):
    diff = abs(angle1 - angle2)
    return min(diff, 2 * np.pi - diff)

# --- グラフ用データ保存リスト ---
ro_i_history = [[] for _ in range(num_agents)]
eta_i_history = [[] for _ in range(num_agents)]
omega_i_history = [[] for _ in range(num_agents)]
alpha_i_history = [[] for _ in range(num_agents)]
u_vec_history = [[] for _ in range(num_agents)]
a_vec_history = [[] for _ in range(num_agents)]

def animate(i):
    theta = omega_target * i
    x = center[0] + radius * np.sin(theta)
    y = center[1] + radius * np.cos(theta)
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
        theta_now = np.arctan2(vec[1], vec[0])
        if not hasattr(animate, "prev_theta"):
            animate.prev_theta = np.zeros(num_agents)
        omega_i = theta_now - animate.prev_theta[j]
        omega_i = (omega_i + np.pi) % (2 * np.pi) - np.pi
        ro_i = np.linalg.norm(vec)
        animate.prev_theta[j] = theta_now
        # ro_i>0 の場合のみ処理を行う
        if ro_i > 0:
            # etaの式をR-ro_iに変更
            eta = R - ro_i
            eta_norm = abs(eta)
            # 隣接エージェントとの角距離・角速度
            idx_plus = (j+1) % num_agents
            idx_minus = (j-1) % num_agents
            vec_plus = agent_positions[idx_plus] - np.array([x, y])
            vec_minus = agent_positions[idx_minus] - np.array([x, y])
            theta_plus = np.arctan2(vec_plus[1], vec_plus[0])
            theta_minus = np.arctan2(vec_minus[1], vec_minus[0])
            # 隣接エージェントの角速度
            if not hasattr(animate, "prev_theta_plus"):
                animate.prev_theta_plus = np.zeros(num_agents)
            if not hasattr(animate, "prev_theta_minus"):
                animate.prev_theta_minus = np.zeros(num_agents)
            omega_i_plus = theta_plus - animate.prev_theta_plus[j]
            omega_i_plus = (omega_i_plus + np.pi) % (2 * np.pi) - np.pi
            omega_i_minus = theta_minus - animate.prev_theta_minus[j]
            omega_i_minus = (omega_i_minus + np.pi) % (2 * np.pi) - np.pi
            animate.prev_theta_plus[j] = theta_plus
            animate.prev_theta_minus[j] = theta_minus
            alpha_i = angular_distance_rad(theta_now, theta_plus)
            alpha_i_minus = angular_distance_rad(theta_now, theta_minus)

            

            # --- fi, zi の計算と表示 ---
            fi = (d_i * alpha_i - d_i * alpha_i_minus) / (2 * d_i)
            zi = (d_i * (omega_i_plus - omega_i) - d_i * (omega_i - omega_i_minus)) / (2 * d_i)

            # --- 制御プロトコルu_iの計算と位置更新 ---
            # 放射方向・接線方向の単位ベクトル
            e_r = vec / ro_i
            e_theta = np.array([-e_r[1], e_r[0]])
            # u_iの各成分
            u_r = -ro_i*omega_i**2  - eta_norm - l1 * np.sign(ro_i - R + eta_norm)
            u_theta = (omega_i + Omega + fi) * eta_norm + zi * ro_i + l2 * np.sign(fi + Omega - omega_i)
            # 合成速度ベクトル
            u_vec = u_r * e_r + u_theta * e_theta
            # 位置更新（タイムステップdt=0.05）
            agent_positions[j] += u_vec * 0.05

            # omega_i, omega_i_plus, omega_i_minusを[rad/sec]に変換
            omega_i_sec = omega_i * fps
            omega_i_plus_sec = omega_i_plus * fps
            omega_i_minus_sec = omega_i_minus * fps
            # u_r, u_theta, u_vecを[m/sec]に変換
            u_r_sec = u_r * fps
            u_theta_sec = u_theta * fps
            u_vec_sec = u_vec * fps
            omega_target_sec = omega_target * fps
            omega_sec = omega * fps
            Omega_sec = Omega * fps

            roi_lines.append(f"Agent{j+1}")
            roi_lines.append(f"  ro_i={ro_i:.2f}, |eta|={eta_norm:.3f}")
            roi_lines.append(f"  omega_i={omega_i_sec:.3f} [rad/sec]")
            roi_lines.append(f"  alpha(-隣)={alpha_i_minus:.3f} [rad], omega_i-={omega_i_minus_sec:.3f} [rad/sec]")
            roi_lines.append(f"  alpha(+隣)={alpha_i:.3f} [rad], omega_i+={omega_i_plus_sec:.3f} [rad/sec]")
            roi_lines.append(f"  fi={fi:.3f}, zi={zi:.3f}")
            roi_lines.append(f"  u_r={u_r_sec:.3f} [m/sec], u_theta={u_theta_sec:.3f} [m/sec]")
            roi_lines.append(f"  u_vec=({u_vec_sec[0]:.3f}, {u_vec_sec[1]:.3f}) [m/sec]")
            roi_lines.append(f"  omega_target={omega_target:.3f} [rad/frame], omega={omega:.3f} [rad/frame], Omega={Omega:.3f} [rad/frame]")
            ro_i_history[j].append(ro_i)
            eta_i_history[j].append(eta)
            omega_i_history[j].append(omega_i_sec)  # [rad/sec]で保存
            alpha_i_history[j].append(alpha_i)   # [rad]で保存
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
            ro_i_history[j].append(ro_i)
            eta_i_history[j].append(0.0)
            omega_i_history[j].append(0.0)
            alpha_i_history[j].append(0.0)
            u_vec_history[j].append(np.zeros(2))
            a_vec_history[j].append(0.0)
    roi_text.set_text('\n'.join(roi_lines))
    animate.prev_agent_pos = agent_positions.copy()
    animate.prev_target_pos = np.array([x, y])
    return point, agent_dots, roi_text

ani = FuncAnimation(fig, animate, frames=frames, init_func=init, blit=True, interval=50)
# plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))  # ←重複防止のため削除

# --- アニメーション終了後にro_i, eta_iのグラフを表示 ---
# （グラフ表示機能を削除）

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

button_ax = plt.axes([0.85, 0.05, 0.1, 0.075])
button = Button(button_ax, '再生/停止')
control = AnimationControl(ani)
button.on_clicked(control.toggle)

plt.show()

