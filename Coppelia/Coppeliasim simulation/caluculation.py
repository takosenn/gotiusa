
#u_r(放射方向)とu_theta(接線方向)を計算する

import numpy as np
from parameter import R, Omega,frame_time,d_i
from DataStrage import e_i_1_integral, e_i_2_integral

def caluculate(i,j,alpha_i,alpha_i_minus,omega_i_plus,omega_i,omega_i_minus,ro_i,eta_norm):
    # --- fi, zi の計算と表示 ---
    fi = (d_i * alpha_i - d_i * alpha_i_minus) / (2 * d_i)
    zi = (d_i * (omega_i_plus - omega_i) - d_i * (omega_i - omega_i_minus)) / (2 * d_i)

    # e_i_1, e_i_2の初期値は0、それ以降は式で計算
    if i == 0:
        tau_i_1 = 0
        tau_i_2 = 0
    else:
        tau_i_1 = 0.5
        tau_i_2 = 0.5
    e_i_1 = tau_i_1 * abs(ro_i - R + eta_norm)
    e_i_2 = tau_i_2 * abs(ro_i * (omega_i + Omega - omega_i))
    
    # --- e_i_1, e_i_2の時間積分 ---
    e_i_1_integral[j] += e_i_1 * frame_time
    e_i_2_integral[j] += e_i_2 * frame_time

    # --- 制御プロトコルu_iの計算（時間積分したe_i_1, e_i_2を使用） ---
    #u_rが放射方向(targetに近づく離れる)の速度成分、u_thetaが接線方向の速度成分
    u_r = -ro_i * omega_i**2 - eta_norm - e_i_1_integral[j] * np.sign(ro_i - R + eta_norm)
    u_theta = ((omega_i + Omega + fi) * eta_norm + zi * ro_i + e_i_2_integral[j] * np.sign(fi + Omega - omega_i))

    #u_r(放射方向)とu_theta(接線方向)の調整
    if ro_i > 1.5 * R or ro_i < 0.5 * R:
        u_r = u_r * 0.5
    else:
        u_r = u_r * 0.2
    if alpha_i < np.pi / 3.4 or alpha_i > np.pi / 2.6:
        u_theta = u_theta * 2
    else:
        u_theta = u_theta * 1
    return u_r,u_theta
