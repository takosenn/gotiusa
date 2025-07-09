# init_parameter
# 初期値

import numpy as np

num_agents = 6  # Agentの数
center = (0, 0)  # 中心座標
radius = 20  # targetの軌道半径
frames = 10000  # フレーム数
xlim = (-10, 10)  # x軸の限界
ylim = (-10, 10)  # y軸の限界
R = 2  # targetとAgentの理想の距離
d_i = 2 * np.pi / num_agents  # Agentiとその隣接Agenti+-の理想角度
frame_time = 0.02  # interval=50msの場合    アニメーション全体の速度を調整
fps = 1 / frame_time
Omega = 2 / fps  # Ω=2
radius_limit = 6  # 配置半径（中心からの距離、固定値)

# ランダムウォークのパラメータ
random_walk_sigma = 0.5  # 1フレームごとの速度変化の標準偏差
max_speed = 1.5  # targetの最大速度（2.0→1.0に変更し追いつきやすく）
