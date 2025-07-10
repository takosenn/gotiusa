import numpy as np

# ドローン Agent数 6台
num_agents = 6

# --- パラメータ設定（論文 Example1 Fig.3 準拠） ---
center = (0, 0)
radius = 20  # targetの軌道半径
frames = 10000
xlim = (-10, 10)  # x軸の限界
ylim = (-10, 10)  # y軸の限界
R = 4  # targetとAgentの理想の距離
d_i = 2 * np.pi / num_agents  # Agentiとその隣接Agenti+-の理想角度
frame_time = 0.02  # interval=50msの場合    アニメーション全体の速度を調整
fps = 1 / frame_time
Omega = 2 / fps  # Ω=2
# ランダムウォークのパラメータ
random_walk_sigma = 0.2  # 1フレームごとの速度変化の標準偏差
max_speed = 1  # targetの最大速度
