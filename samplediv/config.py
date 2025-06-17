# config.py
# パラメータ設定（論文 Example1 Fig.3 準拠）
import numpy as np
center = (0, 0)
radius = 20                 #targetの軌道半径
frames = 5000
xlim = (-30, 30)            #x軸の限界
ylim = (-30, 30)            #y軸の限界
R=4                         #targetとAgentの理想の距離
d_i=np.pi/3     #Agentiとその隣接Agenti+-の理想角度
l1=7                        #プロトコル(12)の制御パラメータ
l2=7                        #プロトコル(12)の制御パラメータ
frame_time = 0.05           # interval=50msの場合
fps = 1 / frame_time
omega_target = 0.12 /fps    # targetの角速度0.12
Omega = 2 / fps             # 各Agentの理想角速度Ω=2
num_agents = 6
