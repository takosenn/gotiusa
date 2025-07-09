
#プロトコルに値を代入

import numpy as np
from init_parameter import d_i,R,Omega
from Data_storage import e_i_1_integral,e_i_2_integral

def protcol(i,j,eta_norm,ro_i,omega_i_local,omega_i_plus_local,omega_i_minus_local,alpha_i_local,alpha_i_minus_local,e_r):
    fi = (d_i * alpha_i_local - d_i * alpha_i_minus_local) / (2 * d_i)
    zi = (d_i * (omega_i_plus_local - omega_i_local)- d_i * (omega_i_local - omega_i_minus_local)) / (2 * d_i)
    u_r = (-ro_i * omega_i_local**2- eta_norm- e_i_1_integral[j] * np.sign(ro_i - R + eta_norm))
    u_theta = ((omega_i_local + Omega + fi) * eta_norm+ zi * ro_i+ e_i_2_integral[j] * np.sign(fi + Omega - omega_i_local))
    if ro_i > 1.1 * R or ro_i < 0.9 * R:
        u_r = u_r * 0.6
    else:
        u_r = u_r * 0.2
    if alpha_i_local < np.pi / 3.6 or alpha_i_local > np.pi / 2.4:
        u_theta = u_theta * 2
    else:
        u_theta = u_theta * 1
    return u_r,u_theta