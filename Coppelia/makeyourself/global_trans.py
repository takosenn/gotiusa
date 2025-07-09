
#速度に関するローカル座標をグローバル座標系に変換する
import numpy as np

def global_trans(theta_global,u_r,u_theta):
    A = np.array(
        [
            [np.cos(theta_global), -np.sin(theta_global)],
            [np.sin(theta_global), np.cos(theta_global)],
        ]
    )
    u_vec_local = np.array([u_r, u_theta])
    u_vec = A @ u_vec_local
    return u_vec