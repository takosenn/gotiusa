# targetとAgentが合体

import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
import matplotlib
from matplotlib.widgets import Button
from matplotlib.lines import Line2D
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

matplotlib.rcParams["font.family"] = "MS Gothic"  # Windows標準の日本語フォントを指定

# CoppeliaSim 接続
client = RemoteAPIClient()
sim = client.require("sim")

# ドローン Agent数
num_agents = 6  # アニメーション・座標・色分け用（全体）
num_sensors = num_agents  # VisionSensorを持つドローン数（1~6すべて）

# drone_handles, quadcopterHandles の二重管理を解消
# ドローンハンドルはquadcopterHandlesのみを使う
quadcopterHandles = [
    sim.getObject(f"/Quadcopter[{i}]") for i in range(1, num_agents + 1)
]
# VisionSensorハンドル
visionSensorHandles = [
    sim.getObject(f"/Quadcopter[{i}]/visionSensor") for i in range(1, num_agents + 1)
]
# target_handleは中央の緑球のみ
# 各エージェントのtargetも可視化したい場合
# target_handles: Quadcopter[1]~[6]のtarget

target_handle = sim.getObject("/Quadcopter[0]/target")
target_handles = [
    sim.getObject(f"/Quadcopter[{i}]/target") for i in range(1, num_agents + 1)
]

print("取得: target")

# 各ドローンごとに履歴を持つ
prev_dist = [None] * num_sensors
prev_time = [0.0] * num_sensors


# ドローンハンドル取得
# for i in range(num_agents):
#     object_name = f"Quadcopter[{i+1}]"  # Quadcopter[1] ~ Quadcopter[4]
#     drone_handle = sim.getObject(
#         f"/{object_name}/target"
#     )  # シーン内のオブジェクト名に合わせて修正
#     drone_handles.append(drone_handle)
#     print("取得: Agent")

# Targetオブジェクト取得（ここをループ外で1回だけ！）
# target_handle = sim.getObject(
#     "/Quadcopter[0]/target"
# )  # シーン内のtarget名に合わせて修正
# print("取得: target")

# シミュレーション開始
if sim.getSimulationState() == sim.simulation_stopped:
    sim.startSimulation()
    print("Simulation started")
    import time

    time.sleep(1.0)  # 少し待つ

# --- パラメータ設定（論文 Example1 Fig.3 準拠） ---
center = (0, 0)
radius = 20  # targetの軌道半径
frames = 10000
xlim = (-10, 10)  # x軸の限界
ylim = (-10, 10)  # y軸の限界
R = 8  # targetとAgentの理想の距離
d_i = 2 * np.pi / num_agents  # Agentiとその隣接Agenti+-の理想角度
frame_time = 0.02  # interval=50msの場合    アニメーション全体の速度を調整
fps = 1 / frame_time
Omega = 2 / fps  # Ω=2


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
max_speed = 1.5  # targetの最大速度（2.0→1.0に変更し追いつきやすく）


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


# --- VisionSensorが最初に検知した物体のワールド座標を記録するリスト ---
first_detected_pos = [None for _ in range(num_agents)]

# 除外するオブジェクトID（自分自身や他のドローンなど）
exclude_object_ids = []
for i in range(1, num_agents + 1):
    try:
        exclude_object_ids.append(sim.getObject(f"/Quadcopter[{i}]"))
    except:
        pass


