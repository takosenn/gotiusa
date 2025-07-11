# 様々な初期パラメータ

import numpy as np

num_agents = 6  # ドローン Agent数 6台

# --- パラメータ設定（論文 Example1 Fig.3 準拠） ---
center = (0, 0)  # targetの中心位置
radius = 20  # targetの軌道半径
frames = 10000  # アニメーションのフレーム数
xlim = (-10, 10)  # x軸の限界
ylim = (-10, 10)  # y軸の限界
R = 1  # targetとAgentの理想の距離
d_i = 2 * np.pi / num_agents  # Agentiとその隣接Agenti+-の理想角度
frame_time = 0.02  # interval=50msの場合    アニメーション全体の速度を調整
fps = 1 / frame_time
Omega = 2 / fps  # Ω=2


# ランダムウォークのパラメータ
random_walk_sigma = (
    0.2  # 1フレームごとの速度変化の標準偏差 特にこの数字にこだわりはない))
)
max_speed = 1  # targetの最大速度
# --- targetのランダムウォーク用初期化 ---
target_pos = np.array([0.0, 0.0])  # targetの初期位置
target_velocity = np.zeros(2)  # targetの初期速度
