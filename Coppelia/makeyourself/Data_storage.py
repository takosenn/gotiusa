# Data Storagef
# データ保存

import numpy as np
from init_parameter import num_agents

# --- グラフ用データ保存リスト ---
ro_i_history: list = [[] for _ in range(num_agents)]
eta_i_history: list = [[] for _ in range(num_agents)]
omega_i_history: list = [[] for _ in range(num_agents)]
alpha_i_history: list = [[] for _ in range(num_agents)]
u_vec_history: list = [[] for _ in range(num_agents)]
a_vec_history: list = [[] for _ in range(num_agents)]
relative_velocity_history: list = [[] for _ in range(num_agents)]
# e_i_1, e_i_2の時間積分値（各エージェントごと）
e_i_1_integral = [0.0 for _ in range(num_agents)]
e_i_2_integral = [0.0 for _ in range(num_agents)]
