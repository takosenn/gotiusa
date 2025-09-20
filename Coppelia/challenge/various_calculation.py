# ローカル座標系の値をグローバル座標系に変換する関数

import numpy as np

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

def Coordinate_Correction(Yaw):
    correction_x = np.cos(Yaw)
    correction_y = np.sin(Yaw)
    #print(f"これは関数内の位置座標補正の値です{np.array([correction_x, correction_y])}")
    return np.array([correction_x, correction_y])