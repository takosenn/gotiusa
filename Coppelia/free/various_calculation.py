# ローカル座標系の値をグローバル座標系に変換する関数

import numpy as np
from parameter import frame_time , num_agents

def omega_i_local_calculation(ro_i , agent_velocity):
    # ローカル角速度
    omega_i_local = agent_velocity / ro_i
    omega_i_local = (omega_i_local + np.pi) % (2 * np.pi) - np.pi
    print(f"これはomega_i_localです{omega_i_local}")
    return omega_i_local

def coordinate_trans(theta_global, u):
    A = np.array(
        [
            [np.cos(theta_global), -np.sin(theta_global)],
            [np.sin(theta_global), np.cos(theta_global)],
        ]
    )
    u_vec_local = np.array([u[0], u[1]])
    u_vec = A @ u_vec_local
    return u_vec

def coordinate_trans_inverse(theta_global, u):
    A = np.array(
        [
            [np.cos(theta_global), -np.sin(theta_global)],
            [np.sin(theta_global), np.cos(theta_global)],
        ]
    )
    u_vec_local = np.array([u[0], u[1]])
    u_vec = np.linalg.inv(A) @ u_vec_local
    return u_vec

def Coordinate_Correction(Yaw):
    correction_x = 0.4*np.cos(Yaw)
    correction_y = 0.4*np.sin(Yaw)
    #print(f"これは関数内の位置座標補正の値です{np.array([correction_x, correction_y])}")
    return np.array([correction_x, correction_y])

def velocity_calculation(positions , prev_positions):
    velocity = (np.array(positions)- np.array(prev_positions)) / frame_time
    return velocity

class Various:
    def __init__(self):
        self.theta = []
        for i in range(num_agents):
            theta = i * np.pi / 3
            self.theta.append(theta)
        self.alpha = []
        for i in range(num_agents):
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
            self.alpha = diff_plus
        else:
            self.alpha = diff_plus + (2 * np.pi)
        diff_minus = theta - theta_minus
        if diff_minus >= 0:
            self.alpha_minus = diff_minus
        else:
            self.alpha_minus = diff_minus + (2 * np.pi)
        return self.alpha , self.alpha_minus
    
    def Angular_velocity(self , theta , prev_theta):                                          #prev_thetaはi番目の角度 theta = 2πの際に問題あり
        delta = theta - prev_theta
        if delta > np.pi:
            delta -= 2 * np.pi
        elif delta < -np.pi:
            delta += 2 * np.pi
        omega = delta #/ frame_time
        return omega
    
    def Velocity(self , current_pos , prev_pos):
        velocity = (np.array(current_pos) - np.array(prev_pos)) / frame_time
        return velocity
    


