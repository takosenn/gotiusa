# ローカル座標系の値をグローバル座標系に変換する関数

import numpy as np

def omega_i_local_calculation(ro_i , agent_velocity):
    #theta_now_local = 0.0  # 自分自身から見たtarget方向は常に0
    # ローカル角速度
    omega_i_local = agent_velocity[1] / ro_i
    print(f"これはomega_i_localです{omega_i_local}")
    omega_i_local = (omega_i_local + np.pi) % (2 * np.pi) - np.pi
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
