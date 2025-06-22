"""
config_parameters.py
全体で使う定数・パラメータ（物理定数、初期値、描画範囲など）を定義。
"""

import numpy as np

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

random_walk_sigma = 0.5  # 1フレームごとの速度変化の標準偏差
max_speed = 2.0  # targetの最大速度
