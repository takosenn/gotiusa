# ローカル座標系の値をグローバル座標系に変換する関数

import numpy as np
from parameter import Params

class Various:
    def __init__(self):
        self.theta = []
        for i in range(Params["num_agents"]):
            theta = i * np.pi / 3
            self.theta.append(theta)
        self.alpha = []
        for i in range(Params["num_agents"]):
            alpha = i * np.pi / 3
            self.alpha.append(alpha)
        self.alpha_minus = np.copy(self.alpha)

    def Theta(self , pos):
        self.theta = np.arctan2(pos[1],pos[0])
        if self.theta >= 0:
            self.theta = self.theta
        else:
            self.theta = self.theta + 2 * np.pi
        return self.theta

    def Angular_distance(self , theta , theta_plus , theta_minus):                          #theta_minusは(i-1)番目、theta_plusは(i+1)番目の角度(World座標系) 
        diff_plus = theta_plus - theta
        if diff_plus >= 0:
            alpha = diff_plus
        else:
            alpha = diff_plus + (2 * np.pi)
        diff_minus = theta - theta_minus
        if diff_minus >= 0:
            alpha_minus = diff_minus
        else:
            alpha_minus = diff_minus + (2 * np.pi)
        return alpha , alpha_minus
    
    def Angular_velocity(self , theta , prev_theta):                                          #prev_thetaはi番目の角度 theta = 2πの際に問題あり
        delta = theta - prev_theta
        if delta > np.pi:
            delta -= 2 * np.pi
        elif delta < -np.pi:
            delta += 2 * np.pi
        omega = delta / Params["frame_time"]
        return omega
    
    def Velocity(self , current_pos , prev_pos):
        velocity = (np.array(current_pos) - np.array(prev_pos)) / Params["frame_time"]
        return velocity
    
    def coordinate_trans(self , theta_global, u):
        A = np.array(
            [
                [np.cos(theta_global), -np.sin(theta_global)],
                [np.sin(theta_global), np.cos(theta_global)],
            ]
        )
        u_vec_local = np.array([u[0], u[1]])
        u_vec = A @ u_vec_local
        return u_vec