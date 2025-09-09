# animation.py内の計算を行う
# 具体的には、各Agentの速度uを計算する関数calculate_uを定義

from parameter import R, Omega, frame_time
import numpy as np

def calculate_u(
    d_i,
    ro_i,
    omega_i_local,
    omega_i_plus_local,
    omega_i_minus_local,
    alpha_i_local,
    alpha_i_minus_local,
    eta_norm,
    e_i_1_integral,
    e_i_2_integral,
    j,
    i,
):
    if i == 0:
        tau_i_1 = 0
        tau_i_2 = 0
    else:
        tau_i_1 = 0.5
        tau_i_2 = 0.5
    e_i_1 = tau_i_1 * abs(ro_i - R + eta_norm)
    e_i_2 = tau_i_2 * abs(ro_i * (omega_i_local + Omega - omega_i_local))

    e_i_1_integral[j] += e_i_1 * frame_time
    e_i_2_integral[j] += e_i_2 * frame_time
    fi = (d_i * alpha_i_local - d_i * alpha_i_minus_local) / (2 * d_i)
    zi = (
        d_i * (omega_i_plus_local - omega_i_local)
        - d_i * (omega_i_local - omega_i_minus_local)
    ) / (2 * d_i)
    u_r = (
        -ro_i * omega_i_local**2
        - eta_norm
        - e_i_1_integral[j] * np.sign(ro_i - R + eta_norm)
    )
    u_theta = (
        (omega_i_local + Omega + fi) * eta_norm
        + zi * ro_i
        + e_i_2_integral[j] * np.sign(fi + Omega - omega_i_local)
    )
    if ro_i > 1.5 * R or ro_i < 0.5 * R:
        u_r = u_r * 1
    else:
        u_r = u_r * 0.5
    if alpha_i_local < np.pi / 3.4 or alpha_i_local > np.pi / 2.6:
        u_theta = u_theta * 2
    else:
        u_theta = u_theta * 1
    return u_r, u_theta
