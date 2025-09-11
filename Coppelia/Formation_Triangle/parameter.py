
import numpy as np
import threading

# --- パラメータ設定 ---
center = (0, 0)             # targetの中心座標
radius = 10                  # targetの軌道半径
frames = 10000              # アニメーションのフレーム数
xlim = (-30, 30)            # x軸の限界
ylim = (-30, 30)            # y軸の限界
radius_limit = 5            # Agentの配置半径の制限
R = [10,6,10,6,10,6]                      # targetとAgentの理想の距離
d_i = [np.pi/3 , np.pi/3 ,np.pi/3 ,np.pi/3 ,np.pi/3 ,np.pi/3 ]            # Agentiとその隣接Agenti+-の理想角度
frame_time = 0.02           # interval=50msの場合    アニメーション全体の速度を調整
fps = 1 / frame_time
omega_target = 0.12 / fps   # targetの角速度0.12
Omega = 2 / fps             # Agentの角速度2
num_agents = 6              # agentの数6