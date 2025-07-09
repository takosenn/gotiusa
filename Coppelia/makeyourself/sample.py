# targetとAgentが合体

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
import matplotlib
from matplotlib.widgets import Button
from matplotlib.lines import Line2D
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

matplotlib.rcParams["font.family"] = "MS Gothic"  # Windows標準の日本語フォントを指定

# --- CoppeliaSim への接続 ---
client = RemoteAPIClient()  # ZMQ経由でCoppeliaSimに接続するクライアントを作成
sim = client.require("sim")  # sim APIを取得

# --- ドローン（エージェント）数の設定 ---
num_agents = 6  # ドローン（エージェント）の台数

# --- ドローンのハンドル（CoppeliaSim内オブジェクト参照）を取得 ---
drone_handles = []
for i in range(num_agents):
    object_name = f"Quadcopter[{i+1}]"  # Quadcopter[1] ~ Quadcopter[6]
    drone_handle = sim.getObject(
        f"/{object_name}/target"
    )  # シーン内のオブジェクト名に合わせて修正
    drone_handles.append(drone_handle)
    print("取得: Agent")

# --- Targetオブジェクトのハンドル取得（1回だけ） ---
target_handle = sim.getObject(
    "/Quadcopter[0]/target"
)  # シーン内のtarget名に合わせて修正
print("取得: target")

# --- 各エージェントのtargetハンドルを取得 ---
agent_target_handles = [
    sim.getObject(f"/Quadcopter[{i}]/target") for i in range(1, num_agents + 1)
]

# --- VisionSensorハンドルを取得 ---
visionSensorHandles = [
    sim.getObject(f"/Quadcopter[{i}]/visionSensor") for i in range(1, num_agents + 1)
]

# --- シミュレーション開始（停止中ならスタート） ---
if sim.getSimulationState() == sim.simulation_stopped:
    sim.startSimulation()
    print("Simulation started")
    import time

    time.sleep(1.0)  # シミュレーション開始後、安定するまで少し待つ

# --- パラメータ設定（論文 Example1 Fig.3 準拠） ---
center = (0, 0)  # シーンの中心座標
radius = 20  # targetの軌道半径
frames = 10000  # アニメーションの総フレーム数
xlim = (-10, 10)  # x軸の表示範囲
ylim = (-10, 10)  # y軸の表示範囲
R = 2  # targetとAgentの理想の距離
# Agentiとその隣接Agenti+-の理想角度
# d_iは円周をエージェント数で等分した角度
# frame_timeは1フレームの時間間隔
# fpsは1秒あたりのフレーム数
# Omegaは円運動の角速度
# これらは制御やアニメーション速度に関わる

d_i = 2 * np.pi / num_agents
frame_time = 0.02  # interval=50msの場合    アニメーション全体の速度を調整
fps = 1 / frame_time
Omega = 2 / fps  # Ω=2

# --- matplotlibによる描画の初期化 ---
fig, ax = plt.subplots()  # 新しい図(fig)と座標軸(ax)を作成
ax.set_xlim(xlim)  # x軸の表示範囲を設定
ax.set_ylim(ylim)  # y軸の表示範囲を設定
ax.set_aspect("equal")  # x, y軸のスケールを等しくする（円が歪まないように）
ax.set_xlabel("x")  # x軸ラベル
ax.set_ylabel("y")  # y軸ラベル
ax.set_title("Example1")  # グラフタイトル

# --- 目標（ターゲット）の軌道を描画（初期位置のみプロット） ---
(point,) = ax.plot([0], [radius], "ro", label="Target")  # 赤丸で目標を表示

# --- エージェントの初期配置 ---
# 各エージェントを円周上に等間隔で配置
agent_positions = np.zeros((num_agents, 2))  # エージェントの座標格納用配列
radius_limit = 6  # 配置半径（中心からの距離、固定値）
for i in range(num_agents):
    theta = 2 * np.pi * i / num_agents  # 各エージェントの角度（等間隔）
    r = radius_limit  # 半径は一定（ランダム性なし）
    agent_positions[i, 0] = center[0] + r * np.cos(theta)  # x座標
    agent_positions[i, 1] = center[1] + r * np.sin(theta)  # y座標

# --- エージェントの描画 ---
agent_ids = list(range(1, num_agents + 1))  # 1~nのエージェント番号リスト
# 色分け用カラーマップ（tab10: 最大10色のカラーマップを利用）
agent_colors = plt.get_cmap("tab10")(np.linspace(0, 1, num_agents))
agent_dots = ax.scatter(
    agent_positions[:, 0], agent_positions[:, 1], c=agent_colors, label="Agents"
)  # エージェントを色分けして描画

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
ax.legend(
    handles=legend_elements, loc="center left", bbox_to_anchor=(1, 0.5)
)  # 凡例をグラフの外側（左中央）に表示

# --- 各エージェントが隣接エージェント（前後の番号）の座標を知るためのリスト作成 ---
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

# --- 各エージェントと隣接エージェント間の距離を計算（デバッグ用） ---
for i in range(num_agents):
    left_idx = (i - 1) % num_agents
    right_idx = (i + 1) % num_agents
    dist_left = np.linalg.norm(agent_positions[i] - agent_positions[left_idx])
    dist_right = np.linalg.norm(agent_positions[i] - agent_positions[right_idx])

