# u_r(放射方向)とu_theta(接線方向)を計算する

import numpy as np
from parameter import Params
from DataStrage import e_i_1_integral, e_i_2_integral


def caluculate(
    i, j, alpha_i, alpha_i_minus, omega_i_plus, omega_i, omega_i_minus, ro_i, eta
):

    # --- fi, zi の計算と表示 ---
    d_i_j = Params["d_i"][j]
    fi = (d_i_j * alpha_i - d_i_j * alpha_i_minus) / (2 * d_i_j)
    zi = (d_i_j * (omega_i_plus - omega_i) - d_i_j * (omega_i - omega_i_minus)) / (
        2 * d_i_j
    )

    # e_i_1, e_i_2の初期値は0、それ以降は式で計算

    if i == 0 or i == 1 or i == 2 or i == 3 or i == 4 or i == 5:
        tau_i_1 = 0
        tau_i_2 = 0
    else:
        tau_i_1 = 2
        tau_i_2 = 2
    # Params["R"] is a per-agent list
    R_j = Params["R"][j]

    e_i_1 = tau_i_1 * np.linalg.norm(ro_i - R_j + eta)
    e_i_2 = tau_i_2 * np.linalg.norm(ro_i * (omega_i - Params["Omega"] - fi))

    # --- e_i_1, e_i_2の時間積分 ---
    e_i_1_integral[j] += e_i_1 * Params["frame_time"]
    e_i_2_integral[j] += e_i_2 * Params["frame_time"]

    # print(f"e_i_1: {e_i_1_integral[j]}")
    # print(f"e_i_2: {e_i_2_integral[j]}")
    # 論文の式(21)に従った制御プロトコルの計算

    # --- 制御プロトコルu_iの計算（時間積分したe_i_1, e_i_2を使用） ---
    # u_rが放射方向(targetに近づく離れる)の速度成分、u_thetaが接線方向の速度成分
    u_r = -ro_i * omega_i**2 - eta - 7 * np.sign(ro_i - R_j + eta)
    u_theta = (
        (omega_i + Params["Omega"] + fi) * eta
        + zi * ro_i
        + 7 * np.sign(fi + Params["Omega"] - omega_i)
    )

    # u_r(放射方向)とu_theta(接線方向)の調整
    if ro_i > 1.5 * R_j or ro_i < 0.5 * R_j:
        u_r = u_r * 1
    else:
        u_r = u_r * 1
    if alpha_i < np.pi / 3.4 or alpha_i > np.pi / 2.6:
        u_theta = u_theta * 1
    else:
        u_theta = u_theta * 1
    # print(u_theta)
    return u_r, u_theta, e_i_1_integral[j], e_i_2_integral[j], fi
