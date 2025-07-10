import numpy as np


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
