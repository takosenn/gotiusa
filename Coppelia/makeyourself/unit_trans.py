
#単位を変換する
from init_parameter import fps

def rad_per_sec(omega_i_local):
    omega_i_sec = omega_i_local * fps
    return omega_i_sec

def meter_per_sec(u_vec):
    u_vec_sec = u_vec * fps
    return u_vec_sec

