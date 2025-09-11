
import numpy as np
from parameter import num_agents

#Agent同士の角距離を計算する関数
def angular_distance_rad(angle1, angle2):
    diff = abs(angle1 - angle2)
    return min(diff, 2 * np.pi - diff)


#隣接Agentの角距離、角速度を計算する関数
def neighbors_info(j,agent_positions,x,y,animate,theta_now):
        idx_plus = (j + 1) % num_agents
        idx_minus = (j - 1) % num_agents
        vec_plus = agent_positions[idx_plus] - np.array([x, y])
        vec_minus = agent_positions[idx_minus] - np.array([x, y])
        theta_plus = np.arctan2(vec_plus[1], vec_plus[0])
        theta_minus = np.arctan2(vec_minus[1], vec_minus[0])
        # 隣接エージェントの角速度
        if not hasattr(animate, "prev_theta_plus"):
            animate.prev_theta_plus = np.zeros(num_agents)
        if not hasattr(animate, "prev_theta_minus"):
            animate.prev_theta_minus = np.zeros(num_agents)
        omega_i_plus = theta_plus - animate.prev_theta_plus[j]
        omega_i_plus = (omega_i_plus + np.pi) % (2 * np.pi) - np.pi     # 角度を-πからπの範囲に正規化
        omega_i_minus = theta_minus - animate.prev_theta_minus[j]
        omega_i_minus = (omega_i_minus + np.pi) % (2 * np.pi) - np.pi   # 角度を-πからπの範囲に正規化
        animate.prev_theta_plus[j] = theta_plus
        animate.prev_theta_minus[j] = theta_minus
        # 隣接エージェントの角距離
        alpha_i = angular_distance_rad(theta_now, theta_plus)           # iとi+の角距離
        alpha_i_minus = angular_distance_rad(theta_now, theta_minus)    # iとi-の角距離
        return alpha_i, alpha_i_minus, omega_i_plus, omega_i_minus