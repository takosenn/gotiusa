import numpy as np

# --- パラメータ設定 ---
num_agents = 6                          # Agentの数6[台]
center = (0, 0)                         # targetの中心座標[m]
radius = 5                              # targetの軌道半径[m]
frames = 10000                          # アニメーションのフレーム数(小さくしすぎるとアニメーションがすぐに終わる)[frame]
xlim = (-10, 10)                        # 2Dアニメーションのx軸の範囲[m]
ylim = (-10, 10)                        # 2Dアニメーションのy軸の範囲[m]
radius_limit = 5                        # Agentの配置半径の制限(中心をtargetとして配置する)[m]
R = 2                                   # targetとAgentの理想の距離(フォーメーションの半径)[m]
d_i = 2 * np.pi / num_agents            # Agentiとその隣接Agenti+-の理想角度[rad]
frame_time = 0.02                       # 1フレームにかかる時間[s]
fps = 1 / frame_time                    # 1秒間に更新するフレーム数[frame]
omega_target = 0.12                     # target円運動の角速度0.12[rad/s]
Omega = 2                               # Agentの角速度2[rad/s]