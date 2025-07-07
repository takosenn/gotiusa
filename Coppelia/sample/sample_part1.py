# sample_part1.py
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

# ドローン Agent数 4台
num_agents = 6
drone_handles = []

# ドローンハンドル取得
for i in range(num_agents):
    object_name = f"Quadcopter[{i+1}]"  # Quadcopter[1] ~ Quadcopter[4]
    drone_handle = sim.getObject(
        f"/{object_name}/target"
    )  # シーン内のオブジェクト名に合わせて修正
    drone_handles.append(drone_handle)
    print("取得: Agent")

# Targetオブジェクト取得（ここをループ外で1回だけ！）
target_handle = sim.getObject(
    "/Quadcopter[0]/target"
)  # シーン内のtarget名に合わせて修正
print("取得: target")

# 各エージェントのtargetハンドルを取得
agent_target_handles = [
    sim.getObject(f"/Quadcopter[{i}]/target") for i in range(1, num_agents + 1)
]

# VisionSensorハンドルを取得
visionSensorHandles = [
    sim.getObject(f"/Quadcopter[{i}]/visionSensor") for i in range(1, num_agents + 1)
]

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
R = 2  # targetとAgentの理想の距離
d_i = 2 * np.pi / num_agents  # Agentiとその隣接Agenti+-の理想角度
frame_time = 0.02  # interval=50msの場合    アニメーション全体の速度を調整
fps = 1 / frame_time
Omega = 2 / fps  # Ω=2