def animate(i):
    global target_pos, target_velocity, point, exclude_object_ids
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
    for j in range(num_sensors):
        # --- Vision Sensor で距離測定 ---
        visionSensorHandle = visionSensorHandles[j]
        ro_i = None  # VisionSensorで計測した値で上書き
        detected_world_pos = None
        try:
            nearClip = sim.getObjectFloatParam(
                visionSensorHandle, sim.visionfloatparam_near_clipping
            )
            farClip = sim.getObjectFloatParam(
                visionSensorHandle, sim.visionfloatparam_far_clipping
            )
            result = sim.getVisionSensorDepth(visionSensorHandle)
            seg_result = sim.getVisionSensorSegmentation(visionSensorHandle)
            if result is not None:
                depthBuffer, resolution = result
                try:
                    depthArray = np.array(depthBuffer, dtype=np.float64)
                except Exception:
                    depthArray = np.frombuffer(depthBuffer, dtype=np.float32)
                if len(resolution) == 2:
                    depthArray = depthArray.reshape(resolution)
                realDepth = nearClip + (farClip - nearClip) * depthArray
                mask = realDepth < (farClip - 1e-4)
                if seg_result is not None:
                    segBuffer, seg_resolution = seg_result
                    segArray = np.array(segBuffer, dtype=np.int32)
                    if len(seg_resolution) == 2:
                        segArray = segArray.reshape(seg_resolution)
                    exclude_mask = np.isin(segArray, exclude_object_ids)
                    valid_mask = np.logical_and(mask, ~exclude_mask)
                else:
                    valid_mask = mask
                if np.any(valid_mask):
                    # 最短距離ピクセルのインデックスを取得
                    min_idx = np.argmin(np.where(valid_mask, realDepth, np.inf))
                    minDist = np.min(realDepth[valid_mask])
                    if minDist < 10.0:
                        ro_i = minDist
                        # 最初に検知した物体のワールド座標を記録
                        if first_detected_pos[j] is None:
                            min_pos = np.unravel_index(min_idx, realDepth.shape)
                            vs_pos = sim.getObjectPosition(visionSensorHandle, -1)
                            vs_orient = sim.getObjectOrientation(visionSensorHandle, -1)
                            u, v = min_pos[1], min_pos[0]
                            res_x, res_y = realDepth.shape[1], realDepth.shape[0]
                            nx = (u / (res_x - 1)) * 2 - 1
                            ny = (v / (res_y - 1)) * 2 - 1
                            # カメラ座標系での方向ベクトル
                            dir_cam = np.array([nx, ny, 1.0])
                            dir_cam = dir_cam / np.linalg.norm(dir_cam)
                            # オイラー角から回転行列を自作
                            import math

                            cx, cy, cz = [math.cos(a) for a in vs_orient]
                            sx, sy, sz = [math.sin(a) for a in vs_orient]
                            # ZYX順
                            Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
                            Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
                            Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
                            R = Rz @ Ry @ Rx
                            dir_world = R @ dir_cam
                            detected_world_pos = np.array(vs_pos) + ro_i * dir_world
                            first_detected_pos[j] = detected_world_pos
                        print(
                            f"[Drone{j+1}] VisionSensor最短距離(ro_i): {minDist:.2f} m (10m以内に物体あり)"
                        )
                    else:
                        print(f"[Drone{j+1}] 10m以内に物体はありません。")
                else:
                    print(f"[Drone{j+1}] 全ピクセル背景または除外物体のみ（未検出）")
            else:
                print(f"[Drone{j+1}] Depth buffer not ready")
        except Exception as e:
            print(f"[Drone{j+1}] VisionSensor error: {e}")
        # --- VisionSensorの向きを最初に検知した物体に向け続ける ---
        if first_detected_pos[j] is not None:
            vs_pos = sim.getObjectPosition(visionSensorHandle, -1)
            target_vec = np.array(first_detected_pos[j]) - np.array(vs_pos)
            target_vec = target_vec / np.linalg.norm(target_vec)
            import math

            yaw = math.atan2(target_vec[1], target_vec[0])
            pitch = math.atan2(-target_vec[2], np.linalg.norm(target_vec[:2]))
            sim.setObjectOrientation(visionSensorHandle, -1, [pitch, 0, yaw])
        # --- ここまでVision Sensor ---
        if ro_i is None:
            # VisionSensorで取得できなかった場合は従来の計算値
            vec = agent_positions[j] - np.array([x, y])
            ro_i = np.linalg.norm(vec)
        else:
            vec = agent_positions[j] - np.array([x, y])
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
            if ro_i > 1.5 * R or ro_i < 0.5 * R:
                u_r = u_r * 0.5
            else:
                u_r = u_r * 0.2
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
    # --- CoppeliaSim 側ドローン位置同期もquadcopterHandlesを使う
    for j in range(num_agents):
        pos_3d = [agent_positions[j][0], agent_positions[j][1], 2.0]  # 高さ2.0m
        sim.setObjectPosition(quadcopterHandles[j], -1, pos_3d)
        # 各エージェントのtargetも可視化（理想位置をそのまま表示）
        sim.setObjectPosition(target_handles[j], -1, pos_3d)
    # targetも毎フレーム更新（親をワールド直下に明示的に設定してから位置を更新）
    sim.setObjectParent(target_handle, -1, True)  # 親をワールド直下に
    target_pos_3d = [target_pos[0], target_pos[1], 2.0]
    sim.setObjectPosition(target_handle, -1, target_pos_3d)
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
