
import numpy as np

# --- パラメータ設定 ---
center = (0, 0)             # targetの中心座標
radius = 5                  # targetの軌道半径
frames = 10000              # アニメーションのフレーム数(小さくしすぎるとアニメーションがすぐに終わる)
xlim = (-10, 10)            # 2Dアニメーションのx軸の範囲
ylim = (-10, 10)            # 2Dアニメーションのy軸の範囲
radius_limit = 5            # Agentの配置半径の制限(中心をtargetとして配置する)
R = 1                       # targetとAgentの理想の距離(フォーメーションの半径)
d_i = np.pi / 3             # Agentiとその隣接Agenti+-の理想角度
frame_time = 0.5           # interval=50msの場合    アニメーション全体の速度を調整
fps = 1 / frame_time
omega_target = 0.12 / fps   # target円運動の角速度0.12[rad/s]
Omega = 2 / fps             # Agentの角速度2[rad/s]
num_agents = 6              # Agentの数6