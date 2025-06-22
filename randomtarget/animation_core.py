"""
animation_data.py
アニメーションで使う履歴データ・積分値リストの初期化を担当。
"""

import numpy as np
from config import num_agents, R, d_i, Omega, frame_time, fps

# --- グラフ用データ保存リスト ---
ro_i_history: list = [[] for _ in range(num_agents)]
eta_i_history: list = [[] for _ in range(num_agents)]
omega_i_history: list = [[] for _ in range(num_agents)]
alpha_i_history: list = [[] for _ in range(num_agents)]
u_vec_history: list = [[] for _ in range(num_agents)]
a_vec_history: list = [[] for _ in range(num_agents)]
relative_velocity_history: list = [[] for _ in range(num_agents)]
e_i_1_integral: list = [0.0 for _ in range(num_agents)]
e_i_2_integral: list = [0.0 for _ in range(num_agents)]

# --- アニメーション関数やコントロールクラスはここに分割して記述可能 ---
# animate, init, AnimationControl など