# --- ro_i（targetと各Agentの距離）表示用テキスト（グラフ外右側に配置） ---
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

# --- ランダムウォークのパラメータ ---
random_walk_sigma = 0.5  # 1フレームごとの速度変化の標準偏差
max_speed = 1.5  # targetの最大速度（2.0→1.0に変更し追いつきやすく）


# --- アニメーション初期化関数（FuncAnimation用） ---
def init():
    point.set_data([0], [radius])  # 目標の位置を初期化
    agent_dots.set_offsets(agent_positions)  # エージェントの位置を初期化
    roi_text.set_text("")  # ROIテキストをリセット
    return point, agent_dots, roi_text  # 初期化した描画要素を返す


# --- 角度の差分をラジアンで計算する関数 ---
"""def angular_distance_rad(angle1, angle2):
    diff = abs(angle1 - angle2)
    return min(diff, 2 * np.pi - diff)"""


# --- グラフ用データ保存リスト（各エージェントごとに履歴を保存） ---
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


# --- アニメーションのメイン関数（1フレームごとに呼ばれる） ---
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
    point.set_data([x], [y])  # 目標の位置を更新
    agent_dots.set_offsets(agent_positions)  # エージェントの位置を更新
    # 色分けを毎フレーム反映
    agent_dots.set_color(agent_colors)

    # --- 前フレームのエージェント・ターゲット位置を記憶（初回のみ属性として追加） ---
    if not hasattr(
        animate, "prev_agent_pos"
    ):  # animate関数にprev_agent_pos属性がなければ
        animate.prev_agent_pos = (
            agent_positions.copy()
        )  # 現在のエージェント位置を保存（次フレームの速度計算用）
    if not hasattr(
        animate, "prev_target_pos"
    ):  # animate関数にprev_target_pos属性がなければ
        animate.prev_target_pos = np.array(
            [x, y]
        )  # 現在のターゲット位置を保存（次フレームの速度計算用）

    roi_lines = []  # 各エージェントの距離や状態を表示するテキスト用リスト
    for j in range(num_agents):
        ro_i = None  # VisionSensorでの距離計測値
        try:
            visionSensorHandle = visionSensorHandles[j]
            result = sim.getVisionSensorDepth(visionSensorHandle)
            if result is not None:
                depthBuffer, resolution = result
                depthArray = np.array(depthBuffer, dtype=np.float64)
                if len(resolution) == 2:
                    depthArray = depthArray.reshape(resolution)
                nearClip = sim.getObjectFloatParam(
                    visionSensorHandle, sim.visionfloatparam_near_clipping
                )
                farClip = sim.getObjectFloatParam(
                    visionSensorHandle, sim.visionfloatparam_far_clipping
                )
                realDepth = nearClip + (farClip - nearClip) * depthArray
                valid_mask = realDepth < (farClip - 1e-4)
                if np.any(valid_mask):
                    minDist = np.min(realDepth[valid_mask])
                    if np.isfinite(minDist):
                        ro_i = minDist
                        print(f"[Drone{j+1}] VisionSensorで検知: ro_i = {ro_i:.2f} m")
                    else:
                        print(f"[Drone{j+1}] VisionSensor: 有効な物体なし")
                else:
                    print(f"[Drone{j+1}] VisionSensor: 物体未検知")
        except Exception as e:
            print(f"[Drone{j+1}] VisionSensor error: {e}")

        if ro_i is None:
            vec = agent_positions[j] - np.array([x, y])
            ro_i = np.linalg.norm(vec)
            print(f"[Drone{j+1}] 計算値: ro_i = {ro_i:.2f} m")

        # --- ローカル座標系の定義: x軸=target方向, y軸=その直交方向 ---
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
                u_r = u_r * 1
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

    roi_text.set_text("\n".join(roi_lines))  # グラフ右側に各エージェントの距離等を表示
    animate.prev_agent_pos = (
        agent_positions.copy()
    )  # 現在のエージェント位置を保存（次フレーム用）
    animate.prev_target_pos = np.array(
        [x, y]
    )  # 現在のターゲット位置を保存（次フレーム用）
    # --- CoppeliaSim 側ドローン位置同期 ---
    for j in range(num_agents):
        pos_3d = [agent_positions[j][0], agent_positions[j][1], 2.0]
        sim.setObjectPosition(drone_handles[j], -1, pos_3d)
        # 各エージェントのtargetも同じ位置に
        sim.setObjectPosition(agent_target_handles[j], -1, pos_3d)
    # targetも1回だけ更新
    target_pos_3d = [target_pos[0], target_pos[1], 2.0]
    sim.setObjectPosition(target_handle, -1, target_pos_3d)
    return point, agent_dots  # , roi_text  # 描画要素を返す


# --- アニメーション生成 ---
ani = FuncAnimation(
    fig, animate, frames=frames, init_func=init, blit=True, interval=frame_time * 1000
)


# --- 再生/停止ボタンのクラス定義 ---
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


# --- 再生/停止ボタンの設置 ---
button_ax = plt.axes((0.85, 0.05, 0.1, 0.075))  # ボタンの位置とサイズ
button = Button(button_ax, "再生/停止")  # ボタン作成
control = AnimationControl(ani)  # コントローラ生成
button.on_clicked(control.toggle)  # ボタン押下時の動作を登録

plt.show()  # グラフ・アニメーションを表示
